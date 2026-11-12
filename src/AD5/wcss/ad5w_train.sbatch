#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --cpus-per-task=8
#SBATCH --mem=120G
#SBATCH --no-requeue
#SBATCH --time=12:00:00
#SBATCH --job-name=ad5w
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/logs/ad5w-%x-%A_%a.out
# Retrains of released methods with the authors' code (AD5) on WCSS (prereg amendment 4). One task = one seed
# (array task id = seed). Submit with --gres=gpu:hopper:<N>,storage:local:150G and --export=ALL,ARM=B|L|X[,EPOCHS=..].
#   B = MADation ViT-B/16 LoRA, L = MADation ViT-L/14 LoRA: the authors' train.sh flags, global batch 256 = N GPUs x
#       (256 / N) per GPU (authors: 8 x 32), 40 epochs, checkpoint of epoch 40 only (the code saves nothing else).
#   X = MixFaceNet-MAD, SMDD main.py patched (AD5_LAST=1: no test list, all 100 epochs, weights after every epoch).
# Everything runs in $TMPDIR (local NVMe): code, wheels and crop pack untarred there, Python 3.9 venv built there from
# the shipped wheels (MADation README: Python 3.9), one result tar + .sha256 back to Lustre. No placeholder: the job
# carries its whole workload and exits non-zero on any failure.
set -euo pipefail
L=${AD5_L:-/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5}   # AD5_L / AD5_PYTHON: rented-machine runs (src/AD5/rented)
PYBIN=${AD5_PYTHON:-python3}
SEED=${SLURM_ARRAY_TASK_ID:?array task = seed}; ARM=${ARM:?ARM=B|L|X}
case $ARM in B|L) T=madation_${ARM}_s${SEED} ;; X) T=mixfacenet_X_s${SEED} ;; *) echo "bad ARM"; exit 2 ;; esac
[ -n "${SMOKE:-}" ] && T=${T}_smoke
[ -f $L/results/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
: "${TMPDIR:?local scratch required}"; S=$TMPDIR/ad5; mkdir -p $S/out
keep() { mkdir -p $L/logs/keep/$T; cp "$@" $L/logs/keep/$T/ 2>/dev/null || true; }
trap 'echo "TERM $(date +%T)"; keep $S/out/*.log $S/out/*.csv; exit 1' TERM
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; $PYBIN --version; date
for p in ad5w_code ad5w_wheels39 smdd_train_cropped; do
  ( cd $L/packs && sha256sum -c $p.tar.sha256 ) || { echo "HASH MISMATCH $p"; exit 3; }
done
mkdir -p $S/code $S/wheels $S/crop
tar -xf $L/packs/ad5w_code.tar -C $S/code; tar -xf $L/packs/ad5w_wheels39.tar -C $S/wheels
tar -xf $L/packs/smdd_train_cropped.tar -C $S/crop
t0=$(date +%s)
$PYBIN -m venv $S/env; PY=$S/env/bin/python
$PY -m pip install -q --no-index --find-links $S/wheels setuptools==69.5.1 wheel==0.43.0
$PY -m pip install -q --no-index --find-links $S/wheels --no-build-isolation -r $S/code/src/AD5/env/madation_requirements.txt
$PY -m pip freeze > $S/out/pip_freeze.txt; echo "env built in $(( $(date +%s) - t0 )) s"
$PY -I -c "import sys, torch, torchvision, cv2, clip, pandas; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0)); assert sys.version_info[:2] == (3, 9)"
sed "s#^CROP_ROOT#$S/crop#" $S/crop/smdd_train_cropped_rel.csv > $S/train.csv
[ -n "${SMOKE:-}" ] && { awk 'NR==1 || (NR-2) % 12 == 0' $S/train.csv > $S/t.csv; mv $S/t.csv $S/train.csv; }
echo "train rows $(( $(wc -l < $S/train.csv) - 1 ))"
NG=${AD5_NG:-$($PY -I -c 'import torch; print(torch.cuda.device_count())')}   # respects CUDA_VISIBLE_DEVICES
( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $S/out/gpumem.csv; sleep 10; done ) >/dev/null 2>&1 &
MP=$!; t0=$(date +%s); rc=0
C=$S/code
if [ $ARM = X ]; then
  ( cd $C/build/smdd_src && AD5_LAST=1 AD5_SEED=$SEED AD5_EPOCH_DIR=$S/out/epochs $PY -I $C/src/AD5/checks/run_with_site.py \
      $C/build/smdd_src $C/build/smdd_src/main.py --train_csv_path $S/train.csv --model_path $S/out/mixfacenet_SMDD.pth \
      --is_train True --is_test False --output_dir $S/out --max_epoch ${EPOCHS:-100} --batch_size 16 ) > $S/out/train_stdout.log 2>&1 || rc=$?
  OUTF="mixfacenet_SMDD.pth train_info.log"
else
  BPG=$(( 256 / NG )); [ $(( BPG * NG )) = 256 ] || { echo "256 not divisible by $NG"; exit 2; }
  if [ $ARM = L ]; then A=(--backbone_size="ViT-L/14" --lora_dropout=0.2 --lora_r=2 --lora_a=8); CS=$C/weights/clip_vitl14_openai.bin
  else A=(--backbone_size="ViT-B/16" --lora_dropout=0.4 --lora_r=2 --lora_a=4); CS=$C/weights/clip_vitb16_openai.bin; fi
  EX=(); [ -n "${SMOKE:-}" ] && EX=(--num_epoch=3 --save_every=3 --log_every=25)
  ( cd $C/build/madation_src/src && OMP_NUM_THREADS=4 AD5_SEED=$SEED AD5_TRAIN_CSV=$S/train.csv AD5_NO_TEST=1 \
      AD5_OUT=$S/run AD5_CLIP_SD=$CS $PY -I -m torch.distributed.launch --nproc_per_node=$NG --nnodes=1 --node_rank=0 \
      --master_addr=localhost --master_port=$(( 12000 + SEED )) config.py --debug=True --dataset_name="MADTrain" \
      --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 "${A[@]}" --batch_size=$BPG "${EX[@]}" ) \
      > $S/out/train_stdout.log 2>&1 || rc=$?
  D=$(dirname "$(ls $S/run/last_trainings/*/*/*/*/training.log 2>/dev/null | head -1)")
  cp -r $D/training.log $D/tensorboard $S/out/ 2>/dev/null || true
  E=$([ -n "${SMOKE:-}" ] && echo 3 || echo 40)
  cp $D/${E}_backbone.pth $D/${E}_header.pth $S/out/ 2>/dev/null || rc=9
  OUTF="${E}_backbone.pth ${E}_header.pth training.log"
fi
kill $MP || true
SEC=$(( $(date +%s) - t0 ))
echo "rc $rc seconds $SEC gpus $NG peak_MiB $(awk -F', ' '{if ($2+0>m) m=$2+0} END {print m+0}' $S/out/gpumem.csv)"
grep -h "Speed" $S/out/training.log 2>/dev/null | tail -3 || true
if [ $rc != 0 ]; then tail -40 $S/out/train_stdout.log; keep $S/out/train_stdout.log $S/out/training.log $S/out/gpumem.csv; exit 1; fi
printf '{"task":"%s","arm":"%s","seed":%s,"job":"%s_%s","host":"%s","gpus":%s,"gpu":"%s","seconds":%s,"train_csv_sha256":"%s"}\n' \
  $T $ARM $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED $(hostname) $NG "$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" $SEC \
  $(sha256sum $S/train.csv | cut -c1-64) > $S/out/job.json
( cd $S/out && sha256sum $OUTF > SHA256SUMS )
tail -c 30000 $S/out/train_stdout.log > $S/out/train_stdout_tail.log; rm -f $S/out/train_stdout.log
tar -cf $TMPDIR/$T.tar -C $S/out .
( cd $TMPDIR && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $L/results; cp $TMPDIR/$T.tar $L/results/; cp $TMPDIR/$T.tar.sha256 $L/results/
cat $L/results/$T.tar.sha256; echo DONE $T; date

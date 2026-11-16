#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --cpus-per-task=16
#SBATCH --mem=250G
#SBATCH --no-requeue
#SBATCH --nice=40
#SBATCH --time=04:00:00
#SBATCH --job-name=ad6w3
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6/logs/ad6w-%x-%A_%a.out
# AD6 matched-recipe retrains (prereg: experiments/AD6_matched-recipe-comparator-retrains/prereg.md). Registered
# recipe transfer: authors' code + AD5 patches (UNCHANGED), training data = full-Sb budget list 1,600,000 rows
# (6,250 updates x global batch 256), num_epoch=1, checkpoint of epoch 1 only. One task = one seed (array id).
# Submit with --gres=gpu:hopper:<N>,storage:local:150G --array=401-405 --export=ALL,ARM=B|L,L=<lustre dir>.
#   B = MADation ViT-B/16 LoRA, L = MADation ViT-L/14 LoRA (authors' train.sh flags; per-GPU batch = 256/NG).
# Code/wheels: ad6w_code.tar (ad5w_code.tar + the registered AD6 epoch-1 save patch, 2 lines in
# build/madation_src/src/utils/logging.py; patch file src/AD6/ad6_save_epoch1.patch), ad5w_wheels39.tar (AD5 wheels,
# sha-verified), data pack ad6_sb_pack.tar (sha-verified), ad6w_wheels39_v3.tar (V3 ADD-ON: torch 2.1.2+cu121 stack,
# env-only amendment - operator-authorized option A, 16 Nov 2026; authors' code and recipe UNCHANGED; see
# madation_requirements_v3.txt in the add-on pack and AD6_WHEELS_V3_AMENDMENT_20261116 in experiments).
set -euo pipefail
L=${AD6_L:?set L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6}
PYBIN=${AD6_PYTHON:-python3}
SEED=${SLURM_ARRAY_TASK_ID:?array task = seed}; ARM=${ARM:?ARM=B|L}
case $ARM in B) T=madation_B_v3sbr_s${SEED} ;; L) T=madation_L_v3sbr_s${SEED} ;; X) T=mixfacenet_X_sbr_s${SEED} ;; *) echo "bad ARM" >&2; exit 2 ;; esac
[ -f $L/results/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
: "${TMPDIR:?local scratch required}"; S=$TMPDIR/ad6; mkdir -p $S/out
keep() { mkdir -p $L/logs/keep/$T; cp "$@" $L/logs/keep/$T/ 2>/dev/null || true; }
trap 'echo "TERM $(date +%T)"; keep $S/out/*.log $S/out/*.csv; exit 1' TERM
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; date
for p in ad6w_code ad5w_wheels39 ad6_sb_pack ad6w_wheels39_v3; do
  ( cd $L/packs && sha256sum -c $p.tar.sha256 ) || { echo "HASH MISMATCH $p" >&2; exit 3; }
done
mkdir -p $S/code $S/wheels $S/data
tar -xf $L/packs/ad6w_code.tar -C $S/code
tar -xf $L/packs/ad5w_wheels39.tar -C $S/wheels
tar -xf $L/packs/ad6w_wheels39_v3.tar -C $S/wheels
tar -xf $L/packs/ad6_sb_pack.tar -C $S/data
t0=$(date +%s)
$PYBIN -m venv $S/env; PY=$S/env/bin/python
$PY -m pip install -q --no-index --find-links $S/wheels setuptools==69.5.1 wheel==0.43.0
$PY -m pip install -q --no-index --find-links $S/wheels --no-build-isolation -r $S/wheels/madation_requirements_v3.txt
$PY -m pip freeze > $S/out/pip_freeze.txt; echo "env built in $(( $(date +%s) - t0 )) s"
$PY -I -c "import sys, torch, torchvision, cv2, clip, pandas; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0)); assert sys.version_info[:2] == (3, 9)"
TRAIN=$S/data/train_Sb_6250x256.csv
sed -i "s#^CROP_ROOT#$S/data#" $TRAIN
[ -f $S/data/manifests/train_Sb.csv ]
printf 'rows %s\n' "$(( $(wc -l < $TRAIN) - 1 ))"
if [ $ARM = X ]; then
  ( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $S/out/gpumem.csv 2>/dev/null || true; sleep 10; done ) >/dev/null 2>&1 &
  MPX=$!; rc=0
  ( cd $S/code/build/smdd_src && AD5_LAST=1 AD5_SEED=$SEED AD5_EPOCH_DIR=$S/out/epochs \
      $PY -I $S/code/src/AD5/checks/run_with_site.py $S/code/build/smdd_src $S/code/build/smdd_src/main.py \
      --train_csv_path $TRAIN --model_path $S/out/mixfacenet_SMDD.pth --is_train True --is_test False \
      --output_dir $S/out --max_epoch 1 --batch_size 256 ) > $S/out/train_stdout.log 2>&1 || rc=$?
  kill $MPX || true; SEC=$(( $(date +%s) - t0 )); [ $rc = 0 ] && [ -s $S/out/mixfacenet_SMDD.pth ] \
    || { tail -40 $S/out/train_stdout.log; keep $S/out/train_stdout.log; exit 1; }
  printf '{"task":"%s","arm":"%s_sbr","seed":%s,"job":"%s_%s","host":"%s","gpus":%s,"per_gpu_batch":256,"global_batch":256,"updates_target":6250,"seconds":%s,"train_csv_sha256":"%s"}\n' \
    $T $ARM $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED $(hostname) 1 $SEC "$(sha256sum $TRAIN | cut -c1-64)" > $S/out/job.json
  ( cd $S/out && sha256sum mixfacenet_SMDD.pth > SHA256SUMS )
  tar -cf $TMPDIR/$T.tar -C $S/out .
  ( cd $TMPDIR && sha256sum $T.tar > $T.tar.sha256 )
  mkdir -p $L/results; cp $TMPDIR/$T.tar $L/results/; cp $TMPDIR/$T.tar.sha256 $L/results/
  cat $L/results/$T.tar.sha256; echo DONE $T; date; exit 0
fi
NG=$(nvidia-smi -L | wc -l); BPG=$(( 256 / NG )); [ $(( BPG * NG )) = 256 ] || { echo "256 not divisible by $NG" >&2; exit 2; }
case $ARM in
  L) A=(--backbone_size="ViT-L/14" --lora_dropout=0.2 --lora_r=2 --lora_a=8); CS=$S/code/weights/clip_vitl14_openai.bin ;;
  B) A=(--backbone_size="ViT-B/16" --lora_dropout=0.4 --lora_r=2 --lora_a=4); CS=$S/code/weights/clip_vitb16_openai.bin ;;
esac
( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $S/out/gpumem.csv 2>/dev/null || true; sleep 10; done ) >/dev/null 2>&1 &
MP=$!; t0=$(date +%s); rc=0
C=$S/code
( cd $C/build/madation_src/src && OMP_NUM_THREADS=4 AD5_SEED=$SEED AD5_TRAIN_CSV=$TRAIN AD5_NO_TEST=1 \
    AD5_OUT=$S/run AD5_CLIP_SD=$CS $PY -I -m torch.distributed.launch --nproc_per_node=$NG --nnodes=1 --node_rank=0 \
    --master_addr=localhost --master_port=$(( 13000 + SEED )) config.py --debug=True --dataset_name="MADTrain" \
    --training_type="MAD_training" --num_epoch=1 --save_every=1 --lr_model=1e-5 --lr_header=1e-4 "${A[@]}" \
    --batch_size=$BPG ) > $S/out/train_stdout.log 2>&1 || rc=$?
D=$(dirname "$(ls $S/run/last_trainings/*/*/*/*/training.log 2>/dev/null | head -1)")
cp -r $D/training.log $D/tensorboard $S/out/ 2>/dev/null || true
cp $D/1_backbone.pth $D/1_header.pth $S/out/ 2>/dev/null || rc=9
kill $MP || true
SEC=$(( $(date +%s) - t0 ))
echo "rc $rc seconds $SEC gpus $NG per_gpu_batch $BPG peak_MiB $(awk -F', ' '{if ($2+0>m) m=$2+0} END {print m+0}' $S/out/gpumem.csv)"
grep -h "Speed\|Loss" $S/out/training.log 2>/dev/null | tail -3 || true
if [ $rc != 0 ]; then tail -40 $S/out/train_stdout.log; keep $S/out/train_stdout.log $S/out/training.log $S/out/gpumem.csv; exit 1; fi
printf '{"task":"%s","arm":"%s_sbr","seed":%s,"job":"%s_%s","host":"%s","gpus":%s,"per_gpu_batch":%s,"global_batch":256,"updates_target":6250,"seconds":%s,"train_csv_sha256":"%s"}\n' \
  $T $ARM $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED $(hostname) $NG $BPG $SEC "$(sha256sum $TRAIN | cut -c1-64)" > $S/out/job.json
( cd $S/out && sha256sum 1_backbone.pth 1_header.pth training.log > SHA256SUMS )
tar -cf $TMPDIR/$T.tar -C $S/out .
( cd $TMPDIR && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $L/results; cp $TMPDIR/$T.tar $L/results/; cp $TMPDIR/$T.tar.sha256 $L/results/
cat $L/results/$T.tar.sha256; echo DONE $T; date

#!/bin/bash -l
# AD6 matched-recipe retrains on ATHENA (A100-40G, plgrid-gpu-a100) — Athena adaptation of
# src/AD6/wcss/ad6w_v3.sbatch (v3.1, md5 2d91c81592b446f4214bc20a8debfb54). Recipe/code UNCHANGED;
# only site plumbing differs: account plgmultivision-gpu-a100, partition plgrid-gpu-a100, $MEMFS work
# area (packs read from the project folder on lustre, L=/net/pr2/projects/plgrid/plggrestoration/smad-next/AD6),
# PYBIN=/usr/bin/python3.9 (Athena modules have no 3.9; /usr/bin/python3.9 is 3.9.25; v3 wheels are cp39),
# result tars written to $L/results (one tar per task), live train log to $L/logs/keep/$T/ (v3.1 pattern).
# Env: v3 wheels torch 2.1.2+cu121 cp39 (see madation_requirements_v3.txt, AD6_WHEELS_V3_AMENDMENT_20261116).
# Submit: sbatch --array=401-405 --export=ALL,ARM=B,AD6_L=<L> [gres/cpus/mem in header]
# multiplicities: NG GPUs seen on the node; per-GPU batch = 256/NG (4 GPUs -> 64 = WCSS H100 layout; the
# recipe fixes the GLOBAL batch 256 and num_epoch=1 -> 6250 updates, exactly as registered on WCSS).
# All 4 packs sha-verified far-side 16 Nov 2026 (v3 = 189968df...07d anchor match) before this script existed.
set -euo pipefail
set -x
trap 'echo "ERR at line $LINENO: cmd=[$BASH_COMMAND]"' ERR
L=${AD6_L:-/net/pr2/projects/plgrid/plggrestoration/smad-next/AD6}
PYBIN=${AD6_PYTHON:-/usr/bin/python3.9}
SEED=${SLURM_ARRAY_TASK_ID:?array task = seed}; ARM=${ARM:?ARM=B|L|X}
case $ARM in B) T=madation_B_v3sbr_s${SEED} ;; L) T=madation_L_v3sbr_s${SEED} ;; X) T=mixfacenet_X_sbr_s${SEED} ;; *) echo "bad ARM" >&2; exit 2 ;; esac
[ -f $L/results/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
: "${MEMFS:?memfs work area required}"; S=$MEMFS/ad6; rm -rf $S; mkdir -p $S/out $L/logs/keep/$T
keep() { mkdir -p $L/logs/keep/$T; cp "$@" $L/logs/keep/$T/ 2>/dev/null || true; }
trap 'echo "TERM $(date +%T)"; keep $S/out/*.log $S/out/*.csv; exit 1' TERM
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; date
# addendum 16 Nov ~20:45Z: original ad6_sb_pack.tar (2b5b2880) is DGX-native — ALL data members are
# symlinks into /mnt/t7 (only 2 real files). On Athena those targets do not exist: smoke #2 (3556490)
# died at the manifests guard ([ -f ] ERR, line 42) and would die in the loader on the 339k lad_* rows.
# ATHENA FIX (data-source twin, recipe/CSV content UNCHANGED): dereferenced rebuild of the same pack
# (same members, symlinks -> real files, built on the DGX with tar -h from the sha-2b5b2880 pack):
# ad6_sb_pack_athena_v1.tar (1,918,525,440 B, sha baa5abe39fb5daf7f6b5bf41a911ebbb7d08f768994125f3cb99208c7c0f6d5a),
# upload streamed in one transfer, sidecar .sha256 in the packs dir. csb pack csv = byte-identical CROP_ROOT rows.
for p in ad6w_code ad5w_wheels39 ad6_sb_pack_athena_v1 ad6w_wheels39_v3; do
  ( cd $L/packs && sha256sum -c $p.tar.sha256 ) || { echo "HASH MISMATCH $p" >&2; exit 3; }
done
mkdir -p $S/code $S/wheels $S/data
tar -xf $L/packs/ad6w_code.tar -C $S/code
tar -xf $L/packs/ad5w_wheels39.tar -C $S/wheels
tar -xf $L/packs/ad6w_wheels39_v3.tar -C $S/wheels
tar -xf $L/packs/ad6_sb_pack_athena_v1.tar -C $S/data
echo "MEMFS usage after extraction: $(du -sm $S 2>/dev/null | cut -f1) MB, memfs:"; df -h $MEMFS 2>/dev/null | tail -1
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
if [ "$ARM" = X ]; then
  rc=0
  ( cd $S/code/build/smdd_src && AD5_LAST=1 AD5_SEED=$SEED AD5_EPOCH_DIR=$S/out/epochs \
      $PY -I $S/code/src/AD5/checks/run_with_site.py $S/code/build/smdd_src $S/code/build/smdd_src/main.py \
      --train_csv_path $TRAIN --model_path $S/out/mixfacenet_SMDD.pth --is_train True --is_test False \
      --output_dir $S/out --max_epoch 1 --batch_size 256 ) > $L/logs/keep/$T/train_stdout.log 2>&1 || rc=$?
  [ $rc = 0 ] && [ -s $S/out/mixfacenet_SMDD.pth ] || { tail -40 $L/logs/keep/$T/train_stdout.log; exit 1; }
  SEC=$(( $(date +%s) - t0 ))
  printf '{"task":"%s","arm":"%s_sbr","seed":%s,"job":"%s_%s","host":"%s","gpus":1,"per_gpu_batch":256,"global_batch":256,"updates_target":6250,"seconds":%s,"train_csv_sha256":"%s"}\n' \
    $T $ARM $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED $(hostname) $SEC "$(sha256sum $TRAIN | cut -c1-64)" > $S/out/job.json
  ( cd $S/out && sha256sum mixfacenet_SMDD.pth > SHA256SUMS )
  tar -cf $L/results/$T.tar -C $S/out .
  ( cd $L/results && sha256sum $T.tar > $T.tar.sha256 )
  cat $L/results/$T.tar.sha256; echo DONE $T; date; exit 0
fi
# addendum 16 Nov ~20:30Z: partition has <2 free A100s right now; smoke uses 1 GPU with AD6_BPG=64
# (per-GPU batch of the registered WCSS H100 layout; smoke only, recorded in MONITOR). Production keeps
# --gres=gpu:4 -> BPG=64, global batch 256. AD6_BPG is a deliberate smoke override, never used in production.
NG=$(nvidia-smi -L | wc -l); BPG=${AD6_BPG:-$(( 256 / NG ))}; [ $(( BPG * NG )) = 256 ] || echo "SMOKE BPG OVERRIDE: gpus $NG BPG $BPG (global $(( BPG * NG )) != 256)" >&2
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
    --batch_size=$BPG ) > $L/logs/keep/$T/train_stdout.log 2>&1 || rc=$?
D=$(dirname "$(ls $S/run/last_trainings/*/*/*/*/training.log 2>/dev/null | head -1)")
cp -r $D/training.log $D/tensorboard $S/out/ 2>/dev/null || true
cp $D/1_backbone.pth $D/1_header.pth $S/out/ 2>/dev/null || rc=9
kill $MP || true
SEC=$(( $(date +%s) - t0 ))
echo "rc $rc seconds $SEC gpus $NG per_gpu_batch $BPG peak_MiB $(awk -F', ' '{if ($2+0>m) m=$2+0} END {print m+0}' $S/out/gpumem.csv)"
grep -h "Speed\|Loss" $S/out/training.log 2>/dev/null | tail -3 || true
if [ $rc != 0 ]; then tail -40 $L/logs/keep/$T/train_stdout.log; keep $S/out/gpumem.csv; exit 1; fi
printf '{"task":"%s","arm":"%s_sbr","seed":%s,"job":"%s_%s","host":"%s","gpus":%s,"per_gpu_batch":%s,"global_batch":256,"updates_target":6250,"seconds":%s,"train_csv_sha256":"%s"}\n' \
  $T $ARM $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED $(hostname) $NG $BPG $SEC "$(sha256sum $TRAIN | cut -c1-64)" > $S/out/job.json
( cd $S/out && sha256sum 1_backbone.pth 1_header.pth training.log > SHA256SUMS )
tar -cf $L/results/$T.tar -C $S/out .
( cd $L/results && sha256sum $T.tar > $T.tar.sha256 )
cat $L/results/$T.tar.sha256; echo DONE $T; date

#!/bin/bash
# AD6 MixFaceNet X_sbr x5 seeds on GB10 (prereg commit 3c799ff). Sequential; idempotent per seed; no rm.
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
C=/home/narolski/ad6_stage/ad6w_code
TRAIN=/home/narolski/ad6_stage/ad6w_code/data/train_Sb_6250x256_gd10.csv
R=/home/narolski/ad6_stage/ad6_results
mkdir -p $R
for SEED in 401 402 403 404 405; do
  T=mixfacenet_X_sbr_s$SEED
  [ -f $R/$T/.tar_written ] && { echo "SKIP $T"; continue; }
  S=$R/$T; mkdir -p $S/out
  echo "=== $T start $(date -u +%H:%M:%SZ)"
  t0=$(date +%s); rc=0
  ( cd $C/build/smdd_src && AD5_LAST=1 AD5_SEED=$SEED AD5_EPOCH_DIR=$S/out/epochs \
      $PY -I $C/src/AD5/checks/run_with_site.py $C/build/smdd_src $C/build/smdd_src/main.py \
      --train_csv_path $TRAIN --model_path $S/out/mixfacenet_SMDD.pth --is_train True --is_test False \
      --output_dir $S/out --max_epoch 1 --batch_size 256 ) > $S/out/train_stdout.log 2>&1 || rc=$?
  SEC=$(( $(date +%s) - t0 ))
  echo "=== $T rc $rc seconds $SEC"
  if [ $rc = 0 ] && [ -s $S/out/mixfacenet_SMDD.pth ]; then
    ( cd $S/out && sha256sum mixfacenet_SMDD.pth > SHA256SUMS )
    touch $S/.tar_written
  else
    tail -30 $S/out/train_stdout.log
  fi
done
echo "AD6_GB10_X_DONE $(date -u +%FT%TZ)"

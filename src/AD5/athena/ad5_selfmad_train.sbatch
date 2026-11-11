#!/bin/bash -l
#SBATCH -J ad5-selfmad
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=16:00:00
#SBATCH -C memfs
#SBATCH --array=401-405
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-selfmad-%A_%a.out
# Retrains of released methods (AD5), production: one SelfMAD retrain per array task (task id = seed) with the
# authors' train__.py (patched: -v last = no validation, no test sets, the epoch-100 state is saved) and the shipped
# train_config.json values (hrnet_w18, batch 32, 100 epochs, lr 5e-4, SMDD). --time is set from the smoke speed.
# v2 (pre-run review findings 2, 7): AD5_EXPECT_N=24982 asserts the training-set size; the model state dict every
# 5 epochs goes to results/AD5/selfmad_S_s<seed>_epochs/ (descriptive only; epoch 100 is the registered reading);
# failed runs keep their log. Output: results/AD5/selfmad_S_s<seed>.tar (+ .sha256). Idempotent.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code_v3/src/AD5/athena/ad5_common.sh
SEED=$SLURM_ARRAY_TASK_ID; T=selfmad_S_s${SEED}
[ -f $RS/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code_v3; SRC=$C/build/selfmad_src; RUN=$C/src/AD5/checks/run_with_site.py; PY=$EN/selfmad/bin/python
[ -f $EN/selfmad/AD5_ENV_OK ] || { echo "env missing"; exit 1; }
export HF_HUB_CACHE=$C/hf_cache
S=$SCRATCH_LOCAL/$T; mkdir -p $S/SMDD $S/out
untar_checked $PK/smdd_train_raw.tar $S/raw SMDD_release_train/os25k_bf_t; mv $S/raw/SMDD_release_train/os25k_bf_t $S/SMDD/os25k_bf_t; rm -rf $S/raw
untar_checked $PK/selfmad_landmarks.tar $S
( cd $PK && sha256sum -c selfmad_labels.tar.gz.sha256 ) && tar -xzf $PK/selfmad_labels.tar.gz -C $S
M=$S/out/gpumem.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
( cd $SRC && AD5_SEED=$SEED AD5_EXPECT_N=24982 AD5_EPOCH_DIR=$RS/${T}_epochs $PY -I $RUN $SRC $SRC/train__.py -n ad5_s$SEED -m hrnet_w18 -b 32 -e ${EPOCHS:-100} -lr 5e-4 \
    -t SMDD -v last -SMDD_path $S/SMDD -s $S/run ) > $S/out/train_stdout.log 2>&1 || rc=$?
kill $MP || true
SEC=$(( $(date +%s) - t0 )); echo "rc $rc seconds $SEC peak_MiB $(peak_mib $M)"
W=$(ls $S/run/*/weights/epoch_${EPOCHS:-100}.tar 2>/dev/null || true)
[ $rc = 0 ] && [ -n "$W" ] || { tail -c 3000 $S/out/train_stdout.log; keep_log $S/out/train_stdout.log $M; exit 1; }
D=$(dirname $(dirname $W)); cp $W $S/out/; cp $D/config.txt $D/logs/losses.logs $S/out/
grep "^AD5 training images" $S/out/train_stdout.log || true
tail -c 20000 $S/out/train_stdout.log > $S/out/train_stdout_tail.log; rm $S/out/train_stdout.log
cp $EN/selfmad/pip_freeze.txt $S/out/
printf '{"task":"%s","seed":%s,"job":"%s_%s","host":"%s","seconds":%s}\n' $T $SEED $SLURM_ARRAY_JOB_ID \
  $SLURM_ARRAY_TASK_ID $(hostname) $SEC > $S/out/job.json
( cd $S/out && sha256sum $(basename $W) losses.logs > SHA256SUMS )
tar -cf $SCRATCH_LOCAL/$T.tar -C $S/out .
( cd $SCRATCH_LOCAL && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $RS; cp $SCRATCH_LOCAL/$T.tar $RS/; cp $SCRATCH_LOCAL/$T.tar.sha256 $RS/
cat $RS/$T.tar.sha256; echo DONE $T; date

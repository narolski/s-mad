#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --no-requeue
#SBATCH --time=40:00:00
#SBATCH --job-name=ad5w-selfmad
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/logs/ad5w-%x-%A_%a.out
# Retrains of released methods with the authors' code (AD5) on WCSS: SelfMAD, one seed per array task (task id = seed).
# Submit with --gres=gpu:hopper:1,storage:local:150G. The same run as the Athena job (athena/ad5_selfmad_train.sbatch,
# code_v5): authors' train__.py patched (-v last, AD5_EXPECT_N=24982, model every 5 epochs), train_config.json values
# (hrnet_w18, batch 32, 100 epochs, lr 5e-4, SMDD). Python 3.10 as the authors' env.yml: a portable CPython 3.10.14
# (python-build-standalone 20240814, sha256 88dee5e4..., checked against the published hash) with the Athena SelfMAD
# wheel house (wheels_selfmad.tar, cp310). All IO in $TMPDIR; one result tar + .sha256 back to Lustre.
# TEST=1: first 160 renders, 5 epochs (passes the save paths).
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
SEED=${SLURM_ARRAY_TASK_ID:?seed}; T=selfmad_S_s${SEED}; [ -n "${TEST:-}" ] && T=${T}_test
[ -f $L/results/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
: "${TMPDIR:?local scratch}"; S=$TMPDIR/ad5s; mkdir -p $S/out $S/run $S/SMDD
keep() { mkdir -p $L/logs/keep/$T; cp "$@" $L/logs/keep/$T/ 2>/dev/null || true; }
trap 'echo "TERM $(date +%T)"; keep $S/out/*.log $S/out/*.csv; exit 1' TERM
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; date
for p in ad5w_selfmad_code.tar ad5w_selfmad_data.tar ad5w_py310.tar.gz selfmad_labels.tar.gz wheels_selfmad.tar; do
  ( cd $L/packs && sha256sum -c $p.sha256 ) || { echo "HASH MISMATCH $p"; exit 3; }
done
mkdir -p $S/py $S/code $S/wheels
tar -xzf $L/packs/ad5w_py310.tar.gz -C $S/py; tar -xf $L/packs/ad5w_selfmad_code.tar -C $S/code
tar -xf $L/packs/wheels_selfmad.tar -C $S/wheels
tar -xf $L/packs/ad5w_selfmad_data.tar -C $S/SMDD          # -> os25k_bf_t/, SMDD_landmarks/os25k_bf_t/
mv $S/SMDD/SMDD_landmarks $S/SMDD_landmarks; tar -xzf $L/packs/selfmad_labels.tar.gz -C $S   # -> SMDD_labels/os25k_bf_t/
t0=$(date +%s); $S/py/python/bin/python3 -m venv $S/env; PY=$S/env/bin/python
$PY -m pip install -q --no-index --find-links $S/wheels setuptools wheel
$PY -m pip install -q --no-index --find-links $S/wheels --no-build-isolation -r $S/code/src/AD5/env/selfmad_requirements.txt
$PY -m pip freeze > $S/out/pip_freeze.txt; echo "env built in $(( $(date +%s) - t0 )) s"
$PY -I -c "import sys, torch, timm, albumentations, efficientnet_pytorch; print(sys.version.split()[0], torch.__version__, timm.__version__, torch.cuda.get_device_name(0))"
export HF_HUB_CACHE=$S/code/hf_cache HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
DATA=$S/SMDD; N=24982; EP=${EPOCHS:-100}; ED=$S/out/epochs
if [ -n "${TEST:-}" ]; then
  U=$S/sub; mkdir -p $U/SMDD/os25k_bf_t $U/SMDD_landmarks/os25k_bf_t $U/SMDD_labels/os25k_bf_t
  for f in $(ls $S/SMDD/os25k_bf_t | sort | head -160); do b=${f%.png}
    ln -s $S/SMDD/os25k_bf_t/$f $U/SMDD/os25k_bf_t/$f; ln -s $S/SMDD_labels/os25k_bf_t/$b.npy $U/SMDD_labels/os25k_bf_t/$b.npy
    [ -f $S/SMDD_landmarks/os25k_bf_t/$b.npy ] && ln -s $S/SMDD_landmarks/os25k_bf_t/$b.npy $U/SMDD_landmarks/os25k_bf_t/$b.npy; done
  DATA=$U/SMDD; N=$(ls $U/SMDD_landmarks/os25k_bf_t | wc -l); EP=5
fi
( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $S/out/gpumem.csv; sleep 20; done ) >/dev/null 2>&1 &
MP=$!; t0=$(date +%s); rc=0; SRC=$S/code/build/selfmad_src
( cd $SRC && AD5_SEED=$SEED AD5_EXPECT_N=$N AD5_EPOCH_DIR=$ED $PY -I $S/code/src/AD5/checks/run_with_site.py $SRC $SRC/train__.py \
    -n ad5_s$SEED -m hrnet_w18 -b 32 -e $EP -lr 5e-4 -t SMDD -v last -SMDD_path $DATA -s $S/run ) > $S/out/train_stdout.log 2>&1 || rc=$?
kill $MP || true; SEC=$(( $(date +%s) - t0 ))
W=$(ls $S/run/*/weights/epoch_$EP.tar 2>/dev/null || true)
echo "rc $rc seconds $SEC"
[ $rc = 0 ] && [ -n "$W" ] || { tail -c 3000 $S/out/train_stdout.log; keep $S/out/train_stdout.log $S/out/gpumem.csv; exit 1; }
Dd=$(dirname $(dirname $W)); cp $W $S/out/; cp $Dd/config.txt $Dd/logs/losses.logs $S/out/
grep "^AD5 training images" $S/out/train_stdout.log || true
tail -c 30000 $S/out/train_stdout.log > $S/out/train_stdout_tail.log; rm $S/out/train_stdout.log
printf '{"task":"%s","seed":%s,"job":"%s_%s","host":"%s","gpu":"%s","seconds":%s}\n' $T $SEED ${SLURM_ARRAY_JOB_ID:-0} $SEED \
  $(hostname) "$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" $SEC > $S/out/job.json
( cd $S/out && sha256sum $(basename $W) losses.logs > SHA256SUMS )
tar -cf $TMPDIR/$T.tar -C $S/out .; ( cd $TMPDIR && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $L/results; cp $TMPDIR/$T.tar $TMPDIR/$T.tar.sha256 $L/results/
cat $L/results/$T.tar.sha256; echo DONE $T; date

#!/bin/bash -l
#SBATCH -J ad5-mixfacenet
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH -C localfs
#SBATCH --array=401-405
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-mixfacenet-%A_%a.out
# Retrains of released methods (AD5), production: one MixFaceNet-MAD retrain per array task (task id = seed) with the
# SMDD repository's main.py (patched: AD5_LAST=1 = no test list, no early stopping, the epoch-100 weights are saved).
# Flags as the official README / defaults: batch 16, up to 100 epochs (here all 100), Adam 1e-4.
# Output: results/AD5/mixfacenet_X_s<seed>.tar (+ .sha256). Idempotent.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
SEED=$SLURM_ARRAY_TASK_ID; T=mixfacenet_X_s${SEED}
[ -f $RS/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code; PY=$EN/madation/bin/python
[ -f $EN/madation/AD5_ENV_OK ] || { echo "env missing"; exit 1; }
S=$SCRATCH_LOCAL/$T; mkdir -p $S/out
untar_checked $PK/smdd_train_cropped.tar $S/crop
sed "s#^CROP_ROOT#$S/crop#" $S/crop/smdd_train_cropped_rel.csv > $S/train.csv
M=$S/out/gpumem.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
( cd $C/build/smdd_src && AD5_LAST=1 AD5_SEED=$SEED $PY -I $C/src/AD5/checks/run_with_site.py $C/build/smdd_src \
    $C/build/smdd_src/main.py --train_csv_path $S/train.csv --model_path $S/out/mixfacenet_SMDD.pth --is_train True \
    --is_test False --output_dir $S/out --max_epoch ${MAX_EPOCH:-100} --batch_size 16 ) > $S/out/train_stdout.log 2>&1 || rc=$?
kill $MP || true
SEC=$(( $(date +%s) - t0 )); echo "rc $rc seconds $SEC peak_MiB $(peak_mib $M)"
[ $rc = 0 ] && [ -s $S/out/mixfacenet_SMDD.pth ] || { tail -c 3000 $S/out/train_stdout.log; exit 1; }
cp $EN/madation/pip_freeze.txt $S/out/
printf '{"task":"%s","seed":%s,"job":"%s_%s","host":"%s","seconds":%s,"train_csv_sha256":"%s"}\n' $T $SEED \
  $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID $(hostname) $SEC $(sha256sum $S/train.csv | cut -c1-64) > $S/out/job.json
tail -c 20000 $S/out/train_stdout.log > $S/out/train_stdout_tail.log; rm $S/out/train_stdout.log
( cd $S/out && sha256sum mixfacenet_SMDD.pth train_info.log > SHA256SUMS )
tar -cf $SCRATCH_LOCAL/$T.tar -C $S/out .
( cd $SCRATCH_LOCAL && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $RS; cp $SCRATCH_LOCAL/$T.tar $RS/; cp $SCRATCH_LOCAL/$T.tar.sha256 $RS/
cat $RS/$T.tar.sha256; echo DONE $T; date

#!/bin/bash -l
#SBATCH -J ad5-madation
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 64
#SBATCH --mem=480G
#SBATCH --gres=gpu:8
#SBATCH --time=02:00:00
#SBATCH -C localfs
#SBATCH --array=401-405
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-madation-%x-%A_%a.out
# Retrains of released methods (AD5), production: one MADation retrain per array task (task id = seed), with the
# authors' train.sh flags on 8 GPUs (torch.distributed.launch, batch 32 per GPU, 40 epochs, checkpoint of epoch 40 only).
# Submit with  sbatch --export=ALL,ARM=L|B|F [--time=...] ad5_madation_train.sbatch
#   L = ViT-L/14 LoRA, B = ViT-B/16 LoRA, F = ViT-L/14 frozen encoder (MAD_training_only_header), as prereg.md.
# Output: results/AD5/madation_<ARM>_s<seed>.tar (+ .sha256): 40_backbone.pth, 40_header.pth, training.log,
# tensorboard/, train_stdout.log, gpumem.csv, pip_freeze.txt, job.json. Idempotent: an existing result tar is not redone.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
SEED=$SLURM_ARRAY_TASK_ID; ARM=${ARM:?ARM=L|B|F}
T=madation_${ARM}_s${SEED}
[ -f $RS/$T.tar.sha256 ] && { echo "$T done already"; exit 0; }
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; date
C=$PK/code; PY=$EN/madation/bin/python
[ -f $EN/madation/AD5_ENV_OK ] || { echo "env missing"; exit 1; }
case $ARM in
  L) A=(--backbone_size="ViT-L/14" --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 --lora_dropout=0.2 --lora_r=2 --lora_a=8); CS=$C/weights/clip_vitl14_openai.bin ;;
  B) A=(--backbone_size="ViT-B/16" --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 --lora_dropout=0.4 --lora_r=2 --lora_a=4); CS=$C/weights/clip_vitb16_openai.bin ;;
  F) A=(--backbone_size="ViT-L/14" --training_type="MAD_training_only_header" --lr_model=0 --lr_header=1e-2); CS=$C/weights/clip_vitl14_openai.bin ;;
  *) echo "bad ARM $ARM"; exit 1 ;;
esac
NG=$(nvidia-smi -L | wc -l)
S=$SCRATCH_LOCAL/$T; mkdir -p $S/out
untar_checked $PK/smdd_train_cropped.tar $S/crop
sed "s#^CROP_ROOT#$S/crop#" $S/crop/smdd_train_cropped_rel.csv > $S/train.csv
echo "train rows $(( $(wc -l < $S/train.csv) - 1 )), GPUs $NG"
M=$S/out/gpumem.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
( cd $C/build/madation_src/src && OMP_NUM_THREADS=8 AD5_SEED=$SEED AD5_TRAIN_CSV=$S/train.csv AD5_NO_TEST=1 \
    AD5_OUT=$S/run AD5_CLIP_SD=$CS $PY -I -m torch.distributed.launch --nproc_per_node=$NG --nnodes=1 --node_rank=0 \
    --master_addr=localhost --master_port=12355 config.py --debug=True --dataset_name="MADTrain" "${A[@]}" \
    --batch_size=32 ) > $S/out/train_stdout.log 2>&1 || rc=$?
kill $MP || true
SEC=$(( $(date +%s) - t0 ))
D=$(dirname $(ls $S/run/last_trainings/*/*/*/*/training.log))
echo "rc $rc seconds $SEC peak_MiB $(peak_mib $M) dir $D"
grep -h "Speed" $D/training.log | tail -3 || true
[ $rc = 0 ] && [ -s $D/40_backbone.pth ] && [ -s $D/40_header.pth ] || { tail -50 $S/out/train_stdout.log; exit 1; }
cp -r $D/40_backbone.pth $D/40_header.pth $D/training.log $D/tensorboard $S/out/
cp $EN/madation/pip_freeze.txt $S/out/
printf '{"task":"%s","arm":"%s","seed":%s,"job":"%s_%s","host":"%s","gpus":%s,"seconds":%s,"train_csv_sha256":"%s","crop_tar_sha256":"%s"}\n' \
  $T $ARM $SEED $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID $(hostname) $NG $SEC $(sha256sum $S/train.csv | cut -c1-64) \
  $(cut -c1-64 $PK/smdd_train_cropped.tar.sha256) > $S/out/job.json
( cd $S/out && sha256sum 40_backbone.pth 40_header.pth training.log > SHA256SUMS )
tar -cf $SCRATCH_LOCAL/$T.tar -C $S/out .
( cd $SCRATCH_LOCAL && sha256sum $T.tar > $T.tar.sha256 )
mkdir -p $RS; cp $SCRATCH_LOCAL/$T.tar $RS/; cp $SCRATCH_LOCAL/$T.tar.sha256 $RS/
cat $RS/$T.tar.sha256; echo DONE $T; date

#!/bin/bash -l
#SBATCH -J ad5-smokeB
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=2
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH --gres=gpu:2
#SBATCH --time=00:15:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-smokeB-%j.out
# Retrains of released methods (AD5), smoke job B (2 GPUs x 15 min = at most 0.5 GPU-hours): the patched MADation code
# with the authors' flags under torch.distributed.launch on 2 GPUs (batch 32 per GPU, as the authors), on every 12th
# image of the cropped SMDD list for 3 epochs (about 160 steps), ViT-L/14 then ViT-B/16; then MixFaceNet-MAD for
# 1 epoch on the same subset. Measures seconds per step and peak GPU memory; checks that the checkpoints are written.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code; PY=$EN/madation/bin/python
[ -f $EN/madation/AD5_ENV_OK ] || { echo "env missing: run smoke A first"; exit 1; }
S=$SCRATCH_LOCAL/ad5B; mkdir -p $S
untar_checked $PK/smdd_train_cropped.tar $S/crop
sed "s#^CROP_ROOT#$S/crop#" $S/crop/smdd_train_cropped_rel.csv > $S/train_full.csv
awk 'NR==1 || (NR-2) % 12 == 0' $S/train_full.csv > $S/train_sub.csv; echo "subset rows $(( $(wc -l < $S/train_sub.csv) - 1 ))"
export OMP_NUM_THREADS=8 AD5_SEED=401 AD5_TRAIN_CSV=$S/train_sub.csv AD5_NO_TEST=1
for arm in L B; do
  if [ $arm = L ]; then BB="ViT-L/14"; X="--lora_dropout=0.2 --lora_r=2 --lora_a=8"; CS=$C/weights/clip_vitl14_openai.bin
  else BB="ViT-B/16"; X="--lora_dropout=0.4 --lora_r=2 --lora_a=4"; CS=$C/weights/clip_vitb16_openai.bin; fi
  M=$S/gpumem_$arm.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
  ( cd $C/build/madation_src/src && AD5_OUT=$S/out_$arm AD5_CLIP_SD=$CS $PY -I -m torch.distributed.launch \
      --nproc_per_node=2 --nnodes=1 --node_rank=0 --master_addr=localhost --master_port=12355 config.py --debug=True \
      --backbone_size="$BB" --dataset_name="MADTrain" --training_type="MAD_training" --lr_model=1e-5 --lr_header=1e-4 \
      $X --batch_size=32 --num_epoch=3 --save_every=3 --log_every=25 ) > $S/train_$arm.log 2>&1 || rc=$?
  kill $MP || true
  echo "ARM $arm rc $rc seconds $(( $(date +%s) - t0 )) peak_MiB $(peak_mib $M)"
  grep -h "Speed\|Total Step\|Trainset" $S/out_$arm/last_trainings/*/*/*/*/training.log | tail -6 || true
  ls -la $S/out_$arm/last_trainings/*/*/*/*/ || tail -30 $S/train_$arm.log
  [ $rc = 0 ] && ls $S/out_$arm/last_trainings/*/*/*/*/3_backbone.pth || echo "ARM $arm FAILED"
done
# MixFaceNet-MAD: 1 epoch on the subset, 1 GPU (the official script uses cuda:0)
M=$S/gpumem_X.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
( cd $C/build/smdd_src && AD5_LAST=1 AD5_SEED=401 CUDA_VISIBLE_DEVICES=0 $PY -I $C/src/AD5/checks/run_with_site.py \
    $C/build/smdd_src $C/build/smdd_src/main.py --train_csv_path $S/train_sub.csv --model_path $S/out_X/mixfacenet_SMDD.pth --is_train True --is_test False \
    --output_dir $S/out_X --max_epoch 1 --batch_size 16 ) > $S/train_X.log 2>&1 || rc=$?
kill $MP || true
echo "ARM X rc $rc seconds $(( $(date +%s) - t0 )) peak_MiB $(peak_mib $M)"; tail -c 600 $S/train_X.log; ls -la $S/out_X || true
mkdir -p $RS/smokeB; cp $S/train_*.log $S/gpumem_*.csv $RS/smokeB/
for arm in L B; do cp $S/out_$arm/last_trainings/*/*/*/*/training.log $RS/smokeB/training_$arm.log || true; done
echo SMOKE_B_DONE; date

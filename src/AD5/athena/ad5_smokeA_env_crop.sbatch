#!/bin/bash -l
#SBATCH -J ad5-smokeA
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=40G
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-smokeA-%j.out
# Retrains of released methods (AD5), smoke job A (1 GPU, at most 0.5 GPU-hours):
#  1. builds the MADation / MixFaceNet-MAD environment envs/AD5/madation from the shipped wheels (no index);
#  2. runs the SMDD repository's image_preprocess.py UNCHANGED (MTCNN on cuda:0, as the authors) on the 40,000 SMDD
#     training images, writes the training list (train.csv order) and packs the crops as packs/AD5/smdd_train_cropped.tar.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; python3 --version; date
C=$PK/code
build_env madation $C/src/AD5/env/madation_requirements.txt $PK/wheels_madation.tar
PY=$EN/madation/bin/python
$PY -I -c "import torch, torchvision, cv2, facenet_pytorch, clip, easydict, pandas, sklearn; print('torch', torch.__version__, torch.version.cuda, 'cudnn', torch.backends.cudnn.version(), 'gpu', torch.cuda.get_device_name(0), 'cv2', cv2.__version__)"
S=$SCRATCH_LOCAL/ad5A; mkdir -p $S
untar_checked $PK/smdd_train_raw.tar $S/raw          # -> $S/raw/SMDD_release_train/{train.csv,os25k_bf_t,m15k_t}
R=$S/raw/SMDD_release_train
[ "$(ls $R/os25k_bf_t | wc -l)" = 25000 ] && [ "$(ls $R/m15k_t | wc -l)" = 15000 ]
M=$S/gpumem.csv; MP=$(gpu_monitor $M)
t0=$(date +%s)
for d in os25k_bf_t m15k_t; do
  $PY -I $C/build/smdd_src/image_preprocess.py --in_folder $R/$d --out_folder $S/crop/$d > $S/crop_$d.log 2>&1
  tail -c 3000 $S/crop_$d.log | tail -2
done
echo "CROP_SECONDS $(( $(date +%s) - t0 ))"
kill $MP || true; echo "PEAK_MIB $(peak_mib $M)"
$PY -I $C/src/AD5/make_train_csv.py $R/train.csv $S/crop CROP_ROOT $S/crop/smdd_train_cropped_rel.csv $S/crop/crop_report.json
cp $S/crop_os25k_bf_t.log $S/crop_m15k_t.log $S/crop/
( cd $S/crop && find os25k_bf_t m15k_t -type f | sort | xargs sha256sum > CROPS_SHA256SUMS )
tar -cf $SCRATCH_LOCAL/smdd_train_cropped.tar -C $S/crop .
( cd $SCRATCH_LOCAL && sha256sum smdd_train_cropped.tar > smdd_train_cropped.tar.sha256 )
cp $SCRATCH_LOCAL/smdd_train_cropped.tar $SCRATCH_LOCAL/smdd_train_cropped.tar.sha256 $PK/
mkdir -p $RS; cp $S/crop/crop_report.json $RS/crop_report.json; cp $EN/madation/pip_freeze.txt $RS/pip_freeze_madation.txt
cat $PK/smdd_train_cropped.tar.sha256
echo SMOKE_A_OK; date

#!/bin/bash -l
#SBATCH -J ad5-selfmad-smoke
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=72G
#SBATCH --gres=gpu:1
#SBATCH --time=00:55:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD5-selfmad-smoke-%j.out
# Retrains of released methods (AD5), SelfMAD smoke + preparation job (1 GPU, at most 0.92 GPU-hours):
#  1. builds envs/AD5/selfmad from the shipped wheels;
#  2. face labels of the 25,000 SMDD genuine renders with the authors' preprocessing/face_labels.py UNCHANGED
#     (Segformer jonathandinu/face-parsing rev 758b82e1 from the shipped cache) -> packs/AD5/selfmad_labels.tar.gz;
#  3. the patched train__.py (-v last) for 1 epoch on 1,600 renders: seconds per step, peak memory, checkpoint format.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code/src/AD5/athena/ad5_common.sh
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
C=$PK/code; SRC=$C/build/selfmad_src; RUN=$C/src/AD5/checks/run_with_site.py
build_env selfmad $C/src/AD5/env/selfmad_requirements.txt $PK/wheels_selfmad.tar
PY=$EN/selfmad/bin/python
export HF_HUB_CACHE=$C/hf_cache
$PY -I -c "import torch, timm, albumentations, transformers, cv2; print('torch', torch.__version__, torch.version.cuda, 'timm', timm.__version__, 'alb', albumentations.__version__, 'transformers', transformers.__version__, 'cv2', cv2.__version__, torch.cuda.get_device_name(0))"
S=$SCRATCH_LOCAL/ad5S; mkdir -p $S/SMDD
untar_checked $PK/smdd_train_raw.tar $S/raw SMDD_release_train/os25k_bf_t
mv $S/raw/SMDD_release_train/os25k_bf_t $S/SMDD/os25k_bf_t
untar_checked $PK/selfmad_landmarks.tar $S                     # -> $S/SMDD_landmarks/os25k_bf_t/*.npy
echo "renders $(ls $S/SMDD/os25k_bf_t | wc -l) landmarks $(ls $S/SMDD_landmarks/os25k_bf_t | wc -l)"
if [ ! -f $PK/selfmad_labels.tar.gz.sha256 ]; then
  t0=$(date +%s); mkdir -p $S/SMDD_labels/os25k_bf_t     # face_labels.py does not create its output directory
  ( cd $SRC/preprocessing && $PY -I $RUN $SRC/preprocessing $SRC/preprocessing/face_labels.py -i $S/SMDD -o labels ) \
      > $S/face_labels.log 2>&1
  echo "LABEL_SECONDS $(( $(date +%s) - t0 )) labels $(ls $S/SMDD_labels/os25k_bf_t | wc -l)"
  ( cd $S && tar -cf - SMDD_labels | gzip -1 > $SCRATCH_LOCAL/selfmad_labels.tar.gz )
  ( cd $SCRATCH_LOCAL && sha256sum selfmad_labels.tar.gz > selfmad_labels.tar.gz.sha256 )
  cp $SCRATCH_LOCAL/selfmad_labels.tar.gz $PK/; cp $SCRATCH_LOCAL/selfmad_labels.tar.gz.sha256 $PK/
  cat $PK/selfmad_labels.tar.gz.sha256
else
  ( cd $PK && sha256sum -c selfmad_labels.tar.gz.sha256 ) && tar -xzf $PK/selfmad_labels.tar.gz -C $S
fi
# smoke: 1 epoch on 1,600 renders (100 steps of 16 + 16)
U=$S/sub; mkdir -p $U/SMDD/os25k_bf_t $U/SMDD_landmarks/os25k_bf_t $U/SMDD_labels/os25k_bf_t $S/out
for f in $(ls $S/SMDD/os25k_bf_t | sort | head -1600); do b=${f%.png}
  ln -s $S/SMDD/os25k_bf_t/$f $U/SMDD/os25k_bf_t/$f; ln -s $S/SMDD_landmarks/os25k_bf_t/$b.npy $U/SMDD_landmarks/os25k_bf_t/$b.npy
  ln -s $S/SMDD_labels/os25k_bf_t/$b.npy $U/SMDD_labels/os25k_bf_t/$b.npy; done
M=$S/gpumem.csv; MP=$(gpu_monitor $M); t0=$(date +%s); rc=0
( cd $SRC && AD5_SEED=401 $PY -I $RUN $SRC $SRC/train__.py -n ad5_smoke -m hrnet_w18 -b 32 -e 1 -lr 5e-4 -t SMDD -v last \
    -SMDD_path $U/SMDD -s $S/out ) > $S/train_smoke.log 2>&1 || rc=$?
kill $MP || true
echo "SMOKE rc $rc seconds $(( $(date +%s) - t0 )) peak_MiB $(peak_mib $M)"; tail -c 2500 $S/train_smoke.log
ls -laR $S/out | head -20
$PY -I -c "import torch,glob; f=glob.glob('$S/out/*/weights/epoch_1.tar')[0]; d=torch.load(f, map_location='cpu', weights_only=True); print(f, sorted(d), len(d['model']), list(d['model'])[:3])"
mkdir -p $RS/selfmad_smoke; cp $S/train_smoke.log $M $RS/selfmad_smoke/; cp $S/face_labels.log $RS/selfmad_smoke/ 2>/dev/null || true
cp $EN/selfmad/pip_freeze.txt $RS/pip_freeze_selfmad.txt
echo SELFMAD_SMOKE_DONE; date

#!/bin/bash -l
#SBATCH -J smadnext-FZ2
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -C memfs
#SBATCH --exclude=t0010
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/FZ2-%j.out
# Frozen read of the new diffusion ladder (FZ2): frozen CLIP ViT-L/14 (MADation input) and DINOv2 features of DG1 images
# and of the 64 A43 cross-environment check frames, in the container image, all work in $MEMFS, one result tar.
# usage: sbatch fz2_job.sbatch TAG DG1_LIST...      (DG1_LIST = result tar stems, e.g. setB_s0 setB_s1 addon_s0)
set -eo pipefail
set -u
TAG=$1; shift
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
SIF=$G/containers/smad_torch221_cu121_v1.sif
P=$G/packs/FZ2/fz2_pack.tar
OUT=$G/results/FZ2/FZ2_$TAG.tar
: "${MEMFS:?RAM disk required (-C memfs)}"
[ -e "$OUT" ] && { echo "result $OUT exists; refusing"; exit 3; }
W=$MEMFS/fz2; mkdir -p "$W/out" "$W/img"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; date; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "container sha (recorded): $(cat $SIF.sha256)"
cd "$W"
( cd $G/packs/FZ2 && sha256sum -c fz2_pack.tar.sha256 )
tar -xf "$P" -C "$W"
( cd "$W/fz2pack" && sha256sum -c MANIFEST.sha256 > /dev/null )
echo "pack ok"
for L in "$@"; do
  T=$G/results/DG1/DG1_$L.tar
  ( cd $G/results/DG1 && sha256sum -c DG1_$L.tar.sha256 )
  mkdir -p "$W/img/$L"; tar -xf "$T" -C "$W/img/$L"
  echo "$L: $(find $W/img/$L -name '*.png' | wc -l) png"
done
run() { apptainer exec --nv -B $G:$G -B $MEMFS:$MEMFS --env HF_HUB_OFFLINE=1 $SIF python -I "$W/fz2pack/code/fz2_feats.py" "$@"; }
CW=$W/fz2pack/weights/madation_fe_vitl14_model.safetensors
DW=$W/fz2pack/weights/dinov2_vitl14_lvd142m.safetensors
for bb in clip_mad dinov2; do
  WT=$CW; [ $bb = dinov2 ] && WT=$DW
  run --backbone $bb --weights $WT --common $W/fz2pack/code --img-root $W/fz2pack/a43check --list $W/fz2pack/a43check.csv \
      --out $W/out/${bb}_a43check.npz --workers 6
  for L in "$@"; do
    run --backbone $bb --weights $WT --common $W/fz2pack/code --img-root $W/img/$L --out $W/out/${bb}_$L.npz --workers 6
  done
done
cp "$G/logs/FZ2-$SLURM_JOB_ID.out" "$W/out/" 2>/dev/null || true
mkdir -p $G/results/FZ2
tar -cf "$OUT.part" -C "$W" out
mv "$OUT.part" "$OUT"
( cd $G/results/FZ2 && sha256sum "FZ2_$TAG.tar" > "FZ2_$TAG.tar.sha256" )
date; echo done

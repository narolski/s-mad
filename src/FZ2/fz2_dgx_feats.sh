#!/bin/bash
# FZ2 fallback/primary feature path on the DGX (FZ1's environment; fz2_feats.py reproduces FZ1's features exactly):
# both backbones on each DG1 list folder under /mnt/t7/smad_next/DG1/gen/<list>. Skips finished files; retries on CUDA OOM.
# usage: bash fz2_dgx_feats.sh LIST...
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ2/fz2_feats.py
O=/mnt/t7/smad_next/FZ2/results/dgx/out; mkdir -p $O /mnt/t7/smad_next/FZ2/logs
D2=$(ls /home/narolski/.cache/huggingface/hub/models--timm--vit_large_patch14_dinov2.lvd142m/snapshots/*/model.safetensors)
export OMP_NUM_THREADS=2 HF_HUB_OFFLINE=1
for L in "$@"; do
  for bb in clip_mad dinov2; do
    W=/mnt/t7/smad_next/FZ1/release/madation_fe_vitl14_model.safetensors; [ $bb = dinov2 ] && W=$D2
    [ -f $O/${bb}_$L.npz ] && { echo "$bb $L exists"; continue; }
    for k in 1 2 3 4 5 6; do
      $PY -I $S --backbone $bb --weights $W --common /home/narolski/mambamorph-code/smadcvpr \
        --img-root /mnt/t7/smad_next/DG1/gen/$L --out $O/${bb}_$L.npz --workers 4 > /mnt/t7/smad_next/FZ2/logs/dgx_${bb}_${L}_try$k.log 2>&1 \
        && { echo "$(date +%H:%M) $bb $L ok (try $k)"; break; }
      echo "$(date +%H:%M) $bb $L failed try $k: $(grep -m1 Error /mnt/t7/smad_next/FZ2/logs/dgx_${bb}_${L}_try$k.log)"; sleep 90
    done
  done
done

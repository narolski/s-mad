#!/bin/bash
# FZ1 feature extraction, sequential (one GPU process at a time; 4 loader workers). fp32 (no TF32).
# Each backbone is first run on 8 images (--smoke) with the same command line, then on the full sets.
set -euo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ1/fz1_feats.py
L=/mnt/t7/smad_next/FZ1/logs
mkdir -p $L
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
$PY -I $S --check --no-tf32 --rgb > $L/check_fp32_rgbcontrol.log 2>&1
for bb in clip_mad clip_native dinov3 dinov2; do
  case $bb in
    clip_mad) sets=a43,sg3,eval,smdd,smdd_flip ;;
    *) sets=a43,sg3 ;;
  esac
  $PY -I $S --backbone $bb --set a43 --smoke --no-tf32 > $L/${bb}_smoke.log 2>&1
  $PY -I $S --backbone $bb --set $sets --no-tf32 > $L/${bb}.log 2>&1
  echo "$bb done $(date)" >> $L/progress.txt
done

#!/bin/bash
# FZ1 feature extraction, second stage (replaces the tail of run_feats.sh after its CLIP a43 / sg3 sets):
# other backbones' probe sets first, then CLIP eval and SMDD (orig + flip in one decode pass). fp32 (no TF32).
set -euo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ1/fz1_feats.py
L=/mnt/t7/smad_next/FZ1/logs
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
for bb in clip_native dinov3 dinov2; do
  $PY -I $S --backbone $bb --set a43 --smoke --no-tf32 > $L/${bb}_smoke.log 2>&1
  $PY -I $S --backbone $bb --set a43,sg3 --no-tf32 > $L/${bb}.log 2>&1
  echo "$bb done $(date)" >> $L/progress.txt
done
$PY -I $S --backbone clip_mad --set smdd+flip --smoke --no-tf32 > $L/clip_mad_smdd_smoke.log 2>&1
$PY -I $S --backbone clip_mad --set eval,smdd+flip --no-tf32 > $L/clip_mad_eval_smdd.log 2>&1
echo "clip_mad eval+smdd done $(date)" >> $L/progress.txt

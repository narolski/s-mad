#!/bin/bash
# FZ1 stage 3: after CLIP eval features exist (fp32), stop the fp32 SMDD pass and extract SMDD orig + flip with
# TF32 matmuls (throughput; allowed by the prereg, recorded in the npz meta). Smoke on 8 images first.
set -euo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ1/fz1_feats.py
L=/mnt/t7/smad_next/FZ1/logs
until [ -f /mnt/t7/smad_next/FZ1/feats/clip_mad/eval.npz ]; do sleep 5; done
sleep 3
B=$(pgrep -f "^/bin/bash /home/narolski/smad-next/src/FZ1/run_feats2.sh" || true)
P=$(pgrep -f "fz1_feats.py --backbone clip_mad --set eval,smdd\+flip" || true)
echo "killing bash $B python $P"
[ -n "$B" ] && kill $B || true
[ -n "$P" ] && kill $P || true
sleep 15
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
rm -f /mnt/t7/smad_next/FZ1/feats/clip_mad/smdd_smoke.npz /mnt/t7/smad_next/FZ1/feats/clip_mad/smdd_flip_smoke.npz
$PY -I $S --backbone clip_mad --set smdd+flip --smoke > $L/clip_mad_smdd_tf32_smoke.log 2>&1
$PY -I $S --backbone clip_mad --set smdd+flip > $L/clip_mad_smdd_tf32.log 2>&1
echo "clip_mad smdd (tf32) done $(date)" >> $L/progress.txt

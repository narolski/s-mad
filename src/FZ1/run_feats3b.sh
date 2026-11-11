#!/bin/bash
# FZ1 stage 3 retry: SMDD orig + flip with TF32. Stage 3 died at 17:41 with CUDA out of memory while moving the
# model to the GPU (machine memory full, not our process). Retries each step up to 6 times, 90 s apart.
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/FZ1/fz1_feats.py
L=/mnt/t7/smad_next/FZ1/logs
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
run() {  # $1 = log name, rest = args
  local log=$1; shift
  for k in 1 2 3 4 5 6; do
    $PY -I $S "$@" > $L/${log}_try$k.log 2>&1 && { echo "$log ok on try $k $(date)" >> $L/progress.txt; return 0; }
    echo "$log failed try $k $(date): $(grep -m1 -E 'Error' $L/${log}_try$k.log)" >> $L/progress.txt
    sleep 90
  done
  return 1
}
rm -f /mnt/t7/smad_next/FZ1/feats/clip_mad/smdd_smoke.npz /mnt/t7/smad_next/FZ1/feats/clip_mad/smdd_flip_smoke.npz
run clip_mad_smdd_tf32_smoke --backbone clip_mad --set smdd+flip --smoke || exit 1
run clip_mad_smdd_tf32 --backbone clip_mad --set smdd+flip || exit 1
echo "clip_mad smdd (tf32) done $(date)" >> $L/progress.txt

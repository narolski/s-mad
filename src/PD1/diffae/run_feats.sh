#!/bin/bash
# PD1 DiffAE feature extraction with retry on CUDA OOM at model load (shared GB10). One model per process.
# usage: run_feats.sh <model> <sets> [extra args]; each step retried up to 40 times, 120 s apart.
set -u
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/PD1/diffae/pd1_feats.py
L=/mnt/t7/smad_next/PD1/diffae/logs
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2
m=$1; sets=$2; shift 2
for i in $(seq 1 40); do
  nice -n 10 $PY -I $S --model $m --sets $sets "$@" > $L/feat_${m}_$(echo $sets | tr ',' '_')_try$i.log 2>&1 && { echo "$m $sets ok (try $i) $(date)" >> $L/feat_progress.txt; exit 0; }
  echo "$m $sets try $i failed: $(grep -m1 -o 'out of memory\|Error.*' $L/feat_${m}_$(echo $sets | tr ',' '_')_try$i.log | head -1) $(date)" >> $L/feat_progress.txt
  sleep 120
done
exit 1

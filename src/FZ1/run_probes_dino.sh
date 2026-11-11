#!/bin/bash
# FZ1: run the P2 probes for each DINO backbone once its features exist (one process at a time), then aggregate.
set -euo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
F=/mnt/t7/smad_next/FZ1
export OMP_NUM_THREADS=1
cd /home/narolski/smad-next
for bb in dinov3 dinov2; do
  until [ -f $F/feats/$bb/sg3.npz ]; do sleep 20; done
  $PY -I src/FZ1/fz1_probe.py --run $bb --jobs 1 > $F/logs/probe_$bb.log 2>&1
done
$PY -I src/FZ1/fz1_probe.py --aggregate > $F/logs/probe_aggregate.log 2>&1
echo "probes done $(date)" >> $F/logs/progress.txt

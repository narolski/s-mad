#!/usr/bin/env bash
# PD1 cross-family transfer: sequential GPU feature extraction in the common space (one process at a time, nice 10).
# Log: /mnt/t7/smad_next/PD1/transfer/logs/feats.log
set -uo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 HF_HUB_OFFLINE=1
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/PD1/transfer
L=/mnt/t7/smad_next/PD1/transfer/logs/feats.log
SETS=Lad,Dtr,Lbench,Dev,Lsoft,Df256,Lx1g,Lblank
run() { for t in 1 2 3; do echo "$(date +%T) start $* try $t" >> $L
          nice -n 10 $PY -I tf_feats.py "$@" < /dev/null 2>&1 | grep -v -i warn | grep -v "  batch" >> $L && break; sleep 30; done; }
run --backbone clip --sets $SETS --bs 32 --workers 2
run --backbone dinov3 --sets $SETS --bs 32 --workers 2
echo "$(date +%T) queue done" >> $L

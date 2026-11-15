#!/usr/bin/env bash
# PD1 cross-family transfer: full analysis per feature (at most 2 CPU processes at a time, nice 10, 2 threads).
set -uo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/PD1/transfer
for f in "$@"; do
  nice -n 10 $PY -I tf_analysis.py --feat $f --B 2000 --splits 200 > /mnt/t7/smad_next/PD1/transfer/logs/analysis_$f.log 2>&1
done

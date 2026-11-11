#!/bin/bash
# CPU analyses with thread caps (lead, 11 Nov evening): gate G-c for the given tags, then the full AR3 baselines
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/AR1; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /tmp
nice -n 10 $P -I $S/gate_c.py --tags "$1"
nice -n 10 $P -I $S/baselines.py
echo CPU_DONE

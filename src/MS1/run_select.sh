#!/bin/bash
# MS1: FFHQ references then person selection (thread caps, nice 10)
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/MS1
nice -n 10 $P -I ffhq_select.py refs
nice -n 10 $P -I ffhq_select.py select --n 900

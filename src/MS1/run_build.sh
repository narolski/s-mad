#!/bin/bash
# MS1: FFHQ images (morph stage, then stored copies), thread caps, nice 10, 2 workers
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/MS1
nice -n 10 $P -I ffhq_build.py morph --workers 2
nice -n 10 $P -I ffhq_build.py soft --workers 2
nice -n 10 $P -I gate.py pixel
echo BUILD_DONE

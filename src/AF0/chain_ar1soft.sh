#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
nice -n 10 $P -I soften.py build --list ar1soft_src --strengths amsl112,fm61 && $P -I lists_extra.py ar1soft && \
OMP_NUM_THREADS=1 nice -n 10 $P -I -c "
import sys; sys.path.insert(0,'.'); import af0lib as L
for g in (32,24,16):
    L.prep('ar1soft',g); L.prep_inner('ar1soft',g)
print('prep ar1soft ok')"

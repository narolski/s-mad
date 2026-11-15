#!/usr/bin/env bash
# wave 4: softened AF0 training copies; retries when the shared GPU refuses the face detector's allocation.
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
for t in 1 2 3 4 5 6 7 8 9 10; do
  nice -n 10 $P -I soften.py build --list soft_src --strengths amsl112,fm61 --alternate && break
  echo "soften try $t failed"; sleep 60
done
$P -I lists_extra.py soft && OMP_NUM_THREADS=1 nice -n 10 $P -I -c "
import sys; sys.path.insert(0,'.'); import af0lib as L
for g in (32,24,16):
    L.prep('soft',g); L.prep_inner('soft',g)
print('prep soft ok')"

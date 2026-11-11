#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
until [ -f /mnt/t7/smad_next/AF0/halves.csv ] && ! pgrep -f "ghost.py --wave" >/dev/null; do sleep 30; done
$P -I lists_extra.py af0_h && OMP_NUM_THREADS=1 nice -n 10 $P -I -c "
import sys; sys.path.insert(0,'.'); import af0lib as L
for g in (32,24,16):
    L.prep('af0_h',g); L.prep_inner('af0_h',g)
print('prep af0_h ok')" || exit 1
OMP_NUM_THREADS=1 nice -n 10 $P -I sanity.py --workers 1 > /mnt/t7/smad_next/AF0/sanity.log 2>&1 &
$P -I lists_extra.py soft_src && nice -n 10 $P -I soften.py build --list soft_src --strengths amsl112,fm61 --alternate && \
$P -I lists_extra.py soft && OMP_NUM_THREADS=1 nice -n 10 $P -I -c "
import sys; sys.path.insert(0,'.'); import af0lib as L
for g in (32,24,16):
    L.prep('soft',g); L.prep_inner('soft',g)
print('prep soft ok')"
wait

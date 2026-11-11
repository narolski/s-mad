#!/usr/bin/env bash
# lead 18:45 (round 3): softened copies (61.2 px and 112.7 px, the verified prep_eval E7 branch via soften.py,
# unchanged) of AR1 OpenCV R4, R3 (536 hosts) and R3m (200 ar1soft hosts); then lists, prep, cue statistics.
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
for t in 1 2 3 4 5 6 7 8 9 10; do
  nice -n 10 $P -I soften.py build --list ladsoft_src --strengths amsl112,fm61 && break
  echo "soften try $t failed"; sleep 60
done
$P -I lists_extra.py ladsoft && OMP_NUM_THREADS=1 nice -n 10 $P -I -c "
import sys; sys.path.insert(0,'.'); import af0lib as L
for g in (32,24,16):
    L.prep('ladsoft',g); L.prep_inner('ladsoft',g)
print('prep ladsoft ok')"
OMP_NUM_THREADS=1 nice -n 10 $P -I cues_all.py ladsoft --workers 1
echo LADSOFT_DONE

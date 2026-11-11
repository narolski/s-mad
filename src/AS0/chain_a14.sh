#!/bin/bash
# AS0 amendment A14: R2w4 measurement and landmark detection, one process at a time, OMP 2, nice 10.
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
L=/mnt/t7/smad_next/AS0/logs
echo "start $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --sets L4 >> $L/measure_a14.log 2>&1
echo "measured $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD4 >> $L/landmarks_a14.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_a14.log 2>&1
nice -n 10 $P -I as0_measure.py --merge >> $L/measure_a14.log 2>&1
nice -n 10 $P -I as0_geom.py >> $L/measure_a14.log 2>&1
echo "done $(date +%H:%M)"

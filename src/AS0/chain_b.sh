#!/bin/bash
# AS0 compute slot B (one process at a time, nice 10): copy landmarks, nominal IOD, measurement of detected sets,
# remaining copy landmarks, blank sensitivity run (amendment A4).
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
echo "start $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets FmO,X >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_measure.py --iod > $L/iod.log 2>&1
echo "iod $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --sets Fm,FmO,G,D,M,Ds,Fe,X >> $L/measure_b.log 2>&1
echo "measure_b $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LsoftN,LsoftO,FeO >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_measure.py --sets LsoftN,LsoftO,FeO >> $L/measure_b.log 2>&1
echo "copies $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --blank --sets L --roles R0,R2w,R3,R3m,R4 >> $L/measure_blank.log 2>&1
nice -n 10 $P -I as0_measure.py --blank --sets Fm,FmO >> $L/measure_blank.log 2>&1
echo "done $(date +%H:%M)"

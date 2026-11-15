#!/bin/bash
# AS0 compute slot B, second plan (18:53; X dropped from phase 1 because of CPU load): merge landmarks, nominal IOD,
# measure the detected sets, blank sensitivity run (A4, reduced), own landmarks of the Lsoft copies and natives.
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
echo "start $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_measure.py --iod > $L/iod.log 2>&1
echo "iod $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --sets Fm,FmO,D,M,Ds,Fe,G >> $L/measure_b.log 2>&1
echo "measure_b $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --blank --sets L --roles R3,R4 >> $L/measure_blank.log 2>&1
nice -n 10 $P -I as0_measure.py --blank --sets Fm,FmO --roles native,e7_FaceMorpher >> $L/measure_blank.log 2>&1
echo "blank $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LsoftN,LsoftO >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_measure.py --sets LsoftN,LsoftO >> $L/measure_b.log 2>&1
echo "done $(date +%H:%M)"

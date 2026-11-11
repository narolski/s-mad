#!/bin/bash
# AS0 slot B, third plan (19:00; machine load about 140): after the running measurement (PID $1) of Fm, FmO, D, M,
# Ds, Fe, G: R8 colorFERET pairs (A7), blank sensitivity run on a host subsample (A4), Lsoft own landmarks (A3).
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
while kill -0 "$1" 2>/dev/null; do sleep 20; done
echo "measure_b ended $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --sets R8 --db feret >> $L/measure_b.log 2>&1
echo "R8 feret $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --blank --sets L --roles R3,R4 --subsample 3 >> $L/measure_blank.log 2>&1
nice -n 10 $P -I as0_measure.py --blank --sets Fm,FmO --roles native,e7_FaceMorpher >> $L/measure_blank.log 2>&1
echo "blank $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LsoftN,LsoftO >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_measure.py --sets LsoftN,LsoftO >> $L/measure_b.log 2>&1
echo "done $(date +%H:%M)"

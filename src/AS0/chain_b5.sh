#!/bin/bash
# AS0 slot B, fifth plan (19:35): after the running chain_b4 step (R8 colorFERET, PID $1) -> G, then a second worker on
# the detected-ladder landmarks LD1 (chunks from the end, A10), then blank run, Ds, Lsoft own landmarks, Fe, Fm secondary.
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
M="nice -n 10 $P -I as0_measure.py"
while kill -0 "$1" 2>/dev/null; do sleep 15; done
echo "R8 feret ended $(date +%H:%M)"
$M --sets G >> $L/measure_b.log 2>&1
echo "G $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD1 --reverse >> $L/landmarks_b.log 2>&1
echo "LD1 reverse worker $(date +%H:%M)"
$M --blank --sets L --roles R3,R4 --subsample 3 >> $L/measure_blank.log 2>&1
$M --blank --sets Fm,FmO --roles native,e7_FaceMorpher >> $L/measure_blank.log 2>&1
echo "blank $(date +%H:%M)"
$M --sets Ds >> $L/measure_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LsoftN,LsoftO >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
$M --sets LsoftN,LsoftO >> $L/measure_b.log 2>&1
$M --sets Fe --roles native,e7_facemorpher,e7_amsl >> $L/measure_b.log 2>&1
$M --sets Fm --roles e7_OpenCV,e7_Webmorph >> $L/measure_b.log 2>&1
echo "done $(date +%H:%M)"

#!/bin/bash
# AS0 slot B, fourth plan (19:04; load about 140, about 1.4 s per 512 image): primary history first, then the
# diffusion ladder, R8 colorFERET, GAN blocks, stored crops, blank run (subsample), Fe, Lsoft own landmarks,
# secondary Fm copies.
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
M="nice -n 10 $P -I as0_measure.py"
echo "start $(date +%H:%M)"
$M --sets Fm --roles native,e7_FaceMorpher >> $L/measure_b.log 2>&1
$M --sets FmO --roles e7_FaceMorpher >> $L/measure_b.log 2>&1
echo "Fm primary $(date +%H:%M)"
$M --sets D,M >> $L/measure_b.log 2>&1
echo "D M $(date +%H:%M)"
$M --sets R8 --db feret >> $L/measure_b.log 2>&1
echo "R8 feret $(date +%H:%M)"
$M --sets G >> $L/measure_b.log 2>&1
echo "G $(date +%H:%M)"
$M --sets Ds >> $L/measure_b.log 2>&1
$M --blank --sets L --roles R3,R4 --subsample 3 >> $L/measure_blank.log 2>&1
$M --blank --sets Fm,FmO --roles native,e7_FaceMorpher >> $L/measure_blank.log 2>&1
echo "Ds blank $(date +%H:%M)"
$M --sets Fe --roles native,e7_facemorpher,e7_amsl >> $L/measure_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LsoftN,LsoftO >> $L/landmarks_b.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_b.log 2>&1
$M --sets LsoftN,LsoftO >> $L/measure_b.log 2>&1
$M --sets Fm --roles e7_OpenCV,e7_Webmorph >> $L/measure_b.log 2>&1
echo "done $(date +%H:%M)"

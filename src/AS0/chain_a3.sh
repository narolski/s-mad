#!/bin/bash
# AS0 slot A, third plan (19:00): when L is measured, stop the first measurement process (PID $1); then detected
# landmarks on built ladder images LD1 = R0, R3, R4 (A10), Lsoft and S measurement, then LD2.
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
until [ -f /mnt/t7/smad_next/AS0/meas/L_09216.npz ]; do sleep 20; done
sleep 5
kill "$1" 2>/dev/null || true
echo "L done, first process stopped $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD1 >> $L/landmarks_a.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_a.log 2>&1
echo "LD1 $(date +%H:%M)"
nice -n 10 $P -I as0_measure.py --sets Lsoft,S >> $L/measure_a2.log 2>&1
echo "Lsoft S $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD2 >> $L/landmarks_a.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_a.log 2>&1
echo "done $(date +%H:%M)"

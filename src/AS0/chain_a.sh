#!/bin/bash
# AS0 compute slot A: waits for the first measurement process, then detects landmarks on the built ladder images
# (amendment A10: LD1 = R0, S0, R3, R4; LD2 = R2w, R3m, R2wm; LD3 = graded).
set -euo pipefail
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/AS0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
L=/mnt/t7/smad_next/AS0/logs
while kill -0 "$1" 2>/dev/null; do sleep 30; done
echo "start $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD1 >> $L/landmarks_a.log 2>&1
echo "LD1 $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD2 >> $L/landmarks_a.log 2>&1
echo "LD2 $(date +%H:%M)"
nice -n 10 $P -I as0_landmarks.py --threads 2 --sets LD3 >> $L/landmarks_a.log 2>&1
nice -n 10 $P -I as0_landmarks.py --merge >> $L/landmarks_a.log 2>&1
echo "done $(date +%H:%M)"

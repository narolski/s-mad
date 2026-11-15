#!/bin/bash
# PN1 GPU queue 2: stop the DGX DINOv3 job after ar1soft (GPU allowance), then CLIP means of the development copies.
set -u
P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
L=/mnt/t7/smad_next/PN1/lists
cd /home/narolski/smad-next/src/PN1
export HF_HUB_OFFLINE=1
until [ -f /mnt/t7/smad_next/PN1/feat/dinov3_512/ar1soft.mean.npy ]; do sleep 10; done
sleep 5
kill 2356268 2>/dev/null; echo "dinov3 stopped after ar1soft $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
while kill -0 2356268 2>/dev/null; do sleep 2; done
t0=$(date +%s); echo "clip224 (2) start $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
nice -n 10 $P featmean.py --backbone clip224 --job devsoft=$L/devsoft.csv
echo "clip224 (2) rc $? end $(date +%T) wall_s $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log

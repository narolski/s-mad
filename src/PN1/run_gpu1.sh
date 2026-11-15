#!/bin/bash
# PN1 GPU queue 1 (DGX, one process at a time, nice 10). Logs wall time per backbone to gpu_time.log.
set -u
P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
L=/mnt/t7/smad_next/PN1/lists
A=/mnt/t7/smad_next/AF0/lists
cd /home/narolski/smad-next/src/PN1
export HF_HUB_OFFLINE=1
t0=$(date +%s); echo "clip224 start $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
nice -n 10 $P featmean.py --backbone clip224 --job eq8_ar1=$L/eq8_ar1.csv --job r2w4=$L/r2w4.csv --job frll_e5=$L/frll_e5.csv
echo "clip224 rc $? end $(date +%T) wall_s $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log
t0=$(date +%s); echo "dinov3 start $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
nice -n 10 $P featmean.py --backbone dinov3_512 --job eq8_ar1=$L/eq8_ar1.csv --job ar1soft=$A/ar1soft.csv --job r2w4_td=$L/r2w4_td.csv --job frll_e5s=$L/frll_e5s.csv
echo "dinov3 rc $? end $(date +%T) wall_s $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log

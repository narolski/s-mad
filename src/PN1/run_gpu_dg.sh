#!/bin/bash
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"; L=/mnt/t7/smad_next/PN1/lists
cd /home/narolski/smad-next/src/PN1; export HF_HUB_OFFLINE=1
for bb in clip224 dinov3_512; do t0=$(date +%s); $P featmean_any.py --backbone $bb --bs 32 --job dg1_test=$L/dg1_test.csv; echo "dg1 $bb rc $? wall $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log; done

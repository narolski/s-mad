#!/bin/bash
# PN1 amendment 8: CLIP and DINOv3 means of the spliced images and their blanked test-host copies (one GPU process).
set -u
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"; L=/mnt/t7/smad_next/PN1/lists
cd /home/narolski/smad-next/src/PN1; export HF_HUB_OFFLINE=1
t0=$(date +%s); $P featmean.py --backbone clip224 --bs 32 --job splice_nat=$L/splice_nat.csv --job splice_blank=$L/splice_blank.csv
echo "splice clip rc $? wall $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log
t0=$(date +%s); $P featmean.py --backbone dinov3_512 --bs 16 --job splice_nat=$L/splice_nat.csv --job splice_blank=$L/splice_blank.csv
echo "splice dinov3 rc $? wall $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log

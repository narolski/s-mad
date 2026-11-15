#!/usr/bin/env bash
until [ "$(cat /mnt/t7/smad_next/AF0/feat/dinov3_512/af0_w2.done)" = "4200" ] && ! pgrep -f "feat.py --backbone dinov3_512 .*--name af0_w2" >/dev/null; do sleep 20; done
cd /home/narolski/smad-next/src/AF0 && OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1 --heads ridge,mlp,logreg --tag full

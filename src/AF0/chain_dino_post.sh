#!/usr/bin/env bash
# after the full DINOv3 heads: F4 fits (ridge, MLP x5, logreg), then the shuffled-map control (ridge).
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
until grep -q seconds_last /mnt/t7/smad_next/AF0/heads/dinov3_512/full/log.json 2>/dev/null; do sleep 30; done
for t in conf unconf; do
  OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval af0_w1,af0_w2 \
    --heads ridge,mlp,logreg --tag f4_$t --train-ids /mnt/t7/smad_next/AF0/f4/${t}_ids.npy
done
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1 \
  --heads ridge --tag shuffle --target shuffle
echo POST_DONE

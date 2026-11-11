#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
OMP_NUM_THREADS=2 nice -n 10 $P -I cn0.py read --backbones clip224 > /mnt/t7/smad_next/AF0/cn0_clip224.log 2>&1
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip224 --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1,bench_s \
  --heads ridge,mlp,logreg --tag full
for t in conf unconf; do
  OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip224 --train af0_w1,af0_w2 --eval af0_w1,af0_w2 \
    --heads ridge,mlp,logreg --tag f4_$t --train-ids /mnt/t7/smad_next/AF0/f4/${t}_ids.npy
done
echo CLIP224_FULL_DONE

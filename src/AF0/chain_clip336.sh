#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip224 --train af0_w1,af0_w2 --eval h1,af0_h,ar1soft --heads ridge,mlp,logreg --tag full --score-only
./waitfeat.sh clip336 ar1
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip336 --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1 --heads ridge,mlp,logreg --tag full
./waitfeat.sh clip336 bench_s
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip336 --train af0_w1,af0_w2 --eval bench_s --heads ridge,mlp,logreg --tag full --score-only
./waitfeat.sh clip336 h1
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip336 --train af0_w1,af0_w2 --eval h1 --heads ridge,mlp,logreg --tag full --score-only
OMP_NUM_THREADS=1 nice -n 10 $P -I metrics.py --backbone clip336 --tag full --af0 af0_w1,af0_w2 --bench bench_s --keys score,score_top10 > /mnt/t7/smad_next/AF0/metrics_clip336_full.log 2>&1
for t in conf unconf; do
  OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone clip336 --train af0_w1,af0_w2 --eval af0_w1,af0_w2 \
    --heads ridge,mlp,logreg --tag f4_$t --train-ids /mnt/t7/smad_next/AF0/f4/${t}_ids.npy
done
OMP_NUM_THREADS=1 nice -n 10 $P -I f4.py read --backbone clip336 --af0 af0_w1,af0_w2 > /mnt/t7/smad_next/AF0/f4_clip336.log 2>&1
echo CLIP336_DONE

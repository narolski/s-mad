#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
until grep -q POST_DONE /mnt/t7/smad_next/AF0/chain_dino_post.log 2>/dev/null; do sleep 30; done
./waitfeat.sh dinov3_512 bench_s
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval bench_s --heads ridge,mlp,logreg --tag full --score-only
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval bench_s --heads ridge --tag shuffle --score-only
./waitfeat.sh dinov3_512 af0_h
./chain_wave2.sh dinov3_512 af0_w1,af0_h,ar1,bench_s
./waitfeat.sh dinov3_512 h1
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval h1,af0_h --heads ridge,mlp,logreg --tag full --score-only
for T in alpha g D G; do OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_h --eval h1 --heads ridge,mlp --seeds 401 --tag w2_$T --score-only; done
./waitfeat.sh dinov3_512 ar1g
OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval ar1g --heads ridge,mlp,logreg --tag full --score-only
for T in alpha g D G; do OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone dinov3_512 --train af0_w1,af0_h --eval ar1g --heads ridge,mlp --seeds 401 --tag w2_$T --score-only; done
echo DINO_REST_DONE

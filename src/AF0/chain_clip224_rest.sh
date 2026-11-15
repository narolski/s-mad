#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
until grep -q CLIP224_FULL_DONE /mnt/t7/smad_next/AF0/chain_clip224_full.log 2>/dev/null; do sleep 30; done
OMP_NUM_THREADS=2 nice -n 10 $P -I cn0.py read --backbones clip224,dinov3_512 --dense-tag full > /mnt/t7/smad_next/AF0/cn0_run.log 2>&1
./waitfeat.sh clip224 af0_h
./chain_wave2.sh clip224 af0_w1,af0_h,ar1,bench_s,h1
./waitfeat.sh clip224 ar1soft
./waitfeat.sh clip224 h1
OMP_NUM_THREADS=2 nice -n 10 $P -I arms.py fit --backbone clip224 --arms a,b,c,d,e
until [ -f /mnt/t7/smad_next/AF0/lists/soft.csv ]; do sleep 60; done
./waitfeat.sh clip224 soft
OMP_NUM_THREADS=2 nice -n 10 $P -I arms.py fit --backbone clip224 --arms a4,b4,c4,d4,e4
OMP_NUM_THREADS=2 nice -n 10 $P -I arms.py read --backbone clip224
echo CLIP224_REST_DONE

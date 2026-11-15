#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
while pgrep -f "cues_all.py ar1" >/dev/null; do sleep 30; done
OMP_NUM_THREADS=1 nice -n 10 $P -I thumbs.py af0_w1 af0_w2 ar1 bench_s h1 --workers 2 && \
OMP_NUM_THREADS=2 nice -n 10 $P -I thumb_heads.py --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1,bench_s,h1 --tag full
echo THUMBS_DONE

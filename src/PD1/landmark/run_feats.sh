#!/usr/bin/env bash
# PD1 landmark: sequential GPU feature extraction (one process at a time, nice 10). Log: OUT/logs/feats.log
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/PD1/landmark
L=/mnt/t7/smad_next/PD1/landmark/logs/feats.log
run() { for t in 1 2 3; do echo "$(date +%T) start $* try $t" >> $L
          nice -n 10 $PY -I feat.py "$@" < /dev/null 2>&1 | grep -v -i warn >> $L && break; sleep 30; done; }
run --backbone dinov3_512 --list smdd --limit 8 --bs 8
run --backbone clip224 --list af0,bench --limit 8 --bs 8
run --backbone clip224 --list ar1,smdd,af0,bench,h1,ar1g --bs 16 --workers 2
run --backbone dinov3_512 --list smdd --bs 8 --workers 2
run --backbone dinov3_512 --list ar1 --only-rung R2wm --bs 8 --workers 2
echo "$(date +%T) queue done" >> $L

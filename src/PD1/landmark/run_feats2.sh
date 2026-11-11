#!/usr/bin/env bash
# PD1 landmark, amendment 1 sets: waits for the first queue (run_feats.sh) to finish, then extracts sequentially.
set -uo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/PD1/landmark
L=/mnt/t7/smad_next/PD1/landmark/logs/feats.log
until grep -q "queue done" $L; do sleep 30; done
run() { for t in 1 2 3; do echo "$(date +%T) start $* try $t" >> $L
          nice -n 10 $PY -I feat.py "$@" < /dev/null 2>&1 | grep -v -i warn >> $L && break; sleep 30; done; }
run --backbone clip224 --list ar1soft --limit 8 --bs 8
run --backbone clip224 --list ar1soft,af0h --bs 16 --workers 2
run --backbone dinov3_512 --list ar1soft --limit 8 --bs 8
run --backbone dinov3_512 --list ar1soft --bs 8 --workers 2
# DINOv3 halves: AF0's cache if complete, else extract here
if [ "$(cat /mnt/t7/smad_next/AF0/feat/dinov3_512/af0_h.done 2>/dev/null)" = "3120" ]; then
  nice -n 10 $PY -I af0_means.py dinov3_512 af0_h >> $L 2>&1
else
  run --backbone dinov3_512 --list af0h --bs 8 --workers 2
fi
echo "$(date +%T) queue2 done" >> $L

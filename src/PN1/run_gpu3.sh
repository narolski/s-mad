#!/bin/bash
# PN1 GPU queue 3 (after queue 2): JPEG-call verification (prep_eval's detector needs CUDA), then the 8-image DGX test
# of the Athena task script run.sh (host Python, test pack, 3 steps, 8 scored rows).
set -u
P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /home/narolski/smad-next/src/PN1
until grep -q "clip224 (2) rc" /mnt/t7/smad_next/PN1/gpu_time.log 2>/dev/null; do sleep 10; done
t0=$(date +%s); echo "jpeg verify start $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
OMP_NUM_THREADS=2 nice -n 10 $P jpeg_c.py verify
echo "jpeg verify rc $? end $(date +%T) wall_s $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log
B=/mnt/t7/smad_next/PN1/dgxtest; rm -rf "$B"; mkdir -p "$B/root/results" "$B/work" "$B/task" "$B/tmp"
cp run.sh "$B/task/run.sh"; printf 'TASK=PN1_B_s401_dgxtest\nARM=B\nSEED=401\n' > "$B/task/task.env"
t0=$(date +%s); echo "dgx run.sh test start $(date +%T)" >> /mnt/t7/smad_next/PN1/gpu_time.log
( cd "$B/work" && TMPDIR=$B/tmp TASK_DIR="$B/task" TASK_WORK="$B/work" PN1_ROOT="$B/root" \
  PN1_PACK=/mnt/t7/smad_next/PN1/pn1_pack_limit8.tar PN1_LOCAL=1 PN1_PY=/home/narolski/mambamorph-code/.venv-spark/bin/python \
  PN1_STEPS=3 PN1_LIMIT=8 PN1_WORKERS=2 nice -n 10 bash "$B/task/run.sh" ) > "$B/run.log" 2>&1
echo "dgx run.sh test rc $? end $(date +%T) wall_s $(( $(date +%s) - t0 ))" >> /mnt/t7/smad_next/PN1/gpu_time.log

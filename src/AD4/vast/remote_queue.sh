#!/bin/bash
# Simple queue on the rented machine: one worker per GPU, each claims the next task directory in /workspace/ad4/tasks
# (atomic mkdir of a claim marker) and runs its run.sh exactly as a WCSS slot does (TASK_DIR, TASK_WORK, cwd),
# with AD4_LOCAL=1 (host python), AD4_ROOT=/workspace/ad4/root, 7 loader workers (as on WCSS).
# Results: /workspace/ad4/root/smad-next/results/AD4/<task>.tar(.sha256). Writes /workspace/ad4/ALL_DONE at the end.
#   nohup setsid bash remote_queue.sh NGPU > /workspace/ad4/queue.log 2>&1 &
set -u
B=/workspace/ad4
N=${1:?number of GPUs}
mkdir -p "$B/claims" "$B/work" "$B/logs" "$B/rc"
echo "$(date +%FT%T) queue start N=$N" > "$B/QUEUE_STARTED"
worker() {
  local g=$1 t
  while :; do
    local got=""
    for t in $(ls "$B/tasks" | sort); do
      if mkdir "$B/claims/$t" 2>/dev/null; then got=$t; break; fi
    done
    [ -n "$got" ] || break
    echo "$(date +%FT%T) gpu $g start $got"
    rm -rf "$B/work/$got"; mkdir -p "$B/work/$got"
    ( cd "$B/work/$got" && CUDA_VISIBLE_DEVICES=$g TASK_DIR="$B/tasks/$got" TASK_WORK="$B/work/$got" \
        AD4_LOCAL=1 AD4_PY=python AD4_ROOT="$B/root" AD4_WORKERS=7 TMPDIR=/tmp bash "$B/tasks/$got/run.sh" ) \
      > "$B/logs/$got.log" 2>&1
    rc=$?
    echo "$rc" > "$B/rc/$got"
    echo "$(date +%FT%T) gpu $g end $got rc=$rc"
    [ "$rc" -eq 0 ] && rm -rf "$B/work/$got"
  done
  echo "$(date +%FT%T) gpu $g idle"
}
# GPU memory sampler (peak per GPU, MiB)
( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> "$B/logs/gpumem.csv"; sleep 20; done ) &
SAMP=$!
for ((g = 0; g < N; g++)); do worker "$g" & done
wait $(jobs -p | grep -v "^$SAMP$")
kill "$SAMP" 2>/dev/null
echo "$(date +%FT%T) all workers idle" > "$B/ALL_DONE"

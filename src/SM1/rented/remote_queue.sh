#!/bin/bash
# SM1 rented queue (A13): the ViT-B/16 fits one after another through fit_local.sh; one result tar + .sha256 per fit in
# /workspace/sm1r/results. A fit that fails is rerun once unchanged (infrastructure rule); a fit with a non-finite loss
# is not rerun. The work folder is removed after each fit.
set -u
B=/workspace/sm1r
cd "$B"; date > "$B/QUEUE_STARTED"; mkdir -p "$B/logs" "$B/rc"
TASKS=${1:?tasks}
for T in $TASKS; do
  ARM=$(echo "$T" | cut -d_ -f2); SEED=$(echo "$T" | cut -d_ -f3 | tr -d s)
  for try in 1 2; do
    ( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$B/logs/${T}_gpumem.csv"; sleep 30; done ) & SM=$!
    TASK=$T ARM=$ARM SEED=$SEED WORKERS=6 bash "$B/bin/fit_local.sh" >> "$B/logs/$T.log" 2>&1
    rc=$?; kill $SM 2>/dev/null || true
    echo "$rc" > "$B/rc/$T"; rm -rf "$B/work/$T"
    echo "$(date +%T) $T try $try rc $rc" >> "$B/queue.log"
    [ $rc -eq 0 ] && break
    grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$T non-finite: not rerun" >> "$B/queue.log"; break; }
  done
done
date > "$B/ALL_DONE"

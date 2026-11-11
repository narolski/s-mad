#!/bin/bash
# PN1 rented queue: the eight fits one after another through the unchanged run.sh (host Python), then the reference
# row (score_ref_local.sh). One result tar + .sha256 per task in /workspace/pn1/root/results/PN1/. A task that fails is
# rerun once unchanged (infrastructure rule); its work folder is removed after each task to keep the disk free.
set -u
B=/workspace/pn1
cd "$B"; date > "$B/QUEUE_STARTED"
mkdir -p "$B/logs" "$B/rc" "$B/tmp"
for T in PN1_A_s401 PN1_B_s401 PN1_Bn_s401 PN1_C_s401 PN1_A_s402 PN1_B_s402 PN1_Bn_s402 PN1_C_s402; do
  for try in 1 2; do
    W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
    ( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$B/logs/${T}_gpumem.csv"; sleep 30; done ) & SM=$!
    ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_LOCAL=1 PN1_PY=python \
      PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
    rc=$?; kill $SM 2>/dev/null || true
    echo "$rc" > "$B/rc/$T"; rm -rf "$W"
    echo "$(date +%T) $T try $try rc $rc" >> "$B/queue.log"
    [ $rc -eq 0 ] && break
    grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$T non-finite: not rerun" >> "$B/queue.log"; break; }
  done
done
for try in 1 2; do
  W=$B/work/ref; rm -rf "$W"; mkdir -p "$W"
  ( cd "$W" && TMPDIR=$B/tmp TASK_WORK="$W" bash "$B/bin/score_ref_local.sh" ) >> "$B/logs/PN1_REF_smdd_m3.log" 2>&1
  rc=$?; echo "$rc" > "$B/rc/PN1_REF_smdd_m3"; rm -rf "$W"
  echo "$(date +%T) REF try $try rc $rc" >> "$B/queue.log"
  [ $rc -eq 0 ] && break
done
date > "$B/ALL_DONE"

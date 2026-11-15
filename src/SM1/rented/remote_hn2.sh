#!/bin/bash
# SM1 A18 queue: smoke (200 steps, 64 rows) then 3 RS fits, one at a time; a failed fit is rerun once.
set -u
B=/workspace/sm1r; mkdir -p "$B/logs" "$B/rc"
S=$B/smoke_hn2; rm -rf "$S"; mkdir -p "$S"
TASK=HN2_RS_s401_smoke ARM=RS SEED=401 STEPS=200 LIMIT=64 RESULTS=$S bash "$B/bin/fit_hn2.sh" > "$B/logs/hn2_smoke.log" 2>&1
echo "smoke rc $?" | tee "$B/logs/hn2_smoke_rc.txt"
grep -q "HN2_TASK_DONE" "$B/logs/hn2_smoke.log" || { date > "$B/results_hn2_FAILED"; exit 1; }
for T in HN2_RS_s401 HN2_RS_s402 HN2_RS_s403; do
  ARM=$(echo "$T" | cut -d_ -f2); SEED=$(echo "$T" | cut -d_ -f3 | tr -d s)
  for try in 1 2; do
    TASK=$T ARM=$ARM SEED=$SEED bash "$B/bin/fit_hn2.sh" >> "$B/logs/$T.log" 2>&1
    rc=$?; echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_hn2.log"; rm -rf "$B/work/$T"
    [ $rc -eq 0 ] && break
    grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$T non-finite: not rerun" >> "$B/queue_hn2.log"; break; }
  done
done
date > "$B/results_hn2/HN2_ALL_DONE"

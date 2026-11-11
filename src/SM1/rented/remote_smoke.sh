#!/bin/bash
# SM1 rented smoke (A13): fit_local.sh on arm a seed 401, 200 steps, 64 scored rows per manifest, the full audit set;
# separate results folder; GPU memory sampled every 5 s.
set -uo pipefail
B=/workspace/sm1r; S=$B/smoke; rm -rf "$S"; mkdir -p "$S"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$S/gpumem.csv"; sleep 5; done ) & SM=$!
TASK=SM1B_a_s401_rsmoke ARM=a SEED=401 STEPS=200 LIMIT=64 WORKERS=6 RESULTS=$S bash "$B/bin/fit_local.sh" > "$S/smoke_run.log" 2>&1
rc=$?
kill $SM 2>/dev/null || true
rm -rf "$B/work/SM1B_a_s401_rsmoke"
grep -E "it/s|SM1R trained|SM1A check|SM1A_DONE|SM1R_TASK_DONE|FAIL|Error" "$S/smoke_run.log" | tail -12 | cut -c1-220
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$S/gpumem.csv"
echo "SMOKE_RC=$rc"

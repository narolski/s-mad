#!/bin/bash
# PN1 rented smoke: the unchanged run.sh on arm Bn, 200 steps, 64 scored rows, separate results root; GPU memory sampled.
set -uo pipefail
B=/workspace/pn1
S=$B/smoke; rm -rf "$S"; mkdir -p "$S/root/results" "$S/work" "$S/task" "$B/tmp"
cp "$B/tasks/PN1_Bn_s401/run.sh" "$S/task/run.sh"; printf 'TASK=PN1_Bn_s401_smoke\nARM=Bn\nSEED=401\n' > "$S/task/task.env"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$S/gpumem.csv"; sleep 5; done ) & SM=$!
( cd "$S/work" && TMPDIR=$B/tmp TASK_DIR="$S/task" TASK_WORK="$S/work" PN1_ROOT="$S/root" PN1_PACK="$B/root/packs/PN1/pn1_pack.tar" \
  PN1_LOCAL=1 PN1_PY=python PN1_STEPS=200 PN1_LIMIT=64 PN1_WORKERS=7 bash "$S/task/run.sh" ) > "$S/smoke_run.log" 2>&1
rc=$?
kill $SM 2>/dev/null || true
rm -rf "$S/work/pn1" "$S/work/data"
grep -E "step +[0-9]+/|PN1_TASK_DONE|FAIL|trained" "$S/smoke_run.log" | cut -c1-200
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$S/gpumem.csv"
echo "SMOKE_RC=$rc"

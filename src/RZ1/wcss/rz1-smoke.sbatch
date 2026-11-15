#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J rz1-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/rz1-smoke-%j.out
# RZ1 WCSS smoke (the run path differs from AB1's: TT1 and MEDS packs, cv2 kernels, RZ1 scripts, 512 input). Owner: RZ1 owner.
# (1) arm SbMR seed 408, 100 steps, full scoring (all rows, 9-kernel cross table): step rate and scoring time;
# (2) arm Sb512 seed 408, 30 steps at batch 64 x 4, 64 scoring rows, without TT1/MEDS: the 512 guard, memory, step rate.
# Results to results/RZ1_smoke; decides nothing about any hypothesis.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/RZ1
[ "$(sha256sum "$P/run_rz1.sh" | cut -c1-64)" = dc5d0838277721df004f46950fe29ee79495892c3dcc8e1b7f78a188cc01abdc ] || { echo "RZ1 FAIL run_rz1.sh pin"; exit 1; }
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
for spec in "SbMR 100 0 " "Sb512 30 64 1"; do
  set -- $spec; ARM=$1; ST=$2; LIM=$3; SK=${4:-}
  TD=$TMPDIR/td_$ARM; W=$TMPDIR/w_$ARM; mkdir -p "$TD" "$W"
  printf 'TASK=RZ1smoke_%s_s408\nARM=%s\nSEED=408\n' "$ARM" "$ARM" > "$TD/task.env"
  ( while sleep 60; do nvidia-smi --query-gpu=memory.used --format=csv,noheader; done ) > "$TMPDIR/mem_$ARM.log" 2>&1 &
  MP=$!
  TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 PN1_STEPS=$ST PN1_LIMIT=$LIM     RZ1_SKIP_TT1=$SK RZ1_RESULTS=$L/results/RZ1_smoke bash "$P/run_rz1.sh"
  kill $MP || true
  echo "RZ1 smoke $ARM peak memory MiB: $(sort -n "$TMPDIR/mem_$ARM.log" | tail -1)"
  rm -rf "$W"
done
echo "RZ1_SMOKE_DONE $(date -Is)"

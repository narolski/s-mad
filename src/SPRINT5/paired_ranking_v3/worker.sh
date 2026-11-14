#!/bin/bash
# Runs inside an actual allocation, never on a login node.
set -euo pipefail
: "${TMPDIR:?}" "${SLURM_JOB_ID:?real allocation required}"
MODE=${1:?smoke or production}
G=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$G/packs/SPRINT5_1_v3
export PN1_ROOT=$G PN1_PY=$HOME/dmenv/bin/python
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
[ "$MODE" = smoke ] || [ "$MODE" = production ]
LOG=$G/results/SPRINT5_1/logs
mkdir -p "$LOG"
exec > >(tee "$LOG/worker_${MODE}_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID:-none}.log") 2>&1
cp -r "$P/source" "$TMPDIR/sprint_source"
export SPRINT_SOURCE=$TMPDIR/sprint_source
(cd "$SPRINT_SOURCE" && sha256sum -c --quiet SHA256SUMS)
export SPRINT_MODE=$MODE
if [ "$MODE" = smoke ]; then
  export PN1_STEPS=2 PN1_LIMIT=0 SPRINT_RESULTS=$G/results/SPRINT5_1/smoke_v3
  SEED=501
  ARMS=(bce paired_bce paired_rank)
else
  : "${SLURM_ARRAY_TASK_ID:?}"
  export SPRINT_REVIEW_RECEIPT=$P/PRODUCTION_RELEASE.json
  "$PN1_PY" "$SPRINT_SOURCE/verify_release.py" "$SPRINT_REVIEW_RECEIPT" "$SPRINT_SOURCE"
  I=$SLURM_ARRAY_TASK_ID
  [ "$I" -ge 0 ] && [ "$I" -lt 15 ]
  SEED=$((501+I/3))
  ALL_ARMS=(bce paired_bce paired_rank)
  ARMS=("${ALL_ARMS[$((I%3))]}")
  export SPRINT_RESULTS=$G/results/SPRINT5_1/production_v3
fi
for ARM in "${ARMS[@]}"; do
  TASK=SPRINT5_1_${MODE}_v3_${ARM}_s${SEED}
  TD=$TMPDIR/task_$ARM; W=$TMPDIR/work_$ARM
  mkdir -p "$TD" "$W"
  printf 'TASK=%s\nARM=%s\nSEED=%s\n' "$TASK" "$ARM" "$SEED" > "$TD/task.env"
  TASK_DIR=$TD TASK_WORK=$W bash "$SPRINT_SOURCE/run.sh"
done
printf 'SPRINT5_WORKER_DONE mode=%s job=%s\n' "$MODE" "$SLURM_JOB_ID"

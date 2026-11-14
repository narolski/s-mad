#!/bin/bash
set -euo pipefail
: "${TMPDIR:?}" "${SLURM_JOB_ID:?}"
MODE=${1:?smoke or pilot}
G=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$G/packs/SPRINT5_4_v1
export PN1_ROOT=$G PN1_PY=$HOME/dmenv/bin/python
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
mkdir -p "$G/results/SPRINT5_4/logs"
exec > >(tee "$G/results/SPRINT5_4/logs/${MODE}_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID:-none}.log") 2>&1
cp -r "$P/source" "$TMPDIR/breadth_source"
export SPRINT_SOURCE=$TMPDIR/breadth_source SPRINT_MODE=$MODE
(cd "$SPRINT_SOURCE" && sha256sum -c --quiet SHA256SUMS)
export SPRINT_REVIEW_RECEIPT=$P/${MODE^^}_RELEASE.json
"$PN1_PY" "$SPRINT_SOURCE/verify_release.py" "$SPRINT_REVIEW_RECEIPT" "$SPRINT_SOURCE" "$MODE"
ALL_ARMS=(narrow_more_variants broad_fewer_variants)
if [ "$MODE" = smoke ]; then
  export PN1_STEPS=2 PN1_LIMIT=0 SPRINT_RESULTS=$G/results/SPRINT5_4/smoke_v1
  SEED=511; ARMS=("${ALL_ARMS[@]}")
elif [ "$MODE" = pilot ]; then
  : "${SLURM_ARRAY_TASK_ID:?}"
  I=$SLURM_ARRAY_TASK_ID; [ "$I" -ge 0 ] && [ "$I" -lt 10 ]
  SEED=$((511+I/2)); ARMS=("${ALL_ARMS[$((I%2))]}")
  export PN1_STEPS=100 PN1_LIMIT=0 SPRINT_RESULTS=$G/results/SPRINT5_4/pilot_v1
else exit 1; fi
for ARM in "${ARMS[@]}"; do
  TASK=SPRINT5_4_${MODE}_v1_${ARM}_s${SEED}
  TD=$TMPDIR/task_$ARM;W=$TMPDIR/work_$ARM;mkdir -p "$TD" "$W"
  printf 'TASK=%s\nARM=%s\nSEED=%s\n' "$TASK" "$ARM" "$SEED" > "$TD/task.env"
  TASK_DIR=$TD TASK_WORK=$W bash "$SPRINT_SOURCE/run.sh"
done
echo "SPRINT5_4_WORKER_DONE mode=$MODE job=$SLURM_JOB_ID"

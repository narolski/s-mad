#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-cpu-short
#SBATCH --no-requeue
# Runs one staged CPU task (a directory with run.sh) with all work in node-local scratch.
set -uo pipefail
: "${TASK_DIR:?task directory required}" "${TMPDIR:?local scratch required}"
W="$TMPDIR/work"; mkdir -p "$W"; cd "$W"
echo "$(date +%FT%T) cpu task $(basename "$TASK_DIR") on $(hostname) cpus=${SLURM_CPUS_PER_TASK:-?}"
TASK_DIR="$TASK_DIR" TASK_WORK="$W" bash "$TASK_DIR/run.sh"; rc=$?
echo "$rc" > "$TASK_DIR/rc"; echo "$(date +%FT%T) rc=$rc"
exit $rc

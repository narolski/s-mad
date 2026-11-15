#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=06:00:00
#SBATCH --job-name=smadnext-slot
# A slot is a generic one-GPU job. When it starts it takes ready tasks from a queue
# directory, one after another, until none is left or too little time remains.
# A task is a directory in $Q/ready holding run.sh and est_minutes (an integer).
# Claiming is an atomic rename. All task IO must go through $TMPDIR.
set -u
# RETIRED 12 Nov 2026 (lead, on the author's instruction). Slots hold a GPU while they wait for work that is placed
# later. On 12 Nov, 108 slots started while WCSS could not be reached, found an empty queue and idled for about
# 69 H100 GPU-hours. Do not submit this script. Every job must carry its own workload (see OWNER_BRIEF.md).
echo "slot.sh is retired: submit jobs that carry their own workload (OWNER_BRIEF.md, 12 Nov 2026)" >&2; exit 64
Q="${SMADNEXT_QUEUE:?queue directory required}"
LIMIT_S="${SMADNEXT_LIMIT_S:-21600}"      # must match --time
IDLE_WAIT_S="${SMADNEXT_IDLE_WAIT_S:-1800}" # how long an empty slot waits for a task
MARGIN_S=900
START=$(date +%s)
ME="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}_${SLURM_ARRAY_TASK_ID:-0}"
: "${TMPDIR:?local scratch required}"
mkdir -p "$Q/ready" "$Q/claimed" "$Q/done" "$Q/failed" "$Q/slotlog"
log(){ echo "$(date +%FT%T) $ME $*" | tee -a "$Q/slotlog/$ME.log"; }
left(){ echo $(( LIMIT_S - ( $(date +%s) - START ) )); }
log "slot start host=$(hostname) limit=${LIMIT_S}s"
idle_since=$(date +%s); ran=0
while :; do
  claimed=""
  for t in $(ls "$Q/ready" 2>/dev/null | sort); do
    est=$(cat "$Q/ready/$t/est_minutes" 2>/dev/null || echo 0)
    [ "$est" -gt 0 ] || continue
    [ $(( est*60 + MARGIN_S )) -le "$(left)" ] || continue
    if mv "$Q/ready/$t" "$Q/claimed/$t" 2>/dev/null; then claimed="$t"; break; fi
  done
  if [ -z "$claimed" ]; then
    if [ $(( $(date +%s) - idle_since )) -ge "$IDLE_WAIT_S" ]; then log "no runnable task for ${IDLE_WAIT_S}s; exit"; break; fi
    [ "$(left)" -gt $(( MARGIN_S + 120 )) ] || { log "out of time; exit"; break; }
    sleep "${SMADNEXT_POLL_S:-60}"; continue
  fi
  T="$Q/claimed/$claimed"; echo "$ME $(hostname) $(date +%FT%T)" > "$T/claimed_by"
  W="$TMPDIR/task_$claimed"; mkdir -p "$W"
  log "run $claimed (est $(cat "$T/est_minutes") min, left $(left)s)"
  ( cd "$W" && TASK_DIR="$T" TASK_WORK="$W" bash "$T/run.sh" ) > "$W/stdout.log" 2>&1; rc=$?
  tail -c 200000 "$W/stdout.log" > "$T/stdout.tail.log"; echo "$rc" > "$T/rc"
  if [ "$rc" -eq 0 ]; then mv "$T" "$Q/done/$claimed"; else mv "$T" "$Q/failed/$claimed"; fi
  log "end $claimed rc=$rc"
  rm -rf "$W"; ran=$((ran+1)); idle_since=$(date +%s)
done
log "slot end ran=$ran"

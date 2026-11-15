#!/bin/bash
# Lead-side watcher (runs on the DGX). Slurm on Athena refused both grant accounts on 11 Nov 2026 17:20
# ("Invalid account or account/partition combination": no Slurm association for the user yet, although
# hpc-grants lists both grants). Every INTERVAL seconds, in one short connection under the Athena lock, this asks
# Slurm with --test-only (creates no job) whether an account is accepted; on the first acceptance it submits the
# environment build and smoke test with that account and exits. plgrestorearc is preferred; plgmultivision is the
# author's fallback. Usage: wait_and_submit_smoke.sh [TRIES=9] [INTERVAL=1200]
set -u
TRIES=${1:-9}; INTERVAL=${2:-1200}
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
for i in $(seq 1 "$TRIES"); do
  out=$(flock -w 300 /tmp/smadnext-athena.lock timeout 120 ssh -o BatchMode=yes -o ConnectTimeout=15 plgpnarolski@athena.cyfronet.pl "bash -lc '
    for A in plgrestorearc-gpu-a100 plgmultivision-gpu-a100; do
      if sbatch --test-only -A \$A -p plgrid-gpu-a100 -N1 -c 8 --mem=64G --gres=gpu:1 -t 10 --wrap true >/dev/null 2>&1; then
        cd $G && J=\$(sbatch --parsable -A \$A src/athena/env_and_smoke.sbatch) && echo \"SUBMITTED account=\$A job=\$J\"; exit 0
      fi
    done; echo NOT_YET'" 2>&1)
  rc=$?
  echo "$(date +%T) try $i: ${out:-no output} (ssh rc $rc)"
  case "$out" in *SUBMITTED*) exit 0 ;; esac
  # a refused or failed connection is never retried quickly: stop and leave it to the lead
  if [ $rc -ne 0 ] && [ -z "$out" ]; then echo "connection failed; stopping without retry"; exit 2; fi
  [ "$i" -lt "$TRIES" ] && sleep "$INTERVAL"
done
echo "$(date +%T) no account accepted after $TRIES tries"; exit 1

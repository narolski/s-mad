#!/bin/bash
set -euo pipefail
export PATH=/usr/bin:/bin LANG=C LC_ALL=C
SEED=${1:?}; case "$SEED" in 401|402|403|404|405) ;; *) exit 2;; esac
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
J=$L/dispatch/ad5_full_math_v2_20261114/s$SEED
: "${SLURM_JOB_ID:?}"
set -C
printf '%s\n' "$SLURM_JOB_ID" > "$J/NATIVE_JOB_ID.txt"
sync -f "$J/NATIVE_JOB_ID.txt"
# Query THIS native allocation only; no guessed age from node-entry wall clock.
/opt/slurm/current/bin/scontrol show job "$SLURM_JOB_ID" -o > "$J/NATIVE_ALLOCATION.txt"
sync -f "$J/NATIVE_ALLOCATION.txt"
exec python3 -I "$L/ad5_full_math_v2/node.py" "$SEED"

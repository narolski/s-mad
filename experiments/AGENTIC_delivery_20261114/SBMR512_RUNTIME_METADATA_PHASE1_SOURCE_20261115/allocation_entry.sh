#!/bin/bash
set -euo pipefail
umask 077
B=/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/sbmr512_runtime_metadata_phase1_v1
: "${SLURM_JOB_ID:?native allocation required}"
set -C
printf '%s\n' "$SLURM_JOB_ID" > "$B/dispatch_s408/NATIVE_JOB_ID.txt"
sync -f "$B/dispatch_s408/NATIVE_JOB_ID.txt"
printf 'SBMR512_RUNTIME_PHASE1_NATIVE_JOB_ID=%s\n' "$SLURM_JOB_ID"
exec "$3" -I -S -B "$B/source/node_driver.py" "$1" "$2"

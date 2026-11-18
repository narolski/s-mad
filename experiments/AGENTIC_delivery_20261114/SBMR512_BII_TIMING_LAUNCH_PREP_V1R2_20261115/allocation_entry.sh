#!/bin/bash
# Shell receipt comes BEFORE any Python/source/hash/runtime failure.
set -euo pipefail
umask 077
J=/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/SbMR512_bii_timing_wcss_v1/dispatch_s408
SRC=/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/SbMR512_bii_timing_wcss_v1/source
: "${SLURM_JOB_ID:?native allocation required}"
set -C
printf '%s\n' "$SLURM_JOB_ID" > "$J/NATIVE_JOB_ID.txt"
sync -f "$J/NATIVE_JOB_ID.txt"
printf 'SBMR512_BII_TIMING_NATIVE_JOB_ID=%s\n' "$SLURM_JOB_ID"
exec "$3" -I -S -B "$SRC/node_driver.py" "$1" "$2"

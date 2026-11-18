#!/bin/bash
# Earliest allocation receipt, before Python startup/source checks/worker can fail.
set -euo pipefail
J=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/dispatch/ad5_real_math_multi_v1_20261114
: "${SLURM_JOB_ID:?native allocation required}"
set -C
printf '%s\n' "$SLURM_JOB_ID" > "$J/NATIVE_JOB_ID.txt"
sync -f "$J/NATIVE_JOB_ID.txt"
printf 'AD5_REAL_MATH_STEP_NATIVE_JOB_ID=%s\n' "$SLURM_JOB_ID"
exec python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_real_math_multi_v1/node.py

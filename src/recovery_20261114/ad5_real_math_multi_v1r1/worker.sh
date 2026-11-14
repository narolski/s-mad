#!/bin/bash
# R1 control-plane wrapper; body/training computation unchanged.
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5
SRC=$L/ad5_real_math_multi_v1r1
KEEP=$L/logs/keep/ad5_real_math_multi_v1r1_20261114
J=$L/dispatch/ad5_real_math_multi_v1r1_20261114
: "${TMPDIR:?}" "${SLURM_JOB_ID:?}"
case "$TMPDIR" in /mnt/lscratch/*) ;; *) exit 2;; esac
python3 -I -c "import sys;sys.path.insert(0,'$SRC');import verify;verify.release()"
mkdir "$KEEP"
mkdir "$KEEP/technical" "$KEEP/original_run"
sync -f "$KEEP"
exec python3 -I "$SRC/supervise.py" --keep "$KEEP" --local-run "$TMPDIR/ad5_real_math_multi_v1r1/run" --allocation-start-file "$J/NATIVE_ALLOCATION_EPOCH.txt" --max-seconds 720 --term-grace 10 --collection-seconds 60 -- /bin/bash "$SRC/body.sh"

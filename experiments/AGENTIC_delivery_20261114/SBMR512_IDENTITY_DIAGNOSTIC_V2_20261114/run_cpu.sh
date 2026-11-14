#!/bin/bash
# CPU metadata acquisition only; requires OTHER review and explicit root grant.
set -euo pipefail
BOOTSTRAP=${1:?canonical pinned bootstrap interpreter}
RELEASE=${2:?exact root metadata grant}
HERE=$(cd -- "$(dirname -- "$0")" && pwd -P)
D=/lustre/pd03/hpc-narolski-1790461090/smad-next/coordination_20261114/sbmr512_identity_diagnostic_dispatch_v2
umask 077
mkdir "$D"
printf '%s\n' 'ROOT_RELEASE_REQUIRED_NO_AUTOMATIC_RETRY' > "$D/INTENT.txt"
sync -f "$D/INTENT.txt"
ulimit -v 524288
set +e
env -i PATH=/usr/bin:/bin LANG=C LC_ALL=C CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 /usr/bin/timeout --signal=TERM --kill-after=10s 120s "$BOOTSTRAP" -I -S -B "$HERE/acquire.py" --release "$RELEASE" > "$D/stdout.log" 2> "$D/stderr.log"
RC=$?
set -e
printf '{"exit_code":%s,"scope":"SOURCE_INSTALL_METADATA_ONLY","scientific_read":"HOLD","automatic_retry":false}\n' "$RC" > "$D/EXECUTION.json"
sync -f "$D/EXECUTION.json"
sync -f "$D/stdout.log"
sync -f "$D/stderr.log"
exit "$RC"

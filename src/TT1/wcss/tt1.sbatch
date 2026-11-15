#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:100G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=02:00:00
#SBATCH --job-name=tt1-score
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/tt1-%j.out
# Owner: owner of the threshold-transfer experiment (TT1), registration TT1-S (commit 01557ce). Workload, all on Lustre
# before submission: smad-next/packs/TT1/{tt1_pack.tar, tt1_nets_s401402.tar, tt1_job.sh} (+ .sha256), smadcvpr/packs/pylib*.
# Submit with --export=ALL,TT1_MODE=test (8 gate rows per network) or TT1_MODE=full (gate, then TT1 rows).
set -euo pipefail
: "${TMPDIR:?local scratch required}" "${TT1_MODE:?}"
B=/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/TT1
JSHA=$(cut -c1-64 "$B/tt1_job.sh.sha256")
[ "$(sha256sum "$B/tt1_job.sh" | cut -c1-64)" = "$JSHA" ] || { echo "TT1 FAIL: tt1_job.sh sha256"; exit 1; }
cp "$B/tt1_job.sh" "$TMPDIR/tt1_job.sh"
TT1_NETS=s401402 \
TT1_PACK_SHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554 \
TT1_NETS_SHA=92bd1841bd9307659c4666bfc344974592613e310f2ee4187dc3fc6884205303 \
  bash "$TMPDIR/tt1_job.sh"

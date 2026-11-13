#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J rz1-rescore
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-02:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/rz1-rescore-%j.out
# RZ1 amendment 1: rescore AB1's kept A and Sb networks (seeds 408-412; results/AB1, sha256-pinned in run_rz1r.sh) with the
# RZ1 scorer on WCSS H100 / ~/dmenv (read-only), after a bit-identity gate against AB1's stored logits. One job, ten
# networks in sequence, about 5-8 min each after about 4 min of input copy. Owner: RZ1 owner. Results: results/RZ1R.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/RZ1
[ "$(sha256sum "$P/run_rz1r.sh" | cut -c1-64)" = f9340251d57b6eb91cfe18b53f11ed875f2ccddcc2d423ee6b00eff22d000c8d ] || { echo "RZ1R FAIL run_rz1r.sh pin"; exit 1; }
W=$TMPDIR/w; mkdir -p "$W"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_rz1r.sh"

#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1b2-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:15:00
#SBATCH --array=0-24
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1b2-fit-%A_%a.out
# AB1 follow-up batch B2 (registration experiments/AB1_protocol-ablation-and-replication/prereg_b2.md, pre-run check
# PRERUN_AB1B2_20261113.md; lead's go under the author's standing instruction for 13 Nov): 25 fits, arms SbH61, SbSp, SbnS0, SbnS3, SbR at seeds 408-412, seed by seed;
# src/AB1/run_b2.sh (on Lustre as packs/AB1/run_b2.sh, pinned here) on the FS1 pack + packs/AB1/ab1b2_overlay.tar
# (pinned here and in run_b2.sh). SbL (Sb twice as long) runs separately with ab1_long.sbatch (unchanged).
# Owner: AB1 owner (Claude agent for the lead). All IO in $TMPDIR; one tar per fit to results/AB1B2.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(SbH61 SbSp SbnS0 SbnS3 SbR SbH61 SbSp SbnS0 SbnS3 SbR SbH61 SbSp SbnS0 SbnS3 SbR SbH61 SbSp SbnS0 SbnS3 SbR SbH61 SbSp SbnS0 SbnS3 SbR)
SEEDS=(408 408 408 408 408 409 409 409 409 409 410 410 410 410 410 411 411 411 411 411 412 412 412 412 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_b2.sh" | cut -c1-64)" = 5e8df7d2bb4b191f8bec206b3d6fca4046c4312f93f2eaffcab4e1d4147244e9 ] || { echo "AB1 FAIL run_b2.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1b2_overlay.tar" | cut -c1-64)" = d2038b98af8b4d835091f80c7034c41bb7dce1a16fab8781e65c44abaabedc5e ] || { echo "AB1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1B2_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_b2.sh"
echo "AB1 fit end $ARM $SEED $(date -Is)"

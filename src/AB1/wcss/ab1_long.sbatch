#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1-long
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-04:00:00
#SBATCH --array=0-4
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1-long-%A_%a.out
# Protocol ablation and replication (AB1), prereg section 6: CONDITIONAL arm SbL (Sb manifest, 12,500 steps), seeds
# 408-412. Submitted ONLY if the lead says that the training-row read (owner PR1, part Z1) shows underfit.
# src/AB1/run.sh v2 (on Lustre as run_v2.sh, cfa4ed26..., pinned here) on the FS1 pack (packs/BB2/pn1_pack_fs.tar,
# 96c31ae2...) + the AB1 overlay v2 (packs/AB1/ab1_overlay_v2.tar, 171fdb21..., pinned here and in run_v2.sh). Owner: AB1 owner (Claude agent for the
# lead). All IO in $TMPDIR; one result tar per fit to results/AB1. A task whose verified tar exists exits at once; a
# missing or mismatched input fails within a minute.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(SbL SbL SbL SbL SbL)
SEEDS=(408 409 410 411 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_v2.sh" | cut -c1-64)" = cfa4ed26d747e1d50f66cfc2af823ed55fd7f31634d6285cff9363a5fa796ab4 ] || { echo "AB1 FAIL run_v2.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1_overlay_v2.tar" | cut -c1-64)" = 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 ] || { echo "AB1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 long fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_v2.sh"
echo "AB1 long fit end $ARM $SEED $(date -Is)"

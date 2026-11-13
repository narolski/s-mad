#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J rz1-512
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-09:00:00
#SBATCH --array=0-14
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/rz1-512-%A_%a.out
# Input resolution and resize method (RZ1), wave 2b (512 px input, position embedding resampled 14x14 -> 32x32, batch 64 x 4): 15 fits, arms A512 Sb512 SbMR512 at seeds 408-412. Owner: RZ1 owner (Claude agent for the lead).
# src/RZ1/run_rz1.sh (packs/RZ1/run_rz1.sh, pinned here) on the FS1 pack + AB1 overlays + TT1 + MEDS packs + RZ1 overlay
# (all pinned in run_rz1.sh; the RZ1 overlay also here). All IO in $TMPDIR; one result tar per fit to results/RZ1.
# A task whose verified tar exists exits at once; a missing or mismatched input fails within a few minutes.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/RZ1
ARMS=(A512 Sb512 SbMR512)
SEEDS=(408 409 410 411 412)
I=$SLURM_ARRAY_TASK_ID
NA=${#ARMS[@]}
ARM=${ARMS[$((I % NA))]}; SEED=${SEEDS[$((I / NA))]}
[ "$(sha256sum "$P/run_rz1.sh" | cut -c1-64)" = dc5d0838277721df004f46950fe29ee79495892c3dcc8e1b7f78a188cc01abdc ] || { echo "RZ1 FAIL run_rz1.sh pin"; exit 1; }
[ "$(sha256sum "$P/rz1_overlay.tar" | cut -c1-64)" = dccf37d20ca0074780a15d99012c3302f52e4ad5a7773b66981b5d316276d383 ] || { echo "RZ1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=RZ1_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "RZ1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_rz1.sh"
echo "RZ1 fit end $ARM $SEED $(date -Is)"

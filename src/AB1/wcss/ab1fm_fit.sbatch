#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1fm-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:15:00
#SBATCH --array=0-4
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1fm-fit-%A_%a.out
# AB1 second-engine arm SbFM (prereg_fm.md): 5 fits at seeds 408-412; src/AB1/run_fm.sh (packs/AB1/run_fm.sh, pinned
# here) on the FS1 pack + packs/AB1/ab1fm_overlay.tar (pinned here and in run_fm.sh). Owner: AB1 owner (Claude agent for
# the lead). All IO in $TMPDIR; one tar per fit to results/AB1FM. A task whose verified tar exists exits at once.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(SbFM SbFM SbFM SbFM SbFM)
SEEDS=(408 409 410 411 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_fm.sh" | cut -c1-64)" = 9c04e3bd637111f38340a1ab385e05355a55db00d49295e45a3343ff3b32d7ea ] || { echo "AB1 FAIL run_fm.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1fm_overlay.tar" | cut -c1-64)" = 681525d8a7f11194dc35822dc9b5c77e936a0bd501313b6aedf292e21fd1b74d ] || { echo "AB1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1FM_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_fm.sh"
echo "AB1 fit end $ARM $SEED $(date -Is)"

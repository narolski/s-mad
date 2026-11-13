#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1x-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:15:00
#SBATCH --array=0-4
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1x-fit-%A_%a.out
# AB1 border-crossed arm Sbx (prereg_x.md): 5 fits at seeds 408-412; src/AB1/run_x.sh (packs/AB1/run_x.sh, pinned here)
# on the FS1 pack + packs/AB1/ab1x_overlay.tar (pinned here and in run_x.sh). Owner: AB1 owner (Claude agent for the
# lead). All IO in $TMPDIR; one tar per fit to results/AB1X. A task whose verified tar exists exits at once.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(Sbx Sbx Sbx Sbx Sbx)
SEEDS=(408 409 410 411 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_x.sh" | cut -c1-64)" = 0051ba1fc27f08ab1068c6282dbdc7c11c55d33f9d5df195d430d8e2833a405c ] || { echo "AB1 FAIL run_x.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1x_overlay.tar" | cut -c1-64)" = e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c ] || { echo "AB1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1X_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_x.sh"
echo "AB1 fit end $ARM $SEED $(date -Is)"

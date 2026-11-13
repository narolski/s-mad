#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1c-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:15:00
#SBATCH --array=0-9
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1c-fit-%A_%a.out
# AB1 batch C (prereg.md amendment 7): 10 fits, arms SpV and BN at seeds 408-412, seed by seed; src/AB1/run_c.sh
# (packs/AB1/run_c.sh, pinned here) on the FS1 pack + packs/AB1/ab1c_overlay.tar (pinned here and in run_c.sh).
# Post-freeze ablation rows. Owner: AB1 owner. All IO in $TMPDIR; one tar per fit to results/AB1C.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(SpV BN SpV BN SpV BN SpV BN SpV BN)
SEEDS=(408 408 409 409 410 410 411 411 412 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_c.sh" | cut -c1-64)" = 7da6688ad6cd5fa7b1305ebbb2218491a4c6efa32f944c8210cb9c6d55779b4d ] || { echo "AB1 FAIL run_c.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1c_overlay.tar" | cut -c1-64)" = 62712bb9d5066443d5737c84da852d055ab248930d5f38fc8b77ba0074a34c68 ] || { echo "AB1 FAIL overlay pin"; exit 1; }
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1C_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_c.sh"
echo "AB1 fit end $ARM $SEED $(date -Is)"

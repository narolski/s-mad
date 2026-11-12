#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ms1-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:60G
#SBATCH --no-requeue
#SBATCH --time=0-03:00:00
#SBATCH --array=0-9
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ms1-fit-%A_%a.out
# MS1 training comparison (prereg part 2): one fit per array task, arms Sb and SbM3 at seeds 403-407, the unchanged
# PN1 recipe through run.sh (MS1 copy, sha256 in run.sh.sha256), pack pn1_pack_ms1.tar (sha256 checked by run.sh).
# All IO in $TMPDIR; one result tar per fit to results/MS1. A task whose verified tar exists exits at once.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/MS1
ARMS=(Sb SbM3 Sb SbM3 Sb SbM3 Sb SbM3 Sb SbM3)
SEEDS=(403 403 404 404 405 405 406 406 407 407)
ARM=${ARMS[$SLURM_ARRAY_TASK_ID]}; SEED=${SEEDS[$SLURM_ARRAY_TASK_ID]}
(cd "$P" && sha256sum -c --quiet run.sh.sha256)
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=MS1_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "MS1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_ms1.tar MS1_RESULTS=$L/results/MS1 \
  PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run.sh"
echo "MS1 fit end $ARM $SEED $(date -Is)"

#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-05:00:00
#SBATCH --array=0-8%5
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-fit-%A_%a.out
# Second backbone (BB2), prereg sections 3-4: nine fits (arms A, B, Sb at seeds 403, 404, 405), one per array task, seed by
# seed, at most 5 GPUs at once; src/BB2/run.sh (sha256 in run.sh.sha256) on the FS1 pack + BB2 overlay (both sha256-checked
# by run.sh). Batch rule from the smoke: BB2_BS / BB2_ACCUM below. All IO in $TMPDIR; one result tar per fit to
# results/BB2. A task whose verified tar exists exits at once; a missing pack or script exits within a minute.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2
ARMS=(A B Sb A B Sb A B Sb)
SEEDS=(403 403 403 404 404 404 405 405 405)
BB2_BS=__BS__; BB2_ACCUM=__ACCUM__
ARM=${ARMS[$SLURM_ARRAY_TASK_ID]}; SEED=${SEEDS[$SLURM_ARRAY_TASK_ID]}
(cd "$P" && sha256sum -c --quiet run.sh.sha256)
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=BB2_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "BB2 fit $ARM $SEED bs $BB2_BS accum $BB2_ACCUM job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_fs.tar BB2_OVERLAY=$P/bb2_overlay.tar BB2_RESULTS=$L/results/BB2 \
  BB2_BS=$BB2_BS BB2_ACCUM=$BB2_ACCUM PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run.sh"
echo "BB2 fit end $ARM $SEED $(date -Is)"

#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J se1-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-03:00:00
#SBATCH --array=0-14
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/se1-fit-%A_%a.out
# Seam-shortcut training arm (SE1), prereg section 5: fifteen fits, arms A, Sb, SE at seeds 408-412, one per array
# task, seed by seed. src/SE1/run.sh (sha256 in run.sh.sha256) on the FS1 pack (packs/BB2/pn1_pack_fs.tar, 96c31ae2...)
# + the SE1 overlay (packs/SE1/se1_overlay.tar), both sha256-checked by run.sh. Owner: SE1 owner (Claude agent for the
# lead). All IO in $TMPDIR; one result tar per fit to results/SE1. A task whose verified tar exists exits at once; a
# missing or mismatched input fails within a minute.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/SE1
ARMS=(A Sb SE A Sb SE A Sb SE A Sb SE A Sb SE)
SEEDS=(408 408 408 409 409 409 410 410 410 411 411 411 412 412 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run.sh" | cut -c1-64)" = b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb ] || { echo "SE1 FAIL run.sh not at its registered pin"; exit 1; }
(cd "$P" && sha256sum -c --quiet run.sh.sha256 se1_overlay.tar.sha256)
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=SE1_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "SE1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L SE1_OVERLAY=$P/se1_overlay.tar SE1_OVERLAY_SHA=de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c \
  PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run.sh"
echo "SE1 fit end $ARM $SEED $(date -Is)"

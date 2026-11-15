#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1c-fit2
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:15:00
#SBATCH --array=0-14
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1c-fit-%A_%a.out
# AB1 batch C (prereg.md amendments 7, 7b): 15 fits, arms SpV, BN and BV at seeds 408-412, seed by seed; src/AB1/run_c.sh
# (packs/AB1/run_c.sh, pinned here) on the FS1 pack + packs/AB1/ab1c_overlay.tar (pinned here and in run_c.sh).
# Post-freeze ablation rows. Owner: AB1 owner. All IO in $TMPDIR; one tar per fit to results/AB1C.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1
ARMS=(SpV BN BV SpV BN BV SpV BN BV SpV BN BV SpV BN BV)
SEEDS=(408 408 408 409 409 409 410 410 410 411 411 411 412 412 412)
I=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run_c.sh" | cut -c1-64)" = 219ae9b00fadeaf85c361e7aa8ba7c89755b2dc83a2260d7518bee4cbb53df65 ] || { echo "AB1 FAIL run_c.sh pin"; exit 1; }   # review F8
[ "$(sha256sum "$P/ab1c_overlay.tar" | cut -c1-64)" = bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7 ] || { echo "AB1 FAIL overlay pin"; exit 1; }
[ "$(sha256sum "$P/preflight.py" | cut -c1-64)" = 6d3cf313f02bf09faae1a2465647709c939662d06458072c4ea2b12101756695 ] || { echo "AB1 FAIL preflight.py pin"; exit 1; }
$HOME/dmenv/bin/python "$P/preflight.py" --pack "$L/packs/BB2/pn1_pack_fs.tar" --overlay "$P/ab1c_overlay.tar" --eval ab1_eval.csv --train "train_$ARM.csv" || { echo "AB1 PREFLIGHT FAILED: no training started"; exit 1; }   # amendment 8
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=AB1C_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "AB1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_c.sh"
echo "AB1 fit end $ARM $SEED $(date -Is)"

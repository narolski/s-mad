#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J gx1-gen
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:40G
#SBATCH --no-requeue
#SBATCH --time=0-03:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/gx1-gen-%A_%a.out
# GAN morphs in training (GX1), generation: one array task = one shard named by line (task id + 1) of the list file
# given as argument (packs/GX1/<list>). Owner: AG1 owner (Claude agent for the lead). Runs gx1_gen_task.sh (pinned).
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next; P=$L/packs/GX1
LIST=${1:?list}
[ "$(sha256sum "$P/gx1_gen_task.sh" | cut -c1-64)" = "$(awk '$2=="gx1_gen_task.sh"{print $1}' "$P/GX1SUMS")" ] || { echo "task script pin"; exit 1; }
S=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$P/$LIST")
[ -n "$S" ] || { echo "no shard for index $SLURM_ARRAY_TASK_ID"; exit 1; }
bash "$P/gx1_gen_task.sh" "$S"

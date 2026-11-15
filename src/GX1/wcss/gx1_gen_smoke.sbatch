#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J gx1-gsmk
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:40G
#SBATCH --no-requeue
#SBATCH --time=0-00:40:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/gx1-gsmk-%j.out
# GX1 generation smoke: the two smoke shards (2 persons each, MIPGAN-I and MIPGAN-II; images never enter the data).
set -euo pipefail
P=/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/GX1
[ "$(sha256sum "$P/gx1_gen_task.sh" | cut -c1-64)" = "$(awk '$2=="gx1_gen_task.sh"{print $1}' "$P/GX1SUMS")" ] || { echo "task script pin"; exit 1; }
bash "$P/gx1_gen_task.sh" GX1_smoke_mip1
bash "$P/gx1_gen_task.sh" GX1_smoke_mip2
echo GX1_SMOKE_OK

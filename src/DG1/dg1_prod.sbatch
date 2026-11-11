#!/bin/bash -l
#SBATCH -J smadnext-DG1
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH -C localfs
#SBATCH --array=0-4
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/DG1-prod-%A_%a.out
# Diffusion-autoencoder generation on Athena (DG1), production: task 0 = set A (FRLL, 102 persons, neutral; 20 and 100
# decoding steps), tasks 1-4 = the four shards of set B (FRGC / colorFERET, 536 hosts, 20 steps, dose series). Each task
# runs one job list through dg1_gen.py in node-local scratch and writes one result tar with a .sha256.
# --time is set at submission from the smoke job's measured seconds per image (at most 4 hours per task).
set -eo pipefail
module load Python/3.12.3
set -u
export G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${SCRATCH_LOCAL:?node-local scratch required (-C localfs)}"
export TMPDIR=$SCRATCH_LOCAL/tmp; mkdir -p "$TMPDIR"
LISTS=(setA setB_s0 setB_s1 setB_s2 setB_s3)
L=${LISTS[$SLURM_ARRAY_TASK_ID]}
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
source "$G/packs/DG1/dg1_env.sh"
bash "$G/packs/DG1/dg1_run_task.sh" "$L" "$L"

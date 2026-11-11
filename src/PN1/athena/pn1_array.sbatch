#!/bin/bash -l
#SBATCH -J pn1-fits
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH -C memfs
#SBATCH --array=0-5
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/results/PN1/logs/fit-%A_%a.out
# Protocol network, first tests (PN1), tier 1: six ViT-B/16 LoRA fits (manifests A, B, C x seeds 401, 402), each through
# the unchanged run.sh (unchanged train.py of the AD4 pack), all work in the RAM disk, one result tar per task.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
TASKS=(PN1_A_s401 PN1_B_s401 PN1_C_s401 PN1_A_s402 PN1_B_s402 PN1_C_s402)
T=${TASKS[$SLURM_ARRAY_TASK_ID]}
W=$MEMFS/work_$T; mkdir -p "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$MEMFS/gpumem_$T.csv"; sleep 20; done ) & SM=$!
cd "$W"
TASK_DIR="$G/tasks/PN1/$T" TASK_WORK="$W" PN1_WORKERS=7 bash "$G/tasks/PN1/$T/run.sh"
kill $SM 2>/dev/null || true
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$MEMFS/gpumem_$T.csv"

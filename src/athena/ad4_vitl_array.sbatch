#!/bin/bash -l
#SBATCH -J smadnext-AD4L
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=10:00:00
#SBATCH -C memfs
#SBATCH --array=0-9
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AD4L-%A_%a.out
# The ten ViT-L/14 tasks of the morph-free networks experiment (AD4): five morph-free and five label-permuted fits,
# each through the unchanged run.sh, all work in node-local scratch, one result tar per task.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
ROOT=/net/pr2/projects/plgrid/plggrestoration
G=$ROOT/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
TASKS=(AD4_m3lmf_s401 AD4_m3lmf_s402 AD4_m3lmf_s403 AD4_m3lmf_s404 AD4_m3lmf_s405 AD4_m3lperm_s401 AD4_m3lperm_s402 AD4_m3lperm_s403 AD4_m3lperm_s404 AD4_m3lperm_s405)
T=${TASKS[$SLURM_ARRAY_TASK_ID]}
W=$MEMFS/work_$T; mkdir -p "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; cat "$G/logs/versions.txt"
cd "$W"
TASK_DIR="$G/tasks/$T" TASK_WORK="$W" AD4_LOCAL=1 AD4_PY="$G/venv/bin/python" AD4_ROOT="$ROOT" AD4_WORKERS=7 bash "$G/tasks/$T/run.sh"

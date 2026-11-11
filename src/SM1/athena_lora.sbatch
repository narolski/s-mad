#!/bin/bash -l
#SBATCH -J smadnext-SM1L
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH -C memfs
#SBATCH --array=0-19
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/SM1L-%A_%a.out
# SMDD five-partner audit and rebuild (SM1), amendment A9: 20 LoRA fits (arms a, c, d, e x seeds 401-405).
# Smoke: sbatch --array=0 --time=01:00:00 --export=ALL,STEPS=3,LIMIT=8,SMOKE=1 athena_lora.sbatch
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
ARMS=(a c d e)
i=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$((i / 5))]}; SEED=$((401 + i % 5))
TASK=SM1L_${ARM}_s${SEED}${SMOKE:+_smoke}
W=$MEMFS/work_$TASK; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date -Is
TASK=$TASK ARM=$ARM SEED=$SEED W=$W G=$G PY=$G/venv/bin/python STEPS=${STEPS:-6250} LIMIT=${LIMIT:-0} WORKERS=14 \
  bash "$G/tasks/SM1/lora_run.sh"

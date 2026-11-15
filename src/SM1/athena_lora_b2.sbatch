#!/bin/bash -l
#SBATCH -J smadnext-SM1B
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH -C memfs
#SBATCH --array=0-3
#SBATCH --exclude=t0010
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/SM1B2-%A_%a.out
# SM1 amendment A12 item 12: 4 ViT-B/16 LoRA fits (AD4's M3 recipe, as A11), arms b and b' x seeds 401, 402,
# through the same lora_run.sh (RECIPE=m3, MANIFESTS=sm1lora_manifests_b; images sm1gpu_img_armsb.tar), 6 workers.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
ARMS=(b bp)
i=$SLURM_ARRAY_TASK_ID
ARM=${ARMS[$((i / 2))]}; SEED=$((401 + i % 2))
TASK=SM1B_${ARM}_s${SEED}${SMOKE:+_smoke}
W=$MEMFS/work_$TASK; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date -Is
TASK=$TASK ARM=$ARM SEED=$SEED RECIPE=m3 MANIFESTS=sm1lora_manifests_b W=$W G=$G PY=$G/venv/bin/python STEPS=${STEPS:-6250} LIMIT=${LIMIT:-0} WORKERS=${WORKERS:-6} \
  bash "$G/tasks/SM1/lora_run.sh"

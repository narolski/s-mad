#!/bin/bash -l
#SBATCH -J smadnext-DG1addon
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -C memfs
#SBATCH --array=0-7
#SBATCH --exclude=t0010
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/DG1-addon-%A_%a.out
# Diffusion-autoencoder generation on Athena (DG1), amendment 2 (approved by the lead): the self-contained add-on, 8
# shards of the 536 set B hosts cut along the partner cycles. Per shard one process encodes every source once, saves
# codes, noise maps and fresh-noise draws, and renders REC/SAME/X/MIR re-renders, fresh-noise, noise-only and
# semantic-only mixes, 100-step REC/SAME/X/FRESH, and both dose series for the dose hosts. RAM disk $MEMFS; one result
# tar per shard, written even if the generator fails. The existing DG1 environment (same experiment).
set -eo pipefail
module load GCCcore/13.3.0 Python/3.12.3
set -u
export G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
L=addon_s$SLURM_ARRAY_TASK_ID
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
source "$G/packs/DG1/dg1_env.sh"
bash "$G/packs/DG1/dg1_addon_task.sh" "$L" "$L"

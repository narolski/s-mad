#!/bin/bash -l
#SBATCH -J smadnext-DG1smoke
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=00:50:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/DG1-smoke-%j.out
# Diffusion-autoencoder generation on Athena (DG1), smoke job (at most 1 GPU-hour): builds the experiment's own
# environment, then the equivalence gate (8 images that exist from the DGX A43 run: 4 reconstructions, 4 two-person
# morphs, 20 steps) and the 8-image check of both sets (20 and 100 steps), in the RAM disk $MEMFS (-C memfs; -C localfs gives only 4 GB on Athena); one result tar.
set -eo pipefail
module load GCCcore/13.3.0 Python/3.12.3
set -u
export G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; python3 --version
export DG1_ENV_BUILD=1
source "$G/packs/DG1/dg1_env.sh"
bash "$G/packs/DG1/dg1_run_task.sh" "smoke_$SLURM_JOB_ID" eq smoke8

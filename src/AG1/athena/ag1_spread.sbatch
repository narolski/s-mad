#!/bin/bash -l
#SBATCH -J smadnext-AG1s
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AG1s-%A_%a.out
# AG1 spread-matched renders (R2s): one array task per line "GEN POOL" of tasks/AG1/spread.txt.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
read -r GEN POOL < <(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$G/tasks/AG1/spread.txt")
bash "$G/tasks/AG1/ag1_spread_task.sh" "$GEN" "$POOL"

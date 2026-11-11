#!/bin/bash -l
#SBATCH -J smadnext-AG1
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH -C localfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AG1-%A_%a.out
# AG1 production: one array task = one shard, the shard named by line (SLURM_ARRAY_TASK_ID + 1) of the list file.
# Submit: sbatch --array=0-(n-1) ag1_array.sbatch tasks/AG1/<list>.txt  (AG3 list with --dependency=afterok:<core>)
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
LIST=${1:?list file}
S=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$G/$LIST")
[ -n "$S" ] || { echo "no shard for index $SLURM_ARRAY_TASK_ID"; exit 1; }
bash "$G/tasks/AG1/ag1_task.sh" "$S"

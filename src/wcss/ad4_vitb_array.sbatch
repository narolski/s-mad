#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --gres=gpu:hopper:1,storage:local:200G
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --no-requeue
#SBATCH --time=02:30:00
#SBATCH --job-name=ad4-vitb
#SBATCH --array=0-9%5
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ad4-vitb-%A_%a.out
# Owner: reading owner of the morph-free networks experiment (AD4). Workload: the ten ViT-B/16 tasks (five morph-free, five
# label-permuted), each through the unchanged run.sh from its task folder in staging/AD4 (pack, library packs and task folders
# are already on Lustre; prereg Amendment 5 (b)). All IO in $TMPDIR; one result tar per task to smad-next/results/AD4/.
# A task whose verified result tar already exists exits at once (run.sh: "already done").
set -euo pipefail
: "${TMPDIR:?local scratch required}"
B=/lustre/pd03/hpc-narolski-1790461090/smad-next
TASKS=(AD4_m3mf_s401 AD4_m3mf_s402 AD4_m3mf_s403 AD4_m3mf_s404 AD4_m3mf_s405
       AD4_m3perm_s401 AD4_m3perm_s402 AD4_m3perm_s403 AD4_m3perm_s404 AD4_m3perm_s405)
T=${TASKS[$SLURM_ARRAY_TASK_ID]}
TD=$B/staging/AD4/$T
[ -f "$TD/run.sh" ] && [ -f "$TD/task.env" ] || { echo "AD4 job: no task folder $TD; nothing to do"; exit 3; }
W=$TMPDIR/task_$T; mkdir -p "$W"
echo "AD4 job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID task $T host $(hostname) $(date +%FT%T)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
cd "$W"
TASK_DIR="$TD" TASK_WORK="$W" bash "$TD/run.sh"
echo "AD4 job end $T $(date +%FT%T)"

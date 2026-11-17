#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --partition=lem-gpu-short
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --no-requeue
#SBATCH --time=02:00:00
#SBATCH --job-name=h5race
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/h5race/logs/h5race-%x-%A_%a.out
# H5 race, WCSS H100 side (see h5_score_run.sh). Submit with --gres=gpu:hopper:1,storage:local:60G --array=1-3
# --export=ALL,LIMIT=0|8[,NETS="..."]. Task 1: release + s405, task 2: s401 s402, task 3: s403 s404 (as the GB10 streams).
set -euo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/h5race
: "${TMPDIR:?local scratch required}"
LIMIT=${LIMIT:-0}
case ${SLURM_ARRAY_TASK_ID:-0} in
  1) G="selfmad_hrnet_w18 selfmad_S_s405" ;; 2) G="selfmad_S_s401 selfmad_S_s402" ;; 3) G="selfmad_S_s403 selfmad_S_s404" ;;
  *) G="" ;;
esac
NETS=${NETS:-$G}; [ -n "$NETS" ] || { echo "no NETS"; exit 2; }
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; date
export PY=$HOME/dmenv/bin/python PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
O=$L/results/job_${SLURM_ARRAY_JOB_ID:-$SLURM_JOB_ID}_lim$LIMIT
bash $L/h5_score_run.sh $TMPDIR/h5 $L/parts $L/h5pack.tar $O "$NETS" $LIMIT 7

#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH --job-name=sprint5-pair
#SBATCH --partition=lem-gpu-short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --time=03:00:00
#SBATCH --array=0-14%1
#SBATCH --no-requeue
#SBATCH --output=/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/sprint5-1-%A_%a.out
set -euo pipefail
bash /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SPRINT5_1/source/worker.sh production

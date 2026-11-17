#!/bin/bash -l
#SBATCH -J h5race
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=100G
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/h5race-%A_%a.out
# H5 race, Athena A100 side (see h5_score_run.sh). Env = the AD5 scoring env (packs/AD5/wheels_score.tar,
# score_requirements.txt, built in the RAM disk as ad5_score_rel.sbatch does). Submit with --array=1-3
# --export=ALL,LIMIT=0|8[,NETS="..."]. Task 1: release + s405, task 2: s401 s402, task 3: s403 s404.
set -eo pipefail
module load Python/3.10.4
set -u
source /net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/code_v4/src/AD5/athena/ad5_common.sh
H=$PK/h5race; LIMIT=${LIMIT:-0}
case ${SLURM_ARRAY_TASK_ID:-0} in
  1) G="selfmad_hrnet_w18 selfmad_S_s405" ;; 2) G="selfmad_S_s401 selfmad_S_s402" ;; 3) G="selfmad_S_s403 selfmad_S_s404" ;;
  *) G="" ;;
esac
NETS=${NETS:-$G}; [ -n "$NETS" ] || { echo "no NETS"; exit 2; }
hostname; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; date
build_env_local score $PK/code_v4/src/AD5/env/score_requirements.txt $PK/wheels_score.tar
export PY=$SCRATCH_LOCAL/env_score/bin/python
O=$RS/h5race/job_${SLURM_ARRAY_JOB_ID:-$SLURM_JOB_ID}_lim$LIMIT
bash $H/h5_score_run.sh $SCRATCH_LOCAL/h5 $H/parts $H/h5pack.tar $O "$NETS" $LIMIT 3

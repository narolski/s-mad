#!/bin/bash -l
#SBATCH -J se1-fit
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH -C memfs
#SBATCH --array=0-14
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/results/SE1/logs/fit-%A_%a.out
# Seam-shortcut training arm (SE1), Athena twin of src/SE1/wcss/se1_fit.sbatch (prereg section 4: one platform for all
# 15 fits; the dispatcher cancels the twin on the other cluster once one starts). Arms A, Sb, SE x seeds 408-412, seed by
# seed; src/SE1/run.sh in the project container (PN1_SIF), work in the RAM disk, one result tar per task to results/SE1.
set -eo pipefail
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
P=$G/packs/SE1
: "${MEMFS:?RAM disk required (-C memfs)}"
ARMS=(A Sb SE A Sb SE A Sb SE A Sb SE A Sb SE)
SEEDS=(408 408 408 409 409 409 410 410 410 411 411 411 412 412 412)
I=$SLURM_ARRAY_TASK_ID; ARM=${ARMS[$I]}; SEED=${SEEDS[$I]}
[ "$(sha256sum "$P/run.sh" | cut -c1-64)" = b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb ] || { echo "SE1 FAIL run.sh not at its registered pin"; exit 1; }
(cd "$P" && sha256sum -c --quiet run.sh.sha256 se1_overlay.tar.sha256 pn1_pack_fs.tar.sha256)
TD=$MEMFS/td; W=$MEMFS/w; mkdir -p "$TD" "$W"; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
printf 'TASK=SE1_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "SE1 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$G PN1_PACK=$P/pn1_pack_fs.tar SE1_OVERLAY=$P/se1_overlay.tar \
  SE1_OVERLAY_SHA=de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c PN1_SIF=$G/containers/smad_torch221_cu121_v1.sif PN1_WORKERS=7 bash "$P/run.sh"
echo "SE1 fit end $ARM $SEED $(date -Is)"

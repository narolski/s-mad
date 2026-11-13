#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ms1p4-fit
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-03:00:00
#SBATCH --array=0-19%20
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ms1p4-fit-%A_%a.out
# MS1 part 4 (prereg.md part 4): 20 fits on WCSS H100, arms Sb (6,250 steps), Sb63 (train_Sb at 3,938 steps), SbM3,
# SbM3S, seeds 403-407, seed by seed; the unchanged PN1 recipe through run_p4.sh; every score in the fit job. All IO in
# $TMPDIR; one result tar per fit to results/MS1P4. A task whose verified tar exists exits at once.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/MS1
ARMS=(Sb Sb63 SbM3 SbM3S Sb Sb63 SbM3 SbM3S Sb Sb63 SbM3 SbM3S Sb Sb63 SbM3 SbM3S Sb Sb63 SbM3 SbM3S)
SEEDS=(403 403 403 403 404 404 404 404 405 405 405 405 406 406 406 406 407 407 407 407)
ARM=${ARMS[$SLURM_ARRAY_TASK_ID]}; SEED=${SEEDS[$SLURM_ARRAY_TASK_ID]}
(cd "$P" && sha256sum -c --quiet run_p4.sh.sha256)
$HOME/dmenv/bin/python -c "import torch, timm; assert torch.__version__ == '2.11.0+cu128' and timm.__version__ == '1.0.30', (torch.__version__, timm.__version__); assert 'sm_90' in torch.cuda.get_arch_list()"
TD=$TMPDIR/td; W=$TMPDIR/w; mkdir -p "$TD" "$W"
printf 'TASK=MS1P4_%s_s%s\nARM=%s\nSEED=%s\n' "$ARM" "$SEED" "$ARM" "$SEED" > "$TD/task.env"
echo "MS1P4 fit $ARM $SEED job $SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID host $(hostname) $(date -Is)"
nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader || true
TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_ms2.tar MS1_RESULTS=$L/results/MS1P4 \
  PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_p4.sh"
echo "MS1P4 fit end $ARM $SEED $(date -Is)"

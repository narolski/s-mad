#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ms1-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ms1-smoke-%j.out
# MS1 smoke on WCSS H100: run.sh (MS1 copy) with 20 steps and 64 scoring rows, arms SbM3 and Sb at seed 403; results to
# results/MS1_smoke (never read as results). All IO in $TMPDIR.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/MS1
hostname; nvidia-smi -L; date -Is
(cd "$P" && sha256sum -c pn1_pack_ms1.tar.sha256 && sha256sum -c run.sh.sha256)
$HOME/dmenv/bin/python -c "import torch, timm, numpy, PIL; print('env', torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))"
for ARM in SbM3 Sb; do
  TD=$TMPDIR/td_$ARM; W=$TMPDIR/w_$ARM; mkdir -p "$TD" "$W"
  printf 'TASK=MS1smoke_%s_s403\nARM=%s\nSEED=403\n' "$ARM" "$ARM" > "$TD/task.env"
  TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_ms1.tar MS1_RESULTS=$L/results/MS1_smoke \
    PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_STEPS=20 PN1_LIMIT=64 PN1_WORKERS=7 bash "$P/run.sh"
  rm -rf "$W"
done
echo "MS1_SMOKE_DONE $(date -Is)"

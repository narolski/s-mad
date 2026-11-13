#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ms1p4-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ms1p4-smoke-%j.out
# MS1 part 4 smoke on WCSS H100 through the real path: run_p4.sh with 20 steps and 64 scoring rows, arms Sb63 and SbM3S,
# seed 403; results to results/MS1P4_smoke (never read as results). Prints GPU, torch, CUDA arch list. All IO in $TMPDIR.
set -euo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/MS1
hostname; nvidia-smi -L; date -Is
(cd "$P" && sha256sum -c pn1_pack_ms2.tar.sha256 && sha256sum -c run_p4.sh.sha256)
$HOME/dmenv/bin/python -c "import torch, timm; print('env', torch.__version__, torch.version.cuda, timm.__version__, torch.cuda.get_device_name(0), torch.cuda.get_arch_list()); assert torch.__version__ == '2.11.0+cu128' and timm.__version__ == '1.0.30'; assert 'sm_90' in torch.cuda.get_arch_list()"
for ARM in Sb63 SbM3S; do
  TD=$TMPDIR/td_$ARM; W=$TMPDIR/w_$ARM; mkdir -p "$TD" "$W"
  printf 'TASK=MS1P4smoke_%s_s403\nARM=%s\nSEED=403\n' "$ARM" "$ARM" > "$TD/task.env"
  TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_ms2.tar MS1_RESULTS=$L/results/MS1P4_smoke \
    PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_STEPS=20 PN1_LIMIT=64 PN1_WORKERS=7 bash "$P/run_p4.sh"
  rm -rf "$W"
done
echo "MS1P4_SMOKE_DONE $(date -Is)"

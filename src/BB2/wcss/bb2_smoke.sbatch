#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-smoke-%j.out
# Second backbone (BB2) smoke on a WCSS H100: src/BB2/run.sh, arm Sb seed 403, 100 steps, 64 scoring rows, first at batch
# 256 in one pass; only if that run fails, the registered fallback batch 128 x 2 accumulation. Decides the batch rule of
# the fits mechanically (prereg section 4); results go to results/BB2_smoke and are never read as results.
# GPU memory is logged every 5 s. All IO in $TMPDIR. Exits within a minute if its pack or scripts are missing.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2
hostname; nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader; date -Is
(cd "$P" && sha256sum -c pn1_pack_fs.tar.sha256 && sha256sum -c bb2_overlay.tar.sha256 && sha256sum -c run.sh.sha256) || { echo "BB2_SMOKE_FAIL pack or script check"; exit 1; }
$HOME/dmenv/bin/python -c "import torch, timm, numpy, PIL; print('env', torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))"
nvidia-smi --query-gpu=timestamp,memory.used,memory.total,utilization.gpu --format=csv,noheader -l 5 > "$TMPDIR/gpumem.csv" 2>&1 &
MON=$!
rc256=1; rc128=1
for MODE in 256x1 128x2; do
  BS=${MODE%x*}; AC=${MODE#*x}
  [ "$MODE" = 128x2 ] && [ "$rc256" = 0 ] && break
  TD=$TMPDIR/td_$MODE; W=$TMPDIR/w_$MODE; mkdir -p "$TD" "$W"
  printf 'TASK=BB2smoke_Sb_s403_bs%s\nARM=Sb\nSEED=403\n' "$MODE" > "$TD/task.env"
  TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_fs.tar BB2_OVERLAY=$P/bb2_overlay.tar \
    BB2_RESULTS=$L/results/BB2_smoke BB2_BS=$BS BB2_ACCUM=$AC PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python \
    PN1_STEPS=100 PN1_LIMIT=64 PN1_WORKERS=7 bash "$P/run.sh"
  rc=$?; echo "BB2_SMOKE_MODE $MODE rc $rc $(date -Is)"
  [ "$MODE" = 256x1 ] && rc256=$rc || rc128=$rc
  rm -rf "$W"
done
kill $MON 2>/dev/null
echo "BB2_GPUMEM_PEAK_MIB $(cut -d, -f2 "$TMPDIR/gpumem.csv" | tr -dc '0-9\n' | sort -n | tail -1)"
mkdir -p $L/results/BB2_smoke && cp "$TMPDIR/gpumem.csv" "$L/results/BB2_smoke/gpumem_$SLURM_JOB_ID.csv"
echo "BB2_SMOKE_DONE rc256 $rc256 rc128 $rc128 $(date -Is)"

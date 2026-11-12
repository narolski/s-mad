#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2-smoke
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-smoke-%j.out
# Second backbone (BB2) smoke on a WCSS H100 (prereg sections 4 and 9). src/BB2/run.sh, arm Sb seed 403, 100 steps, 64
# scoring rows: first batch 256 in one pass, then batch 128 x 2 accumulation (both always run, so the fallback is
# tested). GPU memory.used logged every 2 s per mode; peak printed (BB2_PEAK_MIB). After the 256 x 1 run, featcheck.py
# compares the initial DINOv3 features of 8 training images with the DGX CPU reference (tolerance 1e-3).
# Results go to results/BB2_smoke and are never read as results. All IO in $TMPDIR. Exits within a minute if its
# pack or scripts are missing or off their sha256.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2
hostname; nvidia-smi --query-gpu=name,uuid,memory.total --format=csv,noheader; date -Is
(cd "$P" && sha256sum -c pn1_pack_fs.tar.sha256 bb2_overlay.tar.sha256 run.sh.sha256 featcheck.py.sha256 featref_cpu.npz.sha256) || { echo "BB2_SMOKE_FAIL pack or script check"; exit 1; }
$HOME/dmenv/bin/python -c "import torch, timm, numpy, PIL; print('env', torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))"
mkdir -p $L/results/BB2_smoke
for MODE in 256x1 128x2; do
  BS=${MODE%x*}; AC=${MODE#*x}
  TD=$TMPDIR/td_$MODE; W=$TMPDIR/w_$MODE; mkdir -p "$TD" "$W"
  printf 'TASK=BB2smoke_Sb_s403_bs%s\nARM=Sb\nSEED=403\n' "$MODE" > "$TD/task.env"
  nvidia-smi --query-gpu=timestamp,memory.used,memory.total --format=csv,noheader,nounits -lms 2000 > "$TMPDIR/gpumem_$MODE.csv" 2>&1 &
  MON=$!
  TASK_DIR=$TD TASK_WORK=$W PN1_ROOT=$L PN1_PACK=$P/pn1_pack_fs.tar BB2_OVERLAY=$P/bb2_overlay.tar \
    BB2_RESULTS=$L/results/BB2_smoke BB2_BS=$BS BB2_ACCUM=$AC PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python \
    PN1_STEPS=100 PN1_LIMIT=64 PN1_WORKERS=7 bash "$P/run.sh"
  rc=$?
  kill $MON 2>/dev/null; sleep 1
  PEAK=$(cut -d, -f2 "$TMPDIR/gpumem_$MODE.csv" | tr -dc '0-9\n' | sort -n | tail -1)
  TOT=$(cut -d, -f3 "$TMPDIR/gpumem_$MODE.csv" | tr -dc '0-9\n' | sort -n | tail -1)
  echo "BB2_SMOKE_MODE $MODE rc $rc BB2_PEAK_MIB $PEAK of $TOT $(date -Is)"
  cp "$TMPDIR/gpumem_$MODE.csv" "$L/results/BB2_smoke/gpumem_${SLURM_JOB_ID}_$MODE.csv"
  if [ "$MODE" = 256x1 ] && [ -d "$W/pn1" ]; then
    SMAD_DATA=$W/data HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 $HOME/dmenv/bin/python -I "$P/featcheck.py" --root "$W/pn1" \
      --out "$TMPDIR/feat_wcss.npz" --ref "$P/featref_cpu.npz"
    echo "BB2_FEATCHECK_RC $?"
    cp "$TMPDIR/feat_wcss.npz" "$L/results/BB2_smoke/feat_wcss_$SLURM_JOB_ID.npz" 2>/dev/null
  fi
  rm -rf "$W"
done
echo "BB2_SMOKE_DONE $(date -Is)"

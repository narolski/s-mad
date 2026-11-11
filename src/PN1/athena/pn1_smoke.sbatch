#!/bin/bash -l
#SBATCH -J pn1-smoke
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=00:50:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/results/PN1/logs/smoke-%j.out
# Protocol network, first tests (PN1): smoke test of one manifest-Bn task through the unchanged run.sh on the real pack
# (200 steps, 64 scored rows per manifest), timing and peak GPU memory; optional tier-0 feature extraction
# (featx.tar present in packs/PN1) for DINOv3 sets the DGX could not extract within its GPU allowance.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
SIF=$G/containers/smad_torch221_cu121_v1.sif
echo "SIF_SHA256 $(sha256sum "$SIF" | cut -c1-64)"
apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" "$SIF" python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'cuda', torch.cuda.is_available())"
S=$MEMFS/smoke; mkdir -p "$S/root/results" "$S/work" "$S/task"
cp "$G/tasks/PN1/run.sh" "$S/task/run.sh"
printf 'TASK=PN1_Bn_s401_smoke\nARM=Bn\nSEED=401\n' > "$S/task/task.env"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$S/gpumem.csv"; sleep 5; done ) & SM=$!
set +e
( cd "$S/work" && TASK_DIR="$S/task" TASK_WORK="$S/work" PN1_ROOT="$S/root" PN1_PACK="$G/packs/PN1/pn1_pack.tar" \
  PN1_STEPS=${SMOKE_STEPS:-200} PN1_LIMIT=64 PN1_WORKERS=7 bash "$S/task/run.sh" ) > "$S/smoke_run.log" 2>&1
rc=$?
set -e
kill $SM 2>/dev/null || true
tail -60 "$S/smoke_run.log"
grep -E "it/s|step" "$S/work/train.log" 2>/dev/null | tail -5 || true
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$S/gpumem.csv"
echo "SMOKE_RC=$rc"
mkdir -p "$G/results/PN1/smoke"
cp "$S/smoke_run.log" "$S/gpumem.csv" "$G/results/PN1/smoke/" || true
cp "$S"/root/results/PN1/*.tar* "$G/results/PN1/smoke/" 2>/dev/null || true
# optional tier-0 features
if [ -f "$G/packs/PN1/featx.tar" ]; then
  X=$MEMFS/featx; mkdir -p "$X"
  cp "$G/packs/PN1/featx.tar" "$MEMFS/featx.tar"
  [ "$(sha256sum "$MEMFS/featx.tar" | cut -c1-64)" = "$(cut -c1-64 "$G/packs/PN1/featx.tar.sha256")" ] || { echo "featx sha256"; exit 1; }
  tar -C "$X" -xf "$MEMFS/featx.tar"
  (cd "$X/featx" && sha256sum -c --quiet SHA256SUMS) || { echo "featx content"; exit 1; }
  ( cd "$X/featx" && HF_HOME="$X/featx/hf" HF_HUB_OFFLINE=1 PN1_FEAT_OUT="$X/featx/out" apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" "$SIF" python -I featx_run.py ) 2>&1 | tail -30
  tar -C "$X/featx" -cf "$MEMFS/featx_out.tar" out
  cp "$MEMFS/featx_out.tar" "$G/results/PN1/featx_out.tar"
  (cd "$MEMFS" && sha256sum featx_out.tar) > "$G/results/PN1/featx_out.tar.sha256"
  echo FEATX_DONE
fi
exit $rc

#!/bin/bash -l
#SBATCH -J smadnext-env
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=00:45:00
#SBATCH -C localfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/env-%j.out
# Builds the Python environment on a compute node (Cyfronet rule: no builds on the login node) with the same
# package versions as the WCSS container and the rented machines, then runs a 3-step smoke test of one task of the
# morph-free networks experiment (AD4) through the unchanged run.sh.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
ROOT=/net/pr2/projects/plgrid/plggrestoration
G=$ROOT/smad-next
: "${SCRATCH_LOCAL:?node-local scratch required (-C localfs)}"
export TMPDIR=$SCRATCH_LOCAL/tmp; mkdir -p "$TMPDIR"
hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; python3 --version
if [ ! -x "$G/venv/bin/python" ] || ! "$G/venv/bin/python" -c "import torch, timm" 2>/dev/null; then
  python3 -m venv --clear "$G/venv"
  P="$G/venv/bin/python -m pip --require-virtualenv --no-cache-dir"
  $P install -q -U pip
  $P install -q torch==2.2.1 torchvision==0.17.1 --index-url https://download.pytorch.org/whl/cu121
  $P install -q "timm==1.0.27" "huggingface_hub==0.36.2" "safetensors==0.8.0" "numpy==1.26.4" "pyyaml==6.0.3" "pillow==10.2.0"
fi
"$G/venv/bin/python" -c "import sys, torch, timm, numpy, PIL, safetensors; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'safetensors', safetensors.__version__, 'gpu', torch.cuda.get_device_name(0)); assert torch.cuda.is_available() and timm.__version__ == '1.0.27' and torch.__version__.startswith('2.2.1')" | tee "$G/logs/versions.txt"
echo ENV_OK
# smoke: one ViT-L/14 task, 3 steps, 8 scored images, results into a separate smoke root
T=AD4_m3lmf_s401
S=$SCRATCH_LOCAL/smoke; mkdir -p "$S/root/smad-next/packs/AD4" "$S/root/smad-next/results" "$S/work" "$S/task"
ln -sf "$G/packs/AD4/ad4_pack.tar" "$S/root/smad-next/packs/AD4/ad4_pack.tar"
cp "$G/tasks/$T/run.sh" "$S/task/"; sed "s/^TASK=.*/TASK=${T}_smoke/" "$G/tasks/$T/task.env" > "$S/task/task.env"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$S/gpumem.csv"; sleep 5; done ) & SM=$!
( cd "$S/work" && TASK_DIR="$S/task" TASK_WORK="$S/work" AD4_LOCAL=1 AD4_PY="$G/venv/bin/python" AD4_ROOT="$S/root" AD4_WORKERS=7 AD4_STEPS=${SMOKE_STEPS:-40} AD4_LIMIT=8 bash "$S/task/run.sh" ) 2>&1 | tail -40; rc=${PIPESTATUS[0]}
kill $SM 2>/dev/null || true
awk -F", " '{if ($1+0>m) m=$1+0} END {print "PEAK_MIB " m}' "$S/gpumem.csv"
echo "SMOKE_RC=$rc"
exit $rc

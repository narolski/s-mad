#!/bin/bash -l
#SBATCH -J smadnext-AG1smoke
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=00:55:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/AG1smoke-%j.out
# AG1 smoke (at most 1 GPU-hour): builds envs/AG1 with pinned versions if absent, then the two smoke shards (2 FRLL
# persons through every rung: R2, R2i, R3m mirror, R3, R4, RT, AG3 alpha, MIPGAN-II) through ag1_task.sh.
set -eo pipefail
module load Python/3.10.4 2>&1 || echo "module Python/3.10.4 not loadable; using system python"
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
E=$G/envs/AG1
: "${MEMFS:?RAM disk required (-C memfs)}"
export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR"
hostname; python3 --version
if [ ! -x "$E/bin/python" ] || ! "$E/bin/python" -c "import torch, torchvision, numpy, PIL" 2>/dev/null; then
  mkdir -p "$G/envs"
  python3 -m venv --clear "$E"
  PIP="$E/bin/python -m pip --require-virtualenv --no-cache-dir"
  $PIP install -q -U pip==24.0
  $PIP install -q torch==2.2.1 torchvision==0.17.1 --index-url https://download.pytorch.org/whl/cu121
  $PIP install -q numpy==1.26.4 pillow==10.2.0
fi
"$E/bin/python" -I -c "import sys, torch, torchvision, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'torchvision', torchvision.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'gpu', torch.cuda.get_device_name(0)); assert torch.cuda.is_available() and torch.__version__.startswith('2.2.1')" | tee "$E/versions.txt"
"$E/bin/python" -m pip freeze > "$E/pip_freeze.txt"
echo ENV_OK
rc=0
for S in AG1_smoke_mip1 AG1_smoke_mip2; do
  bash "$G/tasks/AG1/ag1_task.sh" "$S" || { rc=$?; echo "SMOKE $S FAILED rc=$rc"; }
done
echo "SMOKE_RC=$rc"
exit $rc

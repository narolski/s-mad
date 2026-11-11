#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): build (once) or verify the experiment's own Python environment
# inside a job on an Athena compute node (Cyfronet rule: nothing is installed on the login node).
# Versions start from the DGX environment of the A43 generator (/mnt/t7/thirdparty/diffae_venv + .venv-spark):
# Python 3.12.3, torch 2.12.1 / torchvision 0.27.1 (DGX: +cu130), numpy 1.26.4, pillow 12.2.0, pytorch-lightning 2.5.5,
# torchmetrics 1.8.2, lightning-utilities 0.15.2, lmdb 1.7.3, pandas 2.2.3, pytorch-fid 0.3.0, scipy 1.17.1, lpips 0.1.4,
# tqdm 4.68.3, PyYAML 6.0.3. CUDA build: cu130 if the driver is >= 580 (as the DGX), else the nearest that installs
# (cu128, then cu126); a package pin that does not install is replaced by the newest version that does, and recorded.
# Sourced by dg1_smoke.sbatch / dg1_prod.sbatch after `module load Python/3.12.3`. Sets DG1_PY.
set -eo pipefail
G=${G:?}
E=$G/envs/DG1/venv
V=$G/envs/DG1/versions.txt
PINS="numpy==1.26.4 pillow==12.2.0 pytorch-lightning==2.5.5 torchmetrics==1.8.2 lightning-utilities==0.15.2 lmdb==1.7.3 pandas==2.2.3 python-dateutil==2.9.0.post0 pytz==2025.2 tzdata==2025.2 pytorch-fid==0.3.0 scipy==1.17.1 lpips==0.1.4 tqdm==4.68.3 PyYAML==6.0.3"
CHECK='import sys, torch, torchvision, numpy, PIL, pytorch_lightning, torchmetrics, scipy, pandas, lmdb, lpips, pytorch_fid; print("python", sys.version.split()[0], "torch", torch.__version__, "cuda", torch.version.cuda, "torchvision", torchvision.__version__, "numpy", numpy.__version__, "pillow", PIL.__version__, "pytorch_lightning", pytorch_lightning.__version__, "gpu", torch.cuda.get_device_name(0)); assert torch.cuda.is_available()'
if [ -x "$E/bin/python" ] && [ -f "$V" ] && "$E/bin/python" -I -c "$CHECK" > /dev/null 2>&1; then
  echo "DG1 env present: $E"
else
  mkdir -p "$G/envs/DG1"
  python3 -m venv --clear "$E"
  P="$E/bin/python -m pip --require-virtualenv --no-cache-dir --disable-pip-version-check"
  DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
  DMAJ=${DRV%%.*}
  CUS="cu128 cu126"; [ "$DMAJ" -ge 580 ] && CUS="cu130 cu128 cu126"
  TOK=""
  for CU in $CUS; do
    if $P install -q torch==2.12.1 torchvision==0.27.1 --index-url "https://download.pytorch.org/whl/$CU"; then TOK=$CU; break; fi
    echo "torch 2.12.1 / torchvision 0.27.1 with $CU did not install"
  done
  [ -n "$TOK" ] || { echo "no torch 2.12.1 build installed"; exit 3; }
  TV=$("$E/bin/python" -I -c 'import torch, torchvision; print(torch.__version__, torchvision.__version__)')
  printf 'torch==%s\ntorchvision==%s\n' ${TV} > "$G/envs/DG1/constraints.txt"
  DEV=""
  for p in $PINS; do
    if ! $P install -q -c "$G/envs/DG1/constraints.txt" "$p"; then
      n=${p%%==*}; echo "pin $p did not install; taking the newest that does"
      $P install -q -c "$G/envs/DG1/constraints.txt" "$n"; DEV="$DEV $p->$($E/bin/python -m pip show $n | awk '/^Version/{print $2}')"
    fi
  done
  {
    echo "built $(date -Is) on $(hostname) driver $DRV torch index $TOK"
    echo "deviations from the DGX pins:${DEV:- none}"
    "$E/bin/python" -I -c "$CHECK"
    "$E/bin/python" -m pip freeze
  } > "$V"
fi
head -3 "$V"
"$E/bin/python" -I -c "$CHECK"
DG1_PY=$E/bin/python
export DG1_PY

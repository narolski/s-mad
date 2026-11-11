#!/bin/bash
# Runs once on the rented machine (no credentials here). Checks the uploaded pack, installs the pinned Python
# packages into the image's Python (torch 2.2.1 + cu121 is the WCSS container's torch), records versions.
set -euo pipefail
B=/workspace/ad4
cd "$B/root/smad-next/packs/AD4"
sha256sum -c ad4_pack.tar.sha256
cd "$B"
python -m pip install --no-cache-dir "timm==1.0.27" "huggingface_hub==0.36.2" "safetensors==0.8.0" "numpy==1.26.4" \
  "pyyaml==6.0.3" > "$B/pip.log" 2>&1 || { tail -20 "$B/pip.log"; exit 1; }
python -c "import sys, torch, timm, numpy, PIL, safetensors; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'safetensors', safetensors.__version__, 'gpus', torch.cuda.device_count())" | tee "$B/versions.txt"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv | tee "$B/gpus.txt"
nproc | tee "$B/nproc.txt"
echo SETUP_OK

#!/bin/bash
# SM1 rented A100, run on the machine (no credentials here): installs exactly the pinned packages of
# src/athena/containers/smad_torch221_cu121_v1.def into the image's Python (torch held at the image's version), records
# versions and the machine. Packs are unpacked by unpack_one.sh as they arrive (drive.sh setup).
set -euo pipefail
B=/workspace/sm1r
mkdir -p "$B/logs"
python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
  numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || { tail -20 "$B/logs/pip.log"; exit 1; }
python -c "import sys, torch, timm, numpy, PIL, safetensors, huggingface_hub, yaml; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__, 'safetensors', safetensors.__version__, 'huggingface_hub', huggingface_hub.__version__, 'pyyaml', yaml.__version__, 'gpus', torch.cuda.device_count())" | tee "$B/logs/versions.txt"
python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv | tee "$B/logs/gpus.txt"
nproc | tee "$B/logs/nproc.txt"; df -h /workspace /dev/shm | tee "$B/logs/disk.txt"
echo SETUP_OK

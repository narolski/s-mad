#!/bin/bash
# RS1 crop regen env (GB10, 2026-11-16): venv on the spark python (system-site-packages) + facenet wheel from the pack.
set -euo pipefail
PYV=/home/narolski/mambamorph-code/.venv-spark/bin/python
EV=/home/narolski/smad-next/envs/rs1regen
W=/mnt/t7/smad_next/RS1/regen_pack
[ -f "$EV/bin/python" ] || "$PYV" -m venv --system-site-packages "$EV"
# prefer the packed wheel; wait briefly for the pack unpack to provide it
for i in 1 2 3 4 5; do
  WH=$(ls "$W"/wheels/facenet_pytorch-2.6.0-py3-none-any.whl 2>/dev/null | head -1)
  if [ -n "$WH" ]; then
    "$EV/bin/python" -m pip install -q --no-deps "$WH"
    break
  fi
  sleep 60
done
[ -n "${WH:-}" ] || { echo "NO FACENET WHEEL (pack not unpacked yet)"; exit 7; }
"$EV/bin/python" -I -c 'import facenet_pytorch, torch, torchvision, cv2, numpy, safetensors, PIL; print("FACENET_ENV_OK torch", torch.__version__, "facenet", facenet_pytorch.__version__ if hasattr(facenet_pytorch,"__version__") else "?", "numpy", numpy.__version__)'

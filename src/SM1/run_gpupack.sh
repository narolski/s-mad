#!/bin/bash
# SM1: image tars of the GPU feature pack (amendment A7), one set after another. Usage: run_gpupack.sh SET:list,list ...
set -euo pipefail
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /tmp
for spec in "$@"; do
  S=${spec%%:*}; L=${spec#*:}
  [ -f /mnt/t7/smad_next/SM1/gpupack/sm1gpu_img_$S.tar.sha256 ] || $P /home/narolski/smad-next/src/SM1/gpu_pack.py images $S $L
done
echo GPUPACK_DONE "$@"

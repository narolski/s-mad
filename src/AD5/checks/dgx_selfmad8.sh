#!/bin/bash
# Retrains of released methods (AD5): 8-image check of the patched SelfMAD train__.py on the DGX (-v last, -e 1, -b 8
# so that the 8 renders give 2 steps of 4 + 4), then the checkpoint format against the release. Retries on CUDA OOM.
set -uo pipefail
C=/mnt/t7/smad_next/AD5/checks/selfmad8; SRC=/mnt/t7/smad_next/AD5/build/selfmad_src; PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
for k in 1 2 3 4 5 6 7 8; do
  rm -rf $C/out; mkdir -p $C/out
  ( cd $SRC && AD5_SEED=401 HF_HUB_CACHE=/mnt/t7/smad_next/AD5/hf_cache HF_HUB_OFFLINE=1 timeout 1800 nice -n 10 $PY -I \
      /home/narolski/smad-next/src/AD5/checks/run_with_site.py /mnt/t7/smad_next/AD5/build/dgx_site:$SRC $SRC/train__.py \
      -n ad5_check8 -m hrnet_w18 -b 8 -e 1 -lr 5e-4 -t SMDD -v last -SMDD_path $C/SMDD -s $C/out ) > $C/train8.log 2>&1
  echo "try $k rc $? $(date +%H:%M)"
  ls $C/out/*/weights/epoch_1.tar 2>/dev/null && break
  grep -q "out of memory" $C/train8.log || { echo "failed, not OOM"; tail -20 $C/train8.log; exit 1; }
  sleep 150
done
$PY -I -c "
import torch,glob; f=glob.glob('$C/out/*/weights/epoch_1.tar')[0]; d=torch.load(f,map_location='cpu',weights_only=True); print(sorted(d), d['epoch'], len(d['model']))
from safetensors.torch import load_file; r=load_file('/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors'); print('release tensors', len(r), 'same keys', set(r)==set(d['model']), 'same shapes', all(r[k].shape==d['model'][k].shape for k in r))
"
tail -3 $C/out/*/logs/losses.logs; echo CHECK_DONE

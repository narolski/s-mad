#!/bin/bash
# PD1 DiffAE: smoke (8 images), FZ1 reuse check, then full sets; CLIP first, then DINOv3. Sequential, one GPU process.
set -euo pipefail
R=/home/narolski/smad-next/src/PD1/diffae/run_feats.sh
for m in clip dino; do
  $R $m tr --limit 8 --tag smoke
  $R $m none --check-fz1
  $R $m tr,f256,ad1b,fr512,smdd,ev
done

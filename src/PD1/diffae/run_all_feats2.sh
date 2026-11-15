#!/bin/bash
# PD1 DiffAE: full CLIP sets first (CLIP smoke already passed), then DINOv3 smoke and full sets, then the FZ1 reuse
# checks (they only compare with FZ1's caches; they do not gate the analysis). Sequential, one GPU process at a time.
set -uo pipefail
R=/home/narolski/smad-next/src/PD1/diffae/run_feats.sh
$R clip tr,f256,ad1b,fr512,smdd,ev
$R dino tr --limit 8 --tag smoke
$R dino tr,f256,ad1b,fr512,smdd,ev
$R clip none --check-fz1
$R dino none --check-fz1

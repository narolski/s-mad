#!/bin/bash
# PD1 DiffAE: DINOv3 smoke and full sets with 2 loader workers (3 processes, so the CPU analysis fits within 4), then
# the FZ1 reuse checks (comparison with FZ1's caches only; they do not gate the analysis). One GPU process at a time.
set -uo pipefail
R=/home/narolski/smad-next/src/PD1/diffae/run_feats.sh
$R dino tr --limit 8 --tag smoke --workers 2
$R dino tr,f256,ad1b,fr512,smdd,ev --workers 2
$R clip none --check-fz1 --workers 2
$R dino none --check-fz1 --workers 2

#!/bin/bash
# RZ1: write the current overlay sha256 into run_rz1.sh, then run_rz1.sh's and the overlay's sha256 into the sbatch files.
set -euo pipefail
cd "$(dirname "$0")"
OV=$(cut -c1-64 /mnt/t7/smad_next/RZ1/rz1_overlay.tar.sha256)
sed -i -E "s/(OVR_SHA=)[0-9a-f_A-Z]+/\1$OV/" run_rz1.sh
RS=$(sha256sum run_rz1.sh | cut -c1-64)
for f in wcss/*.sbatch; do
  sed -i -E "s#(\"\\\$P/run_rz1.sh\" \| cut -c1-64\)\" = )[0-9a-f]+#\1$RS#; s#(\"\\\$P/rz1_overlay.tar\" \| cut -c1-64\)\" = )[0-9a-f]+#\1$OV#" "$f"
done
grep -h "OVR_SHA=" run_rz1.sh; grep -ho "= [0-9a-f]\{64\}" wcss/*.sbatch | sort | uniq -c; echo "run_rz1.sh $RS overlay $OV"

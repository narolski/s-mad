#!/bin/bash
# FZ2: extract DGX features for each DG1 add-on shard as soon as the DG1 owner's copy is complete (PNG count equals the
# shard's job count in addon_lists_summary.json). Scans every 5 minutes, at most 14 hours. Waits for the production
# extraction to finish first (one extraction process at a time).
set -uo pipefail
O=/mnt/t7/smad_next/FZ2/results/dgx/out
while pgrep -f "^bash /home/narolski/smad-next/src/FZ2/fz2_dgx_feats.sh setB" > /dev/null; do sleep 30; done
for scan in $(seq 1 168); do
  left=0
  for k in 0 1 2 3 4 5 6 7; do
    L=addon_s$k
    [ -f $O/clip_mad_$L.npz ] && [ -f $O/dinov2_$L.npz ] && continue
    left=1
    exp=$(python3 -c "import json;d=json.load(open('/mnt/t7/smad_next/DG1/addon_jobs/addon_lists_summary.json'))['shards']['$L.csv'];print(d['renders20']+d['renders100'])")
    have=$(find /mnt/t7/smad_next/DG1/gen/$L -name '*.png' 2>/dev/null | wc -l)
    if [ "$have" = "$exp" ]; then
      echo "$(date +%H:%M) $L complete ($have png): extracting"
      bash /home/narolski/smad-next/src/FZ2/fz2_dgx_feats.sh $L
    fi
  done
  [ $left = 0 ] && { echo "$(date +%H:%M) all add-on shards extracted"; exit 0; }
  sleep 300
done

#!/bin/bash
# FZ2: once all 16 add-on feature files exist (8 shards x 2 backbones) and no extraction runs, run the registered primary
# read. Checks every 2 minutes, at most 16 hours.
set -uo pipefail
O=/mnt/t7/smad_next/FZ2/results/dgx/out
for k in $(seq 1 480); do
  n=$(ls $O/clip_mad_addon_s*.npz $O/dinov2_addon_s*.npz 2>/dev/null | wc -l)
  if [ "$n" = 16 ] && ! pgrep -f "fz2_feats.py --backbone" > /dev/null; then
    echo "$(date +%H:%M) all 16 add-on feature files present: running the primary read"
    cd /home/narolski/smad-next && OMP_NUM_THREADS=2 nice -n 5 /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
      src/FZ2/fz2_read.py --run addon --feats-dir $O --workers 3 > /mnt/t7/smad_next/FZ2/logs/read_addon.log 2>&1
    echo "$(date +%H:%M) read exit $?"; exit 0
  fi
  sleep 120
done
echo "timed out"; exit 3

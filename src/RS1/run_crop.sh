#!/bin/bash
# Own-crop re-score of the audit rows (RS1): release crops (RGB MTCNN, AR1 crop_rgb.py byte-identical) for the images
# A46 did not crop, in 2 shards, then the 32-file crop check (raw files already cropped by A46), then the merge.
set -euo pipefail
S=/home/narolski/smad-next/src/RS1; O=/mnt/t7/smad_next/RS1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
t0=$(date +%s)
for i in 0 1; do
  [ -f $O/crops/main/crops_${i}of2.csv ] || nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/tocrop.csv --out $O/crops/main --shard $i/2 > $O/crops/main_shard$i.log 2>&1 &
done
wait
echo "crop main $(( $(date +%s) - t0 )) s"
[ -f $O/crops/check/crops.csv ] || nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/cropcheck.csv --out $O/crops/check > $O/crops/check.log 2>&1
nice -n 10 $P -I $S/manifest.py merge
echo CROP_DONE

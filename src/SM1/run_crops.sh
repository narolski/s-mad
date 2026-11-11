#!/bin/bash
# SM1: own MTCNN crops of the audit images in 3 shards (frozen copy of the AR1 crop script, ar1copy/crop_rgb.py).
V="nice -n 10 /mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python -I"
cd /tmp
for i in 0 1 2; do
  $V /home/narolski/smad-next/src/SM1/ar1copy/crop_rgb.py --manifest /mnt/t7/smad_next/SM1/flists/audit.csv --out /mnt/t7/smad_next/SM1/crops/audit --shard $i/3 > /mnt/t7/smad_next/SM1/crops/audit_crop_$i.log 2>&1 &
done
wait
echo CROPS_DONE >> /mnt/t7/smad_next/SM1/crops/audit_crop_0.log

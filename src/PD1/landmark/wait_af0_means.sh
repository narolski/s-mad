#!/usr/bin/env bash
# PD1 landmark: wait for AF0's DINOv3 caches h1 (1196) and ar1g (1800) to complete, then take mean patch tokens (read only)
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/PD1/landmark
for nm in h1:1196 ar1g:1800; do
  n=${nm%%:*}; c=${nm##*:}
  until [ "$(cat /mnt/t7/smad_next/AF0/feat/dinov3_512/$n.done 2>/dev/null)" = "$c" ] && ! pgrep -f "feat.py --backbone dinov3_512 .*--name $n( |$)" >/dev/null; do sleep 60; done
  nice -n 10 $PY -I af0_means.py dinov3_512 $n
done

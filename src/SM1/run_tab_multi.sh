#!/bin/bash
# SM1 T-A / T-B scoring in detector groups (unified GPU memory is tight: 7 models at once ran out of memory).
set -euo pipefail
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /tmp
for G in madation_vitb16,madation_fe_vitb16,mixfacenet_mad_smdd,madation_vitl14,madation_fe_vitl14 madation_fs_vitb16,madation_fs_vitl14; do
  $P /home/narolski/smad-next/src/SM1/rel_multi.py --manifest /mnt/t7/smad_next/SM1/flists/${TABLIST:-tab_sub}.csv --out-dir /mnt/t7/smad_next/SM1/p2scores/${TABLIST:-tab_sub} --dets $G --bs 32 --workers 6
done
TABLIST=${TABLIST:-tab_sub} $P /home/narolski/smad-next/src/SM1/tab.py read
echo TAB_DONE

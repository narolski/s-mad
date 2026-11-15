#!/bin/bash
# RS1: score the 300 JPEG-vs-PNG crop pairs (jpeg_check.py) with the seven releases on the DGX, then compare.
set -uo pipefail
S=/home/narolski/smad-next/src/RS1; O=/mnt/t7/smad_next/RS1/jpegcheck; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /tmp
for d in madation_vitb16 madation_vitl14 madation_fe_vitl14 madation_fe_vitb16 madation_fs_vitb16 madation_fs_vitl14 mixfacenet_mad_smdd; do
  for k in 1 2 3 4; do
    [ -f $O/scores_rel_${d}__jpegcheck.npz ] && break
    nice -n 10 $P -I $S/rs1_score.py --det $d --mode rel --manifest $O/jpegcheck.csv --out-dir $O --tag rel_${d}__jpegcheck --workers 1 --bs 32 > $O/log_$d.log 2>&1
    echo "$d try $k exit $? $(date +%H:%M)"
    [ -f $O/scores_rel_${d}__jpegcheck.npz ] || sleep 90
  done
done
$P -I $S/jpeg_check.py compare
echo JPEGCHECK_DONE

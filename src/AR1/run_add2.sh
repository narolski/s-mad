#!/bin/bash
# fix-up: blanked R2w4 rows of the splice set had no box (their boxes are in crops/extra2); crop and score them
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
until grep -q ADD_DONE $O/run_add.log; do sleep 30; done
$P -I $S/splice.py boxes
$P -I -c "
import csv
rows=[r for r in csv.DictReader(open('$O/crops/splice_bl/crops.csv')) if r['status']=='no_face']
ids={r['id'] for r in rows}
m=[r for r in csv.DictReader(open('$O/lists/splice_blank.csv')) if r['id'] in ids]
with open('$O/lists/splice_blank2.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(m[0])); w.writeheader(); w.writerows(m)
print(len(m))"
[ -f $O/crops/splice_bl2/crops.csv ] || retry nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/splice_blank2.csv --boxes-in $O/crops/boxes_splice.json --out $O/crops/splice_bl2
$P -I $S/lists.py crops $O/crops/splice_bl2/crops.csv $O/lists/crops_splice_bl2.csv
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do
  [ -f $O/scores/scores_rel_${d}__splice_bl2.npz ] || retry nice -n 10 $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_splice_bl2.csv --out-dir $O/scores --tag rel_${d}__splice_bl2
done
echo ADD2_DONE

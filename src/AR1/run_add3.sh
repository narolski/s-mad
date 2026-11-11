#!/bin/bash
# amendment 7b: crops and release scoring of the one-hull splice arms (S4, S3, S0) and their blanked copies
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
until grep -q ADD2_DONE $O/run_add2.log; do sleep 30; done
$P -I -c "
import csv
rows=list(csv.DictReader(open('$O/manifest_splice2.csv')))
for name,sel in (('sp2_native',lambda r: r['variant']=='native'),('sp2_blank',lambda r: r['variant']!='native')):
    with open('$O/lists/'+name+'.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows([r for r in rows if sel(r)])
"
[ -f $O/crops/splice2/crops.csv ] || retry nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/sp2_native.csv --out $O/crops/splice2
$P -I $S/splice.py boxes7b
[ -f $O/crops/splice2_bl/crops.csv ] || retry nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/sp2_blank.csv --boxes-in $O/crops/boxes_splice2.json --out $O/crops/splice2_bl
for v in splice2 splice2_bl; do $P -I $S/lists.py crops $O/crops/$v/crops.csv $O/lists/crops_$v.csv; done
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do for v in splice2 splice2_bl; do
  [ -f $O/scores/scores_rel_${d}__$v.npz ] || retry nice -n 10 $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_$v.csv --out-dir $O/scores --tag rel_${d}__$v
done; done
[ -f $O/scores/scores_own_selfmad__splice2.npz ] || retry nice -n 10 $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/sp2_native.csv --out-dir $O/scores --tag own_selfmad__splice2
[ -f $O/scores/scores_own_selfmad__splice2_bl.npz ] || retry nice -n 10 $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/sp2_blank.csv --lm-from lm_src --out-dir $O/scores --tag own_selfmad__splice2_bl
echo ADD3_DONE

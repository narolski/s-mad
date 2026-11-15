#!/bin/bash
# SM1 T-A / T-B (amendment A3): own MTCNN crops (AR1 crop_rgb.py, unchanged) of tab.csv, then release scores
# (rel_score.py, no TTA, loader in the main process). One process at a time (DGX process cap).
set -euo pipefail
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
V="nice -n 10 /mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python -I"
cd /tmp
L=tab
[ -f $O/crops/$L/crops.csv ] || $V /home/narolski/smad-next/src/AR1/crop_rgb.py --manifest $O/flists/$L.csv --out $O/crops/$L --boxes-out $O/crops/boxes_$L.json
$P -c "
import csv,collections
rows=list(csv.DictReader(open('$O/crops/$L/crops.csv')))
print(collections.Counter(r['status'].split(':')[0] for r in rows))
keep=[dict(id=r['id'],path=r['path']) for r in rows if r['status']=='retained' or r['status'].startswith('flag')]
w=csv.DictWriter(open('$O/crops/${L}_list.csv','w',newline=''),fieldnames=['id','path']); w.writeheader(); w.writerows(keep)
print('crops kept', len(keep))
"
for d in ${DETS:-madation_vitb16 madation_fe_vitb16 mixfacenet_mad_smdd madation_vitl14 madation_fe_vitl14}; do
  [ -f $O/p2scores/tab/scores_rel_$d.npz ] || $P $S/rel_score.py --det $d --manifest $O/crops/${L}_list.csv --out-dir $O/p2scores/tab --tag rel_$d --no-tta --workers 0 --bs 64
done
$P $S/tab.py read
echo TAB_DONE

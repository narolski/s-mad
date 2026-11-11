#!/bin/bash
# SM1 Part 2 chain: audit pairs -> morphs (unchanged engine) -> own MTCNN crops (AR1 crop_rgb.py, unchanged) ->
# release scores (rel_score.py) -> reader. Stages run one after another (process cap). Usage: run_p2.sh smoke|full
set -euo pipefail
MODE=$1
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
V="nice -n 10 /mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python -I"
cd /tmp
[ "$MODE" = smoke ] && L=smoke_audit || L=audit
$P $S/build.py --list $O/lists/$L.csv --workers ${BW:-1}
mkdir -p $O/crops
[ -f $O/crops/$L/crops.csv ] || $V /home/narolski/smad-next/src/AR1/crop_rgb.py --manifest $O/flists/$L.csv --out $O/crops/$L --boxes-out $O/crops/boxes_$L.json
$P -c "
import csv,collections
rows=list(csv.DictReader(open('$O/crops/$L/crops.csv')))
print(collections.Counter(r['status'].split(':')[0] for r in rows))
keep=[dict(id=r['id'],path=r['path']) for r in rows if r['status']=='retained' or r['status'].startswith('flag')]
w=csv.DictWriter(open('$O/crops/${L}_list.csv','w',newline=''),fieldnames=['id','path']); w.writeheader(); w.writerows(keep)
print('crops kept', len(keep))
"
SD=$O/p2scores; [ "$MODE" = smoke ] && SD=$O/p2scores/smoke
for d in madation_vitb16 madation_vitl14 madation_fe_vitb16 madation_fe_vitl14 mixfacenet_mad_smdd madation_fs_vitb16 madation_fs_vitl14; do
  [ -f $SD/scores_rel_$d.npz ] || $P $S/rel_score.py --det $d --manifest $O/crops/${L}_list.csv --out-dir $SD --tag rel_$d --workers 0
done
echo P2_SCORED_$MODE

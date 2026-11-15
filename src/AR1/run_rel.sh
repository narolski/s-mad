#!/bin/bash
# chain A: batched RGB-MTCNN crops (3 shards), merged boxes, blanked copies cropped with the original boxes, 3 rel releases
set -euo pipefail
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
mkdir -p $O/crops $O/scores $O/lists
t0=$(date +%s)
for i in 0 1 2; do
  [ -f $O/crops/main/crops_${i}of3.csv ] || retry $V -I $S/crop_rgb.py --manifest $O/manifest.csv --out $O/crops/main --shard $i/3 > $O/crops/main_shard$i.log 2>&1 &
done
wait
echo "crop main $(( $(date +%s) - t0 )) s"
$P -I -c "import json,glob; d={}
for f in sorted(glob.glob('$O/crops/main/boxes_*of3.jsonl')):
    for l in open(f):
        r=json.loads(l); d[r['id']]=r['box']
json.dump(d, open('$O/crops/boxes_main.json','w')); print('boxes', len(d))"
$P -I $S/lists.py blank $O/lists/blank.csv
[ -f $O/crops/bg/crops.csv ] || retry $V -I $S/crop_rgb.py --manifest $O/lists/blank.csv --src-col bg_path --boxes-in $O/crops/boxes_main.json --out $O/crops/bg
[ -f $O/crops/face/crops.csv ] || retry $V -I $S/crop_rgb.py --manifest $O/lists/blank.csv --src-col face_path --boxes-in $O/crops/boxes_main.json --out $O/crops/face
for v in main bg face; do $P -I $S/lists.py crops $O/crops/$v/crops.csv $O/lists/crops_$v.csv; done
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do
  [ -f $O/scores/scores_rel_$d.npz ] || retry $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_main.csv --out-dir $O/scores --tag rel_$d
done
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do for v in bg face; do
  [ -f $O/scores/scores_rel_${d}__$v.npz ] || retry $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_$v.csv --out-dir $O/scores --tag rel_${d}__$v
done; done
$P -I $S/check_a46.py list
mkdir -p $O/scores/a46check
for d in madation_vitb16 madation_vitl14 mixfacenet_mad_smdd; do
  [ -f $O/scores/a46check/scores_rel_$d.npz ] || retry $P -I $S/score.py --det $d --mode rel --manifest $O/lists/a46check.csv --out-dir $O/scores/a46check --tag rel_$d
done
echo REL_DONE

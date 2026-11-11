#!/bin/bash
# AR1 scoring chain (after the builds). Features and scores are written; no score file is opened here.
set -euo pipefail
S=/home/narolski/smad-next/src/AR1
O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
[ -f $O/manifest.csv ] || $P -I $S/manifest.py > $O/manifest.log
$P -I $S/blank.py --pools frgcferet,frll --rungs R0,R2,R3,R4,NC,R2w,R3m
mkdir -p $O/crops $O/scores $O/lists
t0=$(date +%s)
if [ ! -f $O/crops/boxes_main.json ]; then
  for i in 0 1 2; do $V -I $S/crop_rgb.py --manifest $O/manifest.csv --out $O/crops/main --boxes-out $O/crops/boxes_main.json --shard $i/3 > $O/crops/main_shard$i.log 2>&1 & done
  wait
  $P -I -c "import json,glob; d={}; [d.update(json.load(open(f))) for f in sorted(glob.glob('$O/crops/boxes_main_*of3.json'))]; json.dump(d, open('$O/crops/boxes_main.json','w')); print('boxes', len(d))"
fi
echo "crop main $(( $(date +%s) - t0 )) s"
$P -I $S/lists.py blank $O/lists/blank.csv
[ -f $O/crops/bg/crops.csv ] || $V -I $S/crop_rgb.py --manifest $O/lists/blank.csv --src-col bg_path --boxes-in $O/crops/boxes_main.json --out $O/crops/bg
[ -f $O/crops/face/crops.csv ] || $V -I $S/crop_rgb.py --manifest $O/lists/blank.csv --src-col face_path --boxes-in $O/crops/boxes_main.json --out $O/crops/face
for v in main bg face; do $P -I $S/lists.py crops $O/crops/$v/crops.csv $O/lists/crops_$v.csv; done
$P -I $S/lists.py frames $O/lists/frames.csv
for d in madation_vitb16 madation_vitl14 mixfacenet_mad_smdd; do
  [ -f $O/scores/scores_rel_$d.npz ] || $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_main.csv --out-dir $O/scores --tag rel_$d
  for v in bg face; do
    [ -f $O/scores/scores_rel_${d}__$v.npz ] || $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_$v.csv --out-dir $O/scores --tag rel_${d}__$v
  done
done
[ -f $O/scores/scores_own_selfmad.npz ] || $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/manifest.csv --out-dir $O/scores --tag own_selfmad
[ -f $O/scores/scores_own_selfmad__bg.npz ] || $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/blank.csv --col bg_path --lm-from path --out-dir $O/scores --tag own_selfmad__bg
[ -f $O/scores/scores_own_selfmad__face.npz ] || $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/blank.csv --col face_path --lm-from path --out-dir $O/scores --tag own_selfmad__face
for s in 1 2 3 4 5 6 7 8; do
  r=a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3_s$s.npz ] || $P -I $S/score.py --det M3 --mode nets --run $r --manifest $O/lists/frames.csv --out-dir $O/scores --tag nets_M3_s$s
done
for s in 1 2 3 4 5; do
  r=a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3L_s$s.npz ] || $P -I $S/score.py --det M3L --mode nets --run $r --manifest $O/lists/frames.csv --out-dir $O/scores --tag nets_M3L_s$s
done
echo SCORING_DONE

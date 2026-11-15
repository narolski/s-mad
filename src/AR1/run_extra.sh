#!/bin/bash
# chain C: the appended R2wm rows (manifest_extra.csv): crop, 3 rel releases, SelfMAD own, then the retrain block
set -euo pipefail
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
until grep -q "crop main" $O/run_rel.log; do sleep 60; done
[ -f $O/crops/extra/crops.csv ] || retry $V -I $S/crop_rgb.py --manifest $O/manifest_extra.csv --out $O/crops/extra
$P -I $S/lists.py crops $O/crops/extra/crops.csv $O/lists/crops_extra.csv
until grep -q "REL_DONE" $O/run_rel.log; do sleep 60; done
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do
  [ -f $O/scores/scores_rel_${d}__extra.npz ] || retry $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_extra.csv --out-dir $O/scores --tag rel_${d}__extra
done
until grep -q "OWN_NETS_DONE" $O/run_own_nets.log; do sleep 60; done
[ -f $O/scores/scores_own_selfmad__extra.npz ] || retry $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/manifest_extra.csv --out-dir $O/scores --tag own_selfmad__extra
for s in 1 2 3 4 5 6 7 8; do r=a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3_s${s}__extra.npz ] || retry $P -I $S/score.py --det M3 --mode nets --run $r --manifest $O/manifest_extra.csv --out-dir $O/scores --tag nets_M3_s${s}__extra
done
for s in 1 2 3 4 5; do r=a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3L_s${s}__extra.npz ] || retry $P -I $S/score.py --det M3L --mode nets --run $r --manifest $O/manifest_extra.csv --out-dir $O/scores --tag nets_M3L_s${s}__extra
done
echo EXTRA_DONE

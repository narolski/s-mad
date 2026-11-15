#!/bin/bash
# chain D: the appended R2w4 rows (manifest_extra2.csv): crop, 3 rel releases, SelfMAD own, retrains
set -euo pipefail
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
[ -f $O/crops/extra2/crops.csv ] || retry $V -I $S/crop_rgb.py --manifest $O/manifest_extra2.csv --out $O/crops/extra2
$P -I $S/lists.py crops $O/crops/extra2/crops.csv $O/lists/crops_extra2.csv
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do
  [ -f $O/scores/scores_rel_${d}__extra2.npz ] || retry $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_extra2.csv --out-dir $O/scores --tag rel_${d}__extra2
done
[ -f $O/scores/scores_own_selfmad__extra2.npz ] || retry $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/manifest_extra2.csv --out-dir $O/scores --tag own_selfmad__extra2
for s in 1 2 3 4 5 6 7 8; do r=a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3_s${s}__extra2.npz ] || retry $P -I $S/score.py --det M3 --mode nets --run $r --manifest $O/manifest_extra2.csv --out-dir $O/scores --tag nets_M3_s${s}__extra2
done
for s in 1 2 3 4 5; do r=a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3L_s${s}__extra2.npz ] || retry $P -I $S/score.py --det M3L --mode nets --run $r --manifest $O/manifest_extra2.csv --out-dir $O/scores --tag nets_M3L_s${s}__extra2
done
echo EXTRA2_DONE

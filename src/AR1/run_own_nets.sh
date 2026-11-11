#!/bin/bash
# chain B: SelfMAD own preprocessing (main + blanked, landmarks from the originals) and the retrain block (512 frames)
set -euo pipefail
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
mkdir -p $O/scores $O/lists
$P -I $S/lists.py blank $O/lists/blank_own.csv
$P -I $S/lists.py frames $O/lists/frames.csv
[ -f $O/scores/scores_own_selfmad.npz ] || retry $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/manifest.csv --out-dir $O/scores --tag own_selfmad
for v in bg face; do
  [ -f $O/scores/scores_own_selfmad__$v.npz ] || retry $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/blank_own.csv --col ${v}_path --lm-from path --out-dir $O/scores --tag own_selfmad__$v
done
for s in 1 2 3 4 5 6 7 8; do r=a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3_s$s.npz ] || retry $P -I $S/score.py --det M3 --mode nets --run $r --manifest $O/lists/frames.csv --out-dir $O/scores --tag nets_M3_s$s
done
for s in 1 2 3 4 5; do r=a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s${s}_r
  [ -f $O/scores/scores_nets_M3L_s$s.npz ] || retry $P -I $S/score.py --det M3L --mode nets --run $r --manifest $O/lists/frames.csv --out-dir $O/scores --tag nets_M3L_s$s
done
echo OWN_NETS_DONE

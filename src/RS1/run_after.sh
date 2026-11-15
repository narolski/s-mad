#!/bin/bash
# Own-crop re-score of the audit rows (RS1), DGX orchestration after the main crops: wait for both main crop shards,
# crop check, amendment-2 crops (2 shards, retried on CUDA out of memory), merge, then (after the A46-crop scoring)
# score the new and the amendment crops, then SelfMAD's own preprocessing on the pools it has no score for.
set -uo pipefail
S=/home/narolski/smad-next/src/RS1; O=/mnt/t7/smad_next/RS1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
until [ -f $O/crops/main/crops_0of2.csv ] && [ -f $O/crops/main/crops_1of2.csv ]; do sleep 60; done
echo "main crops done $(date +%H:%M)"
[ -f $O/crops/check/crops.csv ] || nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/cropcheck.csv --out $O/crops/check > $O/crops/check.log 2>&1
crop_shard() {  # $1 = shard index
  for k in 1 2 3 4 5 6; do
    [ -f $O/crops/amend/crops_${1}of2.csv ] && return 0
    nice -n 10 $V -I $S/crop_rgb.py --manifest $O/lists/tocrop_amend.csv --out $O/crops/amend --shard $1/2 >> $O/crops/amend_shard$1.log 2>&1
    echo "amend shard $1 try $k exit $? $(date +%H:%M)"
    [ -f $O/crops/amend/crops_${1}of2.csv ] || sleep 180
  done
}
mkdir -p $O/crops/amend
crop_shard 0 & crop_shard 1 & wait
echo "amend crops done $(date +%H:%M)"
nice -n 10 $P -I $S/manifest.py merge
until ! pgrep -f "run_score.sh a46" > /dev/null; do sleep 60; done
$S/run_score.sh new
$S/run_score.sh amend
for k in 1 2 3 4; do
  [ -f $O/scores/scores_own_selfmad__amend.npz ] && break
  nice -n 10 $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/selfmad_own_amend.csv \
    --out-dir $O/scores --tag own_selfmad__amend --workers 2 > $O/scores/log_own_selfmad__amend_try$k.log 2>&1
  echo "selfmad own try $k exit $? $(date +%H:%M)"
  [ -f $O/scores/scores_own_selfmad__amend.npz ] || sleep 180
done
echo AFTER_DONE

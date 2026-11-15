#!/bin/bash
# Retrains of released methods (AD5): score the SelfMAD release and the SelfMAD retrains on the DGX through RS1's
# score.py --mode own (the release's own preprocessing), on every RS1 manifest image (raw source files; RS1 set names).
#   run_selfmad_dgx.sh [NAMES...]   default: selfmad_hrnet_w18 selfmad_S_s401 ... selfmad_S_s405
# The list is cut into parts of 2,500 images (a killed run loses one part only; the first full run was killed by the
# DGX at 19:38 on 11 Nov); each part is retried up to 6 times; finished parts are skipped; the parts are then merged
# into scores_own_<name>__ad5.npz (ids in list order). Retrain tars: /mnt/t7/smad_next/AD5/results/<name>.tar.
set -uo pipefail
A=/mnt/t7/smad_next/AD5; O=$A/scores_selfmad; mkdir -p $O/parts $A/conv_selfmad
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
REL=/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors
PART=${PART:-2500}
$PY -I - "$O" "$PART" <<'PYEOF'
import csv, sys, pathlib
O, n = pathlib.Path(sys.argv[1]), int(sys.argv[2])
rows = [r for r in csv.DictReader(open('/mnt/t7/smad_next/RS1/manifest.csv')) if r['src_path']]
for k in range(0, len(rows), n):
    p = O / 'parts' / f'list_{k // n:02d}.csv'
    if not p.exists():
        with open(p, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['id', 'path']); [w.writerow([r['id'], r['src_path']]) for r in rows[k:k + n]]
print('images', len(rows), 'parts', (len(rows) + n - 1) // n)
PYEOF
NAMES=${*:-selfmad_hrnet_w18 selfmad_S_s401 selfmad_S_s402 selfmad_S_s403 selfmad_S_s404 selfmad_S_s405}
cd /tmp
for n in $NAMES; do
  [ -f $O/scores_own_${n}__ad5.npz ] && { echo "$n done"; continue; }
  if [ $n = selfmad_hrnet_w18 ]; then wf=$REL
  else
    t=$A/results/$n.tar; (cd $A/results && sha256sum -c $n.tar.sha256) || { echo "missing or bad $t"; continue; }
    d=$A/conv_selfmad/$n; mkdir -p $d; [ -f $d/model.safetensors ] || { tar -xf $t -C $d && \
      $PY -I /home/narolski/smad-next/src/AD5/score/convert_selfmad.py $d/epoch_100.tar $d/model.safetensors $REL > $d/convert.json; } || exit 1
    wf=$d/model.safetensors
  fi
  for L in $O/parts/list_*.csv; do
    k=$(basename $L .csv | cut -d_ -f2); tag=own_${n}__ad5_part$k
    for t in 1 2 3 4 5 6; do
      [ -f $O/parts/scores_$tag.npz ] && break
      nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/score/ad5_score_dgx.py --name $n --weights $wf -- --mode own \
        --manifest $L --out-dir $O/parts --tag $tag --workers ${W:-4} > $O/parts/log_$tag.log 2>&1 && break
      echo "$tag try $t failed $(date +%H:%M)"; sleep 120
    done
    [ -f $O/parts/scores_$tag.npz ] || { echo "FAILED $tag"; continue 2; }
  done
  $PY -I - "$O" "$n" <<'PYEOF'
import sys, glob, pathlib, numpy as np
O, n = pathlib.Path(sys.argv[1]), sys.argv[2]
fs = sorted(glob.glob(str(O / 'parts' / f'scores_own_{n}__ad5_part*.npz')))
zs = [np.load(f) for f in fs]
out = {k: np.concatenate([z[k] for z in zs]) for k in ('id', 'score', 'score_noTTA', 'logit_noTTA', 'cropped')}
assert len(set(out['id'].tolist())) == len(out['id'])
np.savez(O / f'scores_own_{n}__ad5.npz', det=n, mode='own', parts=np.array([pathlib.Path(f).name for f in fs]), **out)
print(n, 'merged', len(out['id']), 'from', len(fs), 'parts')
PYEOF
done
echo SELFMAD_SCORING_DONE

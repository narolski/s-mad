#!/bin/bash
# One-shot scoring of selfmad_S_s405 (retrain, WCSS 6310127_405 COMPLETED 12:02:58Z) on GB10.
# Mirrors registered src/AD5/score/run_selfmad_dgx.sh flow exactly (same ad5_score_dgx.py, same parts lists,
# same retries, same merge) — only difference: weights come from /home staging (t7 is 100% full, cannot hold
# the 1.71 GB retrain tar; documented deviation, scoring code/pins unchanged).
set -uo pipefail
A=/mnt/t7/smad_next/AD5; O=$A/scores_selfmad; n=selfmad_S_s405
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
WF=/home/narolski/ad6_stage/selfmad_s405/conv/model.safetensors
[ -f "$WF" ] || { echo "NO_WEIGHTS"; exit 1; }
cd /tmp
for L in $O/parts/list_*.csv; do
  k=$(basename "$L" .csv | cut -d_ -f2); tag=own_${n}__ad5_part$k
  for t in 1 2 3 4 5 6; do
    [ -f "$O/parts/scores_$tag.npz" ] && break
    nice -n 10 "$PY" -I /home/narolski/smad-next/src/AD5/score/ad5_score_dgx.py --name "$n" --weights "$WF" -- --mode own \
      --manifest "$L" --out-dir "$O/parts" --tag "$tag" --workers 4 > "$O/parts/log_$tag.log" 2>&1 && break
    echo "$tag try $t failed $(date +%H:%M)"; sleep 60
  done
  [ -f "$O/parts/scores_$tag.npz" ] || { echo "FAILED $tag"; break; }
done
"$PY" -I "$O" "$n" <<'PYEOF'
import sys, glob, pathlib, numpy as np
O, n = pathlib.Path(sys.argv[1]), sys.argv[2]
fs = sorted(glob.glob(str(O / 'parts' / f'scores_own_{n}__ad5_part*.npz')))
zs = [np.load(f) for f in fs]
out = {k: np.concatenate([z[k] for z in zs]) for k in ('id', 'score', 'score_noTTA', 'logit_noTTA', 'cropped')}
assert len(set(out['id'].tolist())) == len(out['id'])
np.savez(O / f'scores_own_{n}__ad5.npz', det=n, mode='own', parts=np.array([pathlib.Path(f).name for f in fs]), **out)
print(n, 'merged', len(out['id']), 'from', len(fs), 'parts')
PYEOF
echo SELFMAD_S405_SCORING_DONE

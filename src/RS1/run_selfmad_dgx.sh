#!/bin/bash
# Own-crop re-score of the audit rows (RS1): SelfMAD release with its own preprocessing (AR1 score.py --mode own,
# dlib 81 landmarks, 384, softmax[:, 1]) on the DGX, on one platform: raw FRLL photos, raw MorDIFF morphs, raw E7
# MorDIFF files, the A43 stored control images, FEI and FFHQ (amendment 2). Retries on CUDA out of memory.
set -uo pipefail
S=/home/narolski/smad-next/src/RS1; O=/mnt/t7/smad_next/RS1; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /tmp
for k in 1 2 3 4 5 6; do
  [ -f $O/scores/scores_own_selfmad__dgx.npz ] && break
  nice -n 10 $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/lists/selfmad_own_dgx.csv \
    --out-dir $O/scores --tag own_selfmad__dgx --workers 2 > $O/scores/log_own_selfmad__dgx_try$k.log 2>&1
  echo "selfmad own try $k exit $? $(date +%H:%M)"
  [ -f $O/scores/scores_own_selfmad__dgx.npz ] || sleep 180
done
echo SELFMAD_DGX_DONE

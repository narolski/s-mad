#!/bin/bash
# Retrains of released methods (AD5): the scoring wrapper (score/ad5_score_athena.py) scores the release on 8 RS1 crops
# exactly as RS1's rs1_score.py does (same score.py): both on the DGX, compared tensor by tensor. Retries on CUDA OOM.
set -uo pipefail
C=/mnt/t7/smad_next/AD5/checks/score8; PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
REL=/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors
cd /tmp
for k in 1 2 3 4 5 6 7 8; do
  [ -f $C/out/scores_wrap_madation_vitb16.npz ] || nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/score/ad5_score_athena.py $C/root $C/site \
    --as madation_vitb16 --name madation_vitb16 --weights $REL -- --mode rel --manifest $C/m8.csv --out-dir $C/out \
    --tag wrap_madation_vitb16 --workers 1 --bs 8 > $C/wrap_rel.log 2>&1
  [ -f $C/out/scores_direct_madation_vitb16.npz ] || nice -n 10 $PY -I /home/narolski/smad-next/src/RS1/rs1_score.py --det madation_vitb16 \
    --mode rel --manifest $C/m8.csv --out-dir $C/out --tag direct_madation_vitb16 --workers 1 --bs 8 > $C/direct_rel.log 2>&1
  [ -f $C/out/scores_wrap_madation_vitb16.npz ] && [ -f $C/out/scores_direct_madation_vitb16.npz ] && break
  sleep 120
done
$PY -I -c "
import numpy as np
a=np.load('$C/out/scores_wrap_madation_vitb16.npz'); b=np.load('$C/out/scores_direct_madation_vitb16.npz')
print('ids equal', (a['id']==b['id']).all())
for k in ('score','score_noTTA','logit_noTTA'): print(k, 'max abs diff', float(np.abs(a[k]-b[k]).max()))
fa=np.load('$C/out/feat_wrap_madation_vitb16.npz')['feat']; fb=np.load('$C/out/feat_direct_madation_vitb16.npz')['feat']; print('feat max abs diff', float(np.abs(fa-fb).max()))
"

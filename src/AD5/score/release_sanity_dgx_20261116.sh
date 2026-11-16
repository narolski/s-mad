#!/bin/bash
# Sanity release re-score on GB10 (2026-11-16): 3 registered releases (madation_vitb16, madation_vitl14,
# mixfacenet_mad_smdd) x (v1, v2) on the SAME regen crops as the 15 retrain scores -> "before S" per-id join.
set -uo pipefail
R=/mnt/t7/smad_next/RS1/regen_pack
W=/mnt/t7/smad_next/RS1/regen_run
O=/mnt/t7/smad_next/AD5/scores_retrains
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/AD5/score
SITE=/tmp/rs1_nosite
declare -A WF=( [madation_vitb16]=$R/weights/ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors \
  [madation_vitl14]=$R/weights/bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980.safetensors \
  [mixfacenet_mad_smdd]=$R/weights/3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c.pth )
for n in madation_vitb16 madation_vitl14 mixfacenet_mad_smdd; do
  for v in v1 v2; do
    [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && { echo "$n $v done"; continue; }
    t0=$(date +%s)
    for try in 1 2 3 4 5 6; do
      [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && break
      nice -n 10 "$PY" -I "$S/ad5_score_athena.py" "$R" "$SITE" --as "$n" --name "$n" --weights "${WF[$n]}" \
        -- --mode rel --manifest "$W/score_$v.csv" --out-dir "$O" --tag "rel_${n}__ad5$v" --workers 6 --bs 32 \
        > "$O/log_rel_${n}__ad5${v}_try$try.log" 2>&1 && break
      echo "$n $v try $try failed"; tail -5 "$O/log_rel_${n}__ad5${v}_try$try.log"; sleep 90
    done
    [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && echo "$n $v scored $(( $(date +%s) - t0 ))s"
  done
done
echo RELEASE_SANITY_DONE

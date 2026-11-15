#!/bin/bash
# AD5 retrain scoring on GB10 (2026-11-16): 15 retrains (madation B/L s401–405, mixfacenet_X s401–405)
# through the Athena registered scoring path (ad5_score_athena.py: pack ROOT + byte-identical score.py),
# on the RS1 crops regenerated on GB10 (REGEN per-file sha-verified vs prod_v1/prod_v2 rented references).
#   run_retrains_dgx.sh [NAMES...]
# Output: /mnt/t7/smad_next/AD5/scores_retrains/scores_rel_<name>__ad5{v1,v2}.npz (+ logs).
set -uo pipefail
R=/mnt/t7/smad_next/RS1/regen_pack
W=/mnt/t7/smad_next/RS1/regen_run
CF=/mnt/t7/smad_next/RS1/convert_retrains
O=/mnt/t7/smad_next/AD5/scores_retrains
T=/mnt/t7/smad_next/AD5/results_athena_pull
S=/home/narolski/smad-next/src/AD5/score
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
SITE=/tmp/rs1_nosite
NAMES=${*:-"madation_B_s401 madation_B_s402 madation_B_s403 madation_B_s404 madation_B_s405 \
madation_L_s401 madation_L_s402 madation_L_s403 madation_L_s404 madation_L_s405 \
mixfacenet_X_s401 mixfacenet_X_s402 mixfacenet_X_s403 mixfacenet_X_s404 mixfacenet_X_s405"}
mkdir -p "$O" "$CF" "$SITE"
declare -A ARM=( [madation_B]=madation_vitb16 [madation_L]=madation_vitl14 [mixfacenet_X]=mixfacenet_mad_smdd )
declare -A KIND=( [madation_B]=madation [madation_L]=madation )
declare -A ARCH=( [madation_B]=vitb16 [madation_L]=vitl14 )

prep() {  # prep NAME -> echo weights file
  local n=$1 key arm tag
  key=${n%_s*}; arm=${key#*_}
  case $n in
    mixfacenet_X_*) key=mixfacenet_X ;;
    madation_*) key=madation_${arm} ;;
  esac
  local t=$(ls "$T" | grep -E "^${key}_${n##*_}\.tar$")
  [ -f "$CF/$n/.prepped" ] && { [[ $key = mixfacenet_X ]] && echo "$CF/$n/mixfacenet_SMDD.pth" || echo "$CF/$n/model.safetensors"; return; }
  rm -rf "$CF/$n"; mkdir -p "$CF/$n"
  tar -xf "$T/$t" -C "$CF/$n" || return 1
  if [ "$key" = mixfacenet_X ]; then
    echo "$CF/$n/mixfacenet_SMDD.pth"
  else
    "$PY" -I "$R/code/smadcvpr/a36_madation.py" convert --release "$n" --kind "${KIND[$key]}" --arch "${ARCH[$key]}" \
      --backbone "$CF/$n/40_backbone.pth" --header "$CF/$n/40_header.pth" --log "$CF/$n/training.log" \
      --out "$CF/$n" > "$CF/$n/convert.log" 2>&1 || { cat "$CF/$n/convert.log"; return 1; }
    echo "$CF/$n/model.safetensors"
  fi
  touch "$CF/$n/.prepped"
}

for n in $NAMES; do
  wf=$(prep "$n") || { echo "PREP_FAILED $n"; continue; }
  [ -f "$wf" ] || { echo "NO_WEIGHTS $n"; continue; }
  [ "$n" = mixfacenet_X_s401 ] && wl=$wf || wl=$wf   # placeholder, keep uniform
  for v in v1 v2; do
    [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && { echo "$n $v done"; continue; }
    tag=rel_${n}__ad5$v; t0=$(date +%s)
    for try in 1 2 3 4 5 6; do
      [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && break
      nice -n 10 "$PY" -I "$S/ad5_score_athena.py" "$R" "$SITE" --as "${ARM[${n%_s*}]}" --name "$n" --weights "$wf" \
        -- --mode rel --manifest "$W/score_$v.csv" --out-dir "$O" --tag "$tag" --workers 6 --bs 32 \
        > "$O/log_${tag}_try$try.log" 2>&1 && break
      echo "$tag try $try failed $(date +%T)"; tail -5 "$O/log_${tag}_try$try.log"; sleep 90
    done
    [ -f "$O/scores_rel_${n}__ad5$v.npz" ] && echo "$n $v scored $(( $(date +%s) - t0 ))s"
  done
done
echo RETRAINS_SCORING_DONE

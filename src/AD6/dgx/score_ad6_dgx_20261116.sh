#!/bin/bash
# AD6 H-sbr scoring on GB10 (2026-11-16): 15 matched-recipe retrains (madation_B_sbr / madation_L_sbr /
# mixfacenet_X_sbr, seeds 401-405, WCSS ad6w arrays) through the SAME Athena-registered scoring path as AD5
# (ad5_score_athena.py on the frozen RS1 regen crops, score_v1/score_v2 manifests) -> tags ad6v1/ad6v2.
# Prereg: experiments/AD6_matched-recipe-comparator-retrains/prereg.md. Distinct tag ("h_") keeps H-sbr rows
# separate from released-weights (RW) and H-native (AD5 rel_) rows.
#   score_ad6_dgx_20261116.sh [NAMES...]
# Space policy: /mnt/t7 is FULL (793MB free) -> everything written under /home/narolski/ad6_stage/.
# After a name has both v1+v2 npz + receipt line, its converted weights and pulled tar are DELETED to keep
# /home within budget; SHA256 of every npz is recorded in scores_h_sbr/RECEIPTS_sha256.csv first.
set -uo pipefail
R=/mnt/t7/smad_next/RS1/regen_pack
W=/mnt/t7/smad_next/RS1/regen_run
T=/home/narolski/ad6_stage/ad6_wcss_pull
CF=/home/narolski/ad6_stage/convert_h_sbr
O=/home/narolski/ad6_stage/scores_h_sbr
S=/home/narolski/smad-next/src/AD5/score
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
SITE=/tmp/rs1_nosite
NAMES=${*:-"madation_B_sbr_s401 madation_B_sbr_s402 madation_B_sbr_s403 madation_B_sbr_s404 madation_B_sbr_s405 \
madation_L_sbr_s401 madation_L_sbr_s402 madation_L_sbr_s403 madation_L_sbr_s404 madation_L_sbr_s405 \
mixfacenet_X_sbr_s401 mixfacenet_X_sbr_s402 mixfacenet_X_sbr_s403 mixfacenet_X_sbr_s404 mixfacenet_X_sbr_s405"}
mkdir -p "$O" "$CF" "$SITE"
declare -A AS=( [madation_B_sbr]=madation_vitb16 [madation_L_sbr]=madation_vitl14 [mixfacenet_X_sbr]=mixfacenet_mad_smdd )

prep() {  # prep NAME -> echo weights file ("" on failure)
  local n=$1 key=$1
  key=${n%_s[0-9][0-9][0-9]}          # madation_B_sbr | madation_L_sbr | mixfacenet_X_sbr
  [ -f "$CF/$n/.prepped" ] || {
    local t; t=$(ls "$T" | grep -E "^${n}.tar$") || return 1
    rm -rf "$CF/$n"; mkdir -p "$CF/$n"
    tar -xf "$T/$t" -C "$CF/$n" || return 1
    case $key in
      mixfacenet_X_sbr)
        [ -s "$CF/$n/mixfacenet_SMDD.pth" ] || return 1 ;;
      madation_*)
        [ -s "$CF/$n/1_backbone.pth" ] && [ -s "$CF/$n/1_header.pth" ] && [ -s "$CF/$n/training.log" ] || return 1
        local arch; arch=$([ $key = madation_L_sbr ] && echo vitl14 || echo vitb16)
        df --output=avail -BG /home | tail -1 | grep -qE '^[0-9]+' || return 1
        "$PY" -I "$R/code/smadcvpr/a36_madation.py" convert --release "$n" --kind madation --arch "$arch" \
          --backbone "$CF/$n/1_backbone.pth" --header "$CF/$n/1_header.pth" --log "$CF/$n/training.log" \
          --out "$CF/$n" > "$CF/$n/convert.log" 2>&1 || { cat "$CF/$n/convert.log"; return 1; }
        [ -s "$CF/$n/model.safetensors" ] || return 1 ;;
    esac
    touch "$CF/$n/.prepped"
  }
  case $key in
    mixfacenet_X_sbr) echo "$CF/$n/mixfacenet_SMDD.pth" ;;
    *)                echo "$CF/$n/model.safetensors" ;;
  esac
}

receipt() {  # NAME VERSION -> append sha256 + integrity line to receipts csv
  local n=$1 v=$2 f=$O/feat_h_${n}__ad6$v.npz
  [ -f "$f" ] || return 1
  $( $PY -I - "$f" <<'EOF' >/dev/null 2>&1
import sys, numpy as np
d = np.load(sys.argv[1], allow_pickle=True)
keys = sorted(d.files)
assert 'id' in keys and ('feat' in keys or any('score' in k for k in keys)), keys
sys.exit(0)
EOF
 ) || { echo "NPZ_CORRUPT $f"; return 1; }
  printf '%s,%s,%s\n' "feat_h_${n}__ad6$v.npz" "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c%s "$f")" \
    >> "$O/RECEIPTS_sha256.csv"
}

for n in $NAMES; do
  key=${n%_s[0-9][0-9][0-9]}
  v1=$O/feat_h_${n}__ad6v1.npz; v2=$O/feat_h_${n}__ad6v2.npz
  [ -f "$v1" ] && [ -f "$v2" ] && { echo "$n done already"; continue; }
  if [ ! -f "$T/$n.tar" ]; then echo "NO_TAR $n (fetch first)"; continue; fi
  wf=$(prep "$n") || { echo "PREP_FAILED $n"; continue; }
  [ -f "$wf" ] || { echo "NO_WEIGHTS $n"; continue; }
  for v in v1 v2; do
    npz=$O/feat_h_${n}__ad6$v.npz
    [ -f "$npz" ] && { receipt "$n" "$v" || true; continue; }
    tag=h_${n}__ad6$v; t0=$(date +%s)
    for try in 1 2 3 4 5 6; do
      [ -f "$npz" ] && break
      df --output=avail -BG /home | tail -1 | awk '{if ($1+0 < 6) exit 1}' || { echo "DISK_LOW /home, stop"; break 2; }
      nice -n 10 "$PY" -I "$S/ad5_score_athena.py" "$R" "$SITE" --as "${AS[$key]}" --name "$n" --weights "$wf" \
        -- --mode rel --manifest "$W/score_$v.csv" --out-dir "$O" --tag "$tag" --workers 6 --bs 32 \
        > "$O/log_${tag}_try$try.log" 2>&1 && break
      echo "$tag try $try failed $(date +%T)"; tail -5 "$O/log_${tag}_try$try.log"; sleep 90
    done
    receipt "$n" "$v" && echo "$n $v scored $(( $(date +%s) - t0 ))s"
  done
  if [ -f "$v1" ] && [ -f "$v2" ] && grep -q "^feat_h_${n}__ad6v2.npz," "$O/RECEIPTS_sha256.csv" 2>/dev/null; then
    rm -rf "$CF/$n" "$T/$n.tar" "$T/$n.tar.sha256"; echo "CLEANED weights+tar $n ($(df --output=avail -BG /home | tail -1)GB free)"
  fi
done
n=$(ls $O/feat_h_*__ad6*.npz 2>/dev/null | wc -l); echo "AD6_SCORE_PROGRESS npz=$n/60"
echo AD6_SCORING_DONE

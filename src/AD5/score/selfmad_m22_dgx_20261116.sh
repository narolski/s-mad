#!/bin/bash
# H5 (HOLDS_20261116.md): SelfMAD MAD22 cells on the canonical MAD22 crops (common-protocol scoring).
# Registered descriptive scoring, append-only, dated 2026-11-16. NOT a new training.
#   selfmad_m22_dgx_20261116.sh [NAMES...]
# What it does: score selfmad_hrnet_w18 (released RW row) + selfmad_S_s401..s405 (retrains) in score.py
# --mode rel on the SAME GB10-regen crops/manifests (score_v1.csv 28 253 / score_v2.csv 29 049 rows, id-space
# joins 100% to athena_manifest tags incl. M22_FaceMorpher/OpenCV/Webmorph/MIPGAN_I/II + G22 raw/aln).
# Output: /home/narolski/ad6_stage/scores_selfmad_m22/scores_rel_<name>__m22v{1,2}.npz (+ logs, receipts csv).
# /mnt/t7 is FULL — all writes under /home/narolski/ad6_stage/. Weights conversions are CPU-only
# (conv_selfmad was space-purged; re-converted from hash-verified tars in AD5/results).
set -uo pipefail
A=/mnt/t7/smad_next/AD5
R=/mnt/t7/smad_next/RS1/regen_run
T=/home/narolski/ad6_stage/scores_selfmad_m22
CF=$T/conv
O=$T
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/AD5/score
REL=/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors
NAMES=${*:-"selfmad_hrnet_w18 selfmad_S_s401 selfmad_S_s402 selfmad_S_s403 selfmad_S_s404 selfmad_S_s405"}
mkdir -p "$O/conv" "$O/parts"
for n in $NAMES; do
  if [ $n = selfmad_hrnet_w18 ]; then wf=$REL
  else
    (cd $A/results && sha256sum -c $n.tar.sha256 >/dev/null) || { echo "BAD_TAR $n"; continue; }
    d=$O/conv/$n
    if [ ! -f $d/model.safetensors ]; then
      mkdir -p $d; tar -xf $A/results/$n.tar -C $d || { echo "TAR_FAILED $n"; continue; }
      $PY -I $S/convert_selfmad.py $d/epoch_100.tar $d/model.safetensors $REL > $d/convert.json || { echo "CONVERT_FAILED $n"; continue; }
    fi
    wf=$d/model.safetensors
  fi
  for v in v1 v2; do
    npz=$O/scores_rel_${n}__m22$v.npz
    [ -f "$npz" ] && { echo "$n $v done"; continue; }
    tag=rel_${n}__m22$v; t0=$(date +%s)
    for try in 1 2 3 4 5 6; do
      [ -f "$npz" ] && break
      df --output=avail -BG /home | tail -1 | awk '{if ($1+0 < 6) exit 1}' || { echo "DISK_LOW /home"; break 2; }
      nice -n 15 "$PY" -I "$S/ad5_score_dgx.py" --name $n --weights $wf -- --mode rel \
        --manifest $R/score_$v.csv --out-dir "$O" --tag "$tag" --workers 4 --bs 32 \
        > "$O/log_${tag}_try$try.log" 2>&1 && break
      echo "$tag try $try failed $(date +%T)"; tail -5 "$O/log_${tag}_try$try.log"; sleep 90
    done
    [ -f "$npz" ] && printf '%s,%s,%s\n' "scores_rel_${n}__m22$v.npz" "$(sha256sum $npz | cut -c1-64)" "$(stat -c%s $npz)" >> $O/RECEIPTS_sha256.csv \
      && echo "$n $v scored $(( $(date +%s) - t0 ))s"
  done
done
n=$(ls $O/scores_rel_*__m22*.npz 2>/dev/null | wc -l); echo "SELFMAD_M22_PROGRESS npz=$n/12"
echo SELFMAD_M22_SCORING_DONE

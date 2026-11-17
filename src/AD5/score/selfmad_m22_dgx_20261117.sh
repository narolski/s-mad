#!/bin/bash
# H5 amendment 1 (2026-11-17) to selfmad_m22_dgx_20261116.sh (registered 9eb2a0c). Same scoring, same crops,
# same manifests, same frozen score.py/ar1_common.py pins, same metric. Three changes, all mechanical:
#  (a) score.py --mode rel resolves the architecture spec by --det name (a12_released.RELEASES); only the released
#      name "selfmad_hrnet_w18" is in that table, so retrains are scored as --name selfmad_hrnet_w18 with their own
#      --weights file (ad5_score_dgx.py overrides WEIGHTS/WEIGHT_SHA for that name and prints the weights sha256).
#      Output tags keep the retrain name: rel_<name>__m22v{1,2}.
#  (b) only the member ./epoch_100.tar is extracted from each 1.7 GB retrain archive (/home has ~12 GB free).
#  (c) seed 405 uses its already converted weights in /home/narolski/ad6_stage/selfmad_s405/conv
#      (convert.json: 1956/1956 tensors, same keys and shapes as the release); its archive is not on /mnt/t7.
#   selfmad_m22_dgx_20261117.sh NAMES...
set -uo pipefail
A=/mnt/t7/smad_next/AD5
R=/mnt/t7/smad_next/RS1/regen_run
O=/home/narolski/ad6_stage/scores_selfmad_m22
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/AD5/score
REL=/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors
S405=/home/narolski/ad6_stage/selfmad_s405/conv/model.safetensors
mkdir -p "$O/conv"
for n in "$@"; do
  if [ "$n" = selfmad_hrnet_w18 ]; then wf=$REL
  elif [ "$n" = selfmad_S_s405 ]; then wf=$S405
  else
    (cd $A/results && sha256sum -c $n.tar.sha256 >/dev/null) || { echo "BAD_TAR $n"; continue; }
    d=$O/conv/$n
    if [ ! -f $d/model.safetensors ]; then
      mkdir -p $d; tar -xf $A/results/$n.tar -C $d ./epoch_100.tar || { echo "TAR_FAILED $n"; continue; }
      $PY -I $S/convert_selfmad.py $d/epoch_100.tar $d/model.safetensors $REL > $d/convert.json || { echo "CONVERT_FAILED $n"; continue; }
    fi
    wf=$d/model.safetensors
  fi
  for v in v1 v2; do
    tag=rel_${n}__m22$v; npz=$O/scores_$tag.npz
    [ -f "$npz" ] && { echo "$n $v done"; continue; }
    t0=$(date +%s)
    for try in 1 2 3; do
      [ -f "$npz" ] && break
      df --output=avail -BG /home | tail -1 | awk '{if ($1+0 < 6) exit 1}' || { echo "DISK_LOW /home"; break 2; }
      nice -n 15 "$PY" -I "$S/ad5_score_dgx.py" --name selfmad_hrnet_w18 --weights $wf -- --mode rel \
        --manifest $R/score_$v.csv --out-dir "$O" --tag "$tag" --workers 4 --bs 32 \
        > "$O/log_${tag}_try$try.log" 2>&1 && break
      echo "$tag try $try failed $(date +%T)"; tail -5 "$O/log_${tag}_try$try.log"; sleep 60
    done
    [ -f "$npz" ] && printf '%s,%s,%s,%s\n' "scores_$tag.npz" "$(sha256sum $npz | cut -c1-64)" "$(stat -c%s $npz)" "$(sha256sum $wf | cut -c1-64)" >> $O/RECEIPTS_sha256.csv \
      && echo "$n $v scored $(( $(date +%s) - t0 ))s"
  done
done
echo "STREAM_DONE $* npz_total=$(ls $O/scores_rel_*__m22*.npz 2>/dev/null | wc -l)/12"

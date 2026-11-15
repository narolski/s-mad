#!/bin/bash
# SM1 A16 (DRAFT: DG1 rungs FRESH1/NOISES/NOISEX/SEMS/SEMX/MIR/REC20; derived from the A15 script, development data only): score the saved ViT-B/16 fits of arms a, e, f (seeds 401, 402) on the
# development diffusion ladder (DG1 add-on X20 / REC20 / SAME20 of 536 FRGC / colorFERET hosts), the AR1 camera photos
# (R0) and OpenCV morphs (R4), and the AF0 softened copies of both. No benchmark cell is scored. The network of each
# fit is rebuilt from its result tar (sm1_lora_audit.py: reproduction check on 256 stored AD4 rows, then the manifest).
# Inputs on the machine: /workspace/sm1r/results/SM1B_<arm>_s<seed>.tar, the unpacked packs, the dev files under
# data/x (checked by dev16_files.sha256), manifests/dev16/sm1_dev16_eval.csv. One tar + sha256 per fit: results_dev16/SM1E_*.
set -uo pipefail
B=/workspace/sm1r; OUT=$B/results_dev16; mkdir -p "$OUT" "$B/devfits"
[ -f "$B/ALL_DONE" ] || { echo "no fit tars staged"; exit 1; }
(cd "$B/data/x" && sha256sum -c --quiet "$B/manifests/dev16/dev16_files.sha256") || { echo "dev files hash mismatch"; exit 1; }
(cd "$B/manifests/dev16" && sha256sum -c --quiet sm1_dev16_eval.csv.sha256) || { echo "manifest hash mismatch"; exit 1; }
for F in SM1B_a_s401 SM1B_a_s402 SM1B_e_s401 SM1B_e_s402 SM1B_f_s401 SM1B_f_s402; do
  T=SM1E_${F#SM1B_}
  [ -e "$OUT/$T.tar" ] && { echo "done $T"; continue; }
  if ! (cd "$B/results" && sha256sum -c --quiet "$F.tar.sha256"); then echo "SKIP $F: tar missing or hash mismatch"; continue; fi
  rm -rf "$B/devfits/$F"; tar -C "$B/devfits" -xf "$B/results/$F.tar" || { echo "SKIP $F: untar"; continue; }
  W=$B/work/dev16_$F; rm -rf "$W"; mkdir -p "$W/data/manifests"
  ln -s "$B/data/x" "$W/data/x"                                       # no benchmark folder or manifest linked
  cp "$B/manifests/dev16/sm1_dev16_eval.csv" "$B/manifests/v2/sm1_ar1_eval.csv" "$W/data/manifests/"
  env SMAD_DATA=$W/data HF_HOME=$B/ad4/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 python "$B/bin/sm1_lora_audit.py" \
    --fit "$B/devfits/$F" --code "$B/ad4/code" --manifest sm1_dev16_eval.csv --out "$W/res/$T" --workers 6 \
    --check-npz ar1eval/scores_eval.npz --check-manifest sm1_ar1_eval.csv || { echo "SKIP $F: scoring failed"; rm -rf "$W"; continue; }
  tar -C "$W/res" -cf "$OUT/$T.tar" "$T"; (cd "$OUT" && sha256sum "$T.tar" > "$T.tar.sha256")
  rm -rf "$W" "$B/devfits/$F"
  echo "SM1E_FIT_DONE $T $(date -Is)"
done
echo SM1E_ALL_DONE; date > "$OUT/SM1E_ALL_DONE"

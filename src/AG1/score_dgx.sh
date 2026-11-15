#!/bin/bash
# AG1 scoring on the DGX GPU (GB10): the released detectors on manifests/ag1.csv through ag1_score.py (the registered
# A43 adapter over amendment G's a41g_score.py), one write-once npz per (release, mode).
# Usage: score_dgx.sh DATA_ROOT OUT_ROOT [release:mode ...]
#   DATA_ROOT  holds manifests/ag1.csv, the frames it names (relative paths) and AG1_data_pins.sha256
#   OUT_ROOT   gets jobroot/, A12REL/ and a41g_out/ag1/<release>/<mode>/scores_ag1.npz
# Releases: MADation from /mnt/t7/wcss_backups/madation_official_upload/madation_official.tar (A12REL/ inside);
# SelfMAD release from /mnt/t7/smad_next/AR1/weights/selfmad_release/ (sha256 0ad8db6f..., copied there by the AR1
# owner from WCSS A12REL); SelfMAD own crop needs the 81-landmark dlib model (/mnt/t7/thirdparty/dlib81_wcss_20261107).
set -euo pipefail
DATA=${1:?data root}; OUT=${2:?out root}; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
PY="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PRED=/mnt/t7/thirdparty/dlib81_wcss_20261107/shape_predictor_81_face_landmarks.dat
JOBS=("$@")
[ ${#JOBS[@]} -gt 0 ] || JOBS=(madation_vitb16:rel madation_vitl14:rel selfmad_hrnet_w18:rel selfmad_hrnet_w18:own
                                madation_fe_vitb16:rel madation_fe_vitl14:rel madation_fs_vitb16:rel madation_fs_vitl14:rel)
mkdir -p "$OUT"
[ -d "$OUT/jobroot" ] || bash "$HERE/make_score_root.sh" "$OUT/jobroot" "$DATA/AG1_data_pins.sha256"
for j in "${JOBS[@]}"; do                                   # extract only the releases asked for (disk)
  rel=${j%%:*}
  case $rel in madation_*) [ -d "$OUT/A12REL/$rel" ] || tar -xf /mnt/t7/wcss_backups/madation_official_upload/madation_official.tar -C "$OUT" "A12REL/$rel" ;; esac
done
if [ ! -s "$OUT/A12REL/selfmad_hrnet_w18/hrnet_w18_checkpoint.model.safetensors" ]; then
  mkdir -p "$OUT/A12REL/selfmad_hrnet_w18"
  cp /mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors "$OUT/A12REL/selfmad_hrnet_w18/"
fi
LIST=$OUT/jobroot/smadcvpr/plans/A36/A36_releases.tsv
cd "$OUT"
for j in "${JOBS[@]}"; do
  rel=${j%%:*}; mode=${j##*:}
  ck=$(awk -F'\t' -v r="$rel" '!/^#/ && $1 ~ ("/" r "$") {print $2}' "$LIST")
  o=$OUT/a41g_out/ag1/$rel/$mode/scores_ag1.npz
  [ -e "$o" ] && { echo "exists: $o"; continue; }
  extra=()
  [ "$mode" = own ] && extra=(--predictor "$PRED")
  SMAD_DATA=$DATA $PY -I "$OUT/jobroot/smadcvpr/ag1_score.py" --item ag1 --mode "$mode" \
    --ckpt "$OUT/A12REL/$rel/$ck" --list "$LIST" --manifest ag1.csv --out "$o" --workers 2 "${extra[@]}"
done

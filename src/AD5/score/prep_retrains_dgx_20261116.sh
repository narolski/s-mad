#!/bin/bash
# AD5 retrain prep on GB10 (2026-11-16): untar + a36 convert madation B/L s401–s405 (mixfacenet_X just untarred).
set -uo pipefail
CF=/mnt/t7/smad_next/RS1/convert_retrains
T=/mnt/t7/smad_next/AD5/results_athena_pull
R=/mnt/t7/smad_next/RS1/regen_pack
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
mkdir -p "$CF"
for n in madation_B_s401 madation_B_s402 madation_B_s403 madation_B_s404 madation_B_s405 \
         madation_L_s401 madation_L_s402 madation_L_s403 madation_L_s404 madation_L_s405; do
  [ -f "$CF/$n/.prepped" ] && { echo "$n prepared"; continue; }
  rm -rf "$CF/$n"; mkdir -p "$CF/$n"
  tar -xf "$T/$n.tar" -C "$CF/$n" || { echo "TAR_FAILED $n"; continue; }
  arch=$([ "${n#madation_}" = L ] && echo vitl14 || echo vitb16)
  "$PY" -I "$R/code/smadcvpr/a36_madation.py" convert --release "$n" --kind madation --arch "$arch" \
    --backbone "$CF/$n/40_backbone.pth" --header "$CF/$n/40_header.pth" --log "$CF/$n/training.log" \
    --out "$CF/$n" > "$CF/$n/convert.log" 2>&1 && touch "$CF/$n/.prepped" || { echo "CONVERT_FAILED $n"; tail -8 "$CF/$n/convert.log"; }
done
for n in mixfacenet_X_s401 mixfacenet_X_s402 mixfacenet_X_s403 mixfacenet_X_s404 mixfacenet_X_s405; do
  [ -f "$CF/$n/.prepped" ] && { echo "$n prepared"; continue; }
  rm -rf "$CF/$n"; mkdir -p "$CF/$n"
  tar -xf "$T/$n.tar" -C "$CF/$n" && touch "$CF/$n/.prepped" || echo "TAR_FAILED $n"
done
echo RETRAIN_PREP_DONE

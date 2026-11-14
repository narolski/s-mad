#!/bin/bash
set -euo pipefail
L=$G
P=$L/packs
PY=${PN1_PY:?}
R=${SPRINT_BATTERY_R:?}; RUN=${SPRINT_BATTERY_RUN:?}
get() { local t=$1 h=$2 d=$3 n; n=$(basename "$t"); cp "$t" "$W/$n"; [ "$(sha256sum "$W/$n" | cut -c1-64)" = "$h" ] || die "$n sha256"; mkdir -p "$d"; tar -C "$d" -xf "$W/$n"; rm -f "$W/$n"; }
die() { echo "SPRINT battery FAIL $*" >&2; exit 1; }
get "$P/TT1/tt1_pack.tar" 2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554 "$W"
(cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || die "TT1 pack SHA256SUMS"
get "$P/BB2/tt1m_meds.tar" 3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61 "$W"
(cd "$W/tt1m" && sha256sum -c --quiet SHA256SUMS) || die "MEDS pack SHA256SUMS"
get "$P/BB2/pr1_gd.tar" 40aa95d2b48719025bc3b80ebf9fa997bb1adf6c69da894120716a6e962b7329 "$W"
(cd "$W/pr1g" && sha256sum -c --quiet SHA256SUMS) || die "GD pack SHA256SUMS"
get "$P/BATTERY/battery_code_v1rc1.tar" 8a86676d17c2aea33ac5f05ee40589c2a199ff709982619f810f353cdc4615dd "$W/bcode"
cp "$L/results/AB1/AB1_Sb_s408.tar" "$W/AB1_Sb_s408.tar"
[ "$(sha256sum "$W/AB1_Sb_s408.tar" | cut -c1-64)" = a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa ] || die "reference pin"
cd "$W/bcode/src"
$PY -m battery.run --ckpt "$RUN" --arm "$ARM" --seed "$SEED" --out "$R/battery" --code "$W/pn1/code" --hf-home "$W/pn1/hf" --ref "$W/AB1_Sb_s408.tar" --data dev="$D" tt1="$W/tt1/data" meds="$W/tt1m/data" gd="$W/pr1g/data" --train-manifest "$D/manifests/train_Sb.csv" --expect-eval "$R/scores_eval.npz" --workers "${PN1_WORKERS:-7}" --stats no > "$R/battery.log" 2>&1

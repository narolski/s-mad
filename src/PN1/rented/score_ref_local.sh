#!/bin/bash
# PN1 amendment 5 task (rented machine copy of src/PN1/score_ref.sh): score the eight SMDD ViT-B/16 recipe retrains with pn1_score.py on the PN1 evaluation
# manifest, from the PN1 pack (eval images, code, weights) and refnets.tar; one result tar out. Container as run.sh.
set -euo pipefail
: "${TASK_WORK:?}"
G=/workspace/pn1/root
PACK=$G/packs/PN1/pn1_pack.tar
REFS=$G/packs/PN1/refnets.tar
OUT=$G/results/PN1
# rented machine: host Python instead of the container image (amendment 6); nothing else changed
W=$(cd -P "$TASK_WORK" && pwd)
die() { echo "PN1 REF FAIL: $*" >&2; exit 1; }
py() { python "$@"; }
T0=$SECONDS
[ -e "$OUT/PN1_REF_smdd_m3.tar" ] && { echo "already done"; exit 0; }
for f in "$PACK" "$REFS"; do
  cp "$f" "$W/"; b=$(basename "$f")
  [ "$(sha256sum "$W/$b" | cut -c1-64)" = "$(cut -c1-64 "$f.sha256")" ] || die "$b sha256"
  tar -C "$W" -xf "$W/$b" && rm -f "$W/$b"
done
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || die "pack content"
(cd "$W/refnets" && sha256sum -c --quiet SHA256SUMS) || die "refnets content"
D=$W/data; mkdir -p "$D/manifests"
ln -s "$W/pn1/data/eval" "$D/eval"; ln -s "$W/pn1/data/train" "$D/train"
for f in "$W"/pn1/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
head -2 "$W/pn1/data/manifests/train_A.csv" > "$D/manifests/ref_train1.csv"
export SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
mkdir -p "$W/res/PN1_REF_smdd_m3"
for d in "$W"/refnets/a12_*; do
  n=$(basename "$d")
  py "$W/pn1/src/pn1_score.py" --run "$d" --code "$W/pn1/code" --eval-manifest pn1_eval.csv \
    --train-manifest ref_train1.csv --out "$W/res/PN1_REF_smdd_m3/$n" --workers 7 --limit "${PN1_LIMIT:-0}"
  rm -f "$W/res/PN1_REF_smdd_m3/$n/last_trainable.pt"
done
echo "wall_s $((SECONDS - T0)) host $(hostname)" > "$W/res/PN1_REF_smdd_m3/task_info.txt"
tar -C "$W/res" -cf "$W/PN1_REF_smdd_m3.tar" PN1_REF_smdd_m3
cp "$W/PN1_REF_smdd_m3.tar" "$OUT/PN1_REF_smdd_m3.tar.part"
(cd "$W" && sha256sum PN1_REF_smdd_m3.tar) > "$W/PN1_REF_smdd_m3.tar.sha256"
[ "$(sha256sum "$OUT/PN1_REF_smdd_m3.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/PN1_REF_smdd_m3.tar.sha256")" ] || die "copy-back"
mv "$OUT/PN1_REF_smdd_m3.tar.part" "$OUT/PN1_REF_smdd_m3.tar"; cp "$W/PN1_REF_smdd_m3.tar.sha256" "$OUT/"
echo "PN1_REF_DONE wall $((SECONDS - T0)) s"

#!/bin/bash
# PN1 amendment 13 (rented): after the third queue (B rescoring, ALL_DONE3), score this machine's four tier-1 networks
# (A, B, Bn, C of SEED, from their result tars) on the HN2 FFHQ list (pn1_hn2.tar); code and CLIP weights from pack 2.
# One tar + .sha256 in results: PN1_HN2_s<SEED>.tar with scores_hn2_<arm>.npz. Args: SEED
set -u
B=/workspace/pn1; S=$1; T=PN1_HN2_s$S
PIN2=266ce5c352f1a04220d2025092ef92f973f0c8ecdc5872671a228819b189fce6
PINH=7648b15ac67798e7601e24b790e62ef86687949f9af0ac440065c2fcb6ac42a7
until [ -f "$B/ALL_DONE3" ]; do sleep 60; done
fail() { echo "FAIL $1" > "$B/rc/$T"; exit 1; }
[ "$(sha256sum < "$B/root/packs/PN1/pn1_hn2.tar" | cut -d' ' -f1)" = "$PINH" ] || fail pinh
W=$B/work/hn2; rm -rf "$W"; mkdir -p "$W/res/$T"
tar -C "$W" -xf "$B/root/packs/PN1/pn1_pack2.tar" pn1/code pn1/hf pn1/SHA256SUMS || fail pack2
(cd "$W/pn1" && grep -E "  (code|hf)/" SHA256SUMS | sha256sum -c --quiet) || fail pack2sums
tar -C "$W" -xf "$B/root/packs/PN1/pn1_hn2.tar" && (cd "$W/pn1h" && sha256sum -c --quiet SHA256SUMS) || fail hn2sums
D=$W/data; mkdir -p "$D/manifests"; ln -s "$W/pn1h/data/eval" "$D/eval"; ln -s "$W/pn1h/data/manifests/pn1_hn2.csv" "$D/manifests/pn1_hn2.csv"
for a in A B Bn C; do
  tar -C "$W" -xf "$B/root/results/PN1/PN1_${a}_s$S.tar" || fail "tar_$a"
  SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 python "$B/bin/rescore.py" --resdir "$W/PN1_${a}_s$S" --code "$W/pn1/code" \
    --manifest pn1_hn2.csv --fam ffhq --out "$W/res/$T/scores_hn2_$a.npz" >> "$B/logs/$T.log" 2>&1 || fail "score_$a"
done
echo 0 > "$B/rc/$T"
cp "$B/logs/$T.log" "$W/res/$T/"; nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$W/res/$T/gpu.txt"
tar -C "$W/res" -cf "$B/root/results/PN1/$T.tar" "$T"; (cd "$B/root/results/PN1" && sha256sum "$T.tar" > "$T.tar.sha256")
rm -rf "$W"; date > "$B/ALL_DONE4"

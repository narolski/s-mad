#!/bin/bash
# PN1 amendment 10 (rented): after the second queue, rescore this machine's B network (from its result tar) on the
# spliced and blanked evaluation rows of pack 2; one tar + .sha256 in results. Args: SEED
set -u
B=/workspace/pn1; S=$1; T=PN1_Brescore_s$S
until [ -f "$B/ALL_DONE2" ]; do sleep 60; done
W=$B/work/rescore; rm -rf "$W"; mkdir -p "$W/res/$T"
tar -C "$W" -xf "$B/root/packs/PN1/pn1_pack2.tar" && (cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || { echo FAIL > "$B/rc/$T"; exit 1; }
tar -C "$W" -xf "$B/root/results/PN1/PN1_B_s$S.tar"
D=$W/data; mkdir -p "$D/manifests"; ln -s "$W/pn1/data/eval" "$D/eval"; ln -s "$W/pn1/data/manifests/pn1_eval.csv" "$D/manifests/pn1_eval.csv"
SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 python "$B/bin/rescore.py" --resdir "$W/PN1_B_s$S" --code "$W/pn1/code" \
  --out "$W/res/$T/scores_splice.npz" > "$B/logs/$T.log" 2>&1; rc=$?
echo $rc > "$B/rc/$T"; [ $rc -eq 0 ] || exit 1
cp "$B/logs/$T.log" "$W/res/$T/"
tar -C "$W/res" -cf "$B/root/results/PN1/$T.tar" "$T"; (cd "$B/root/results/PN1" && sha256sum "$T.tar" > "$T.tar.sha256")
rm -rf "$W"; date > "$B/ALL_DONE3"

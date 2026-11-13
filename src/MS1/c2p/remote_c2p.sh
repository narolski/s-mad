#!/bin/bash
# DRAFT, not run (contrast 2-prime, prereg_contrast2prime_draft.md): on the MS1 rented host after its queue ended,
# under the host lock: score the 15 FS1 checkpoints (A, B, Sb x seeds 403-407; meta.json + last_trainable.pt from
# their result tars) with the unchanged src/PN1/rescore.py on (a) the platform-gate rows of the FS1 manifest
# (fam af0, 1,339; fam ffhq, 5,000; both already scored by these networks on the A100) and (b) the MS1 FFHQ hold-out
# (fam ms1ffhq, 1,480), all from the MS1 fit pack already on the host. One tar C2P_<Q>.tar (+ .sha256).
#   bash remote_c2p.sh PACKPIN Q
set -u
B=${MS1_B:-/workspace/ms1}; PIN=${1:?pack pin}; Q=${2:?queue}
exec 9> "$B/ms1_queue.lock"; flock 9
[ -f "$B/ALL_DONE_$Q" ] || { echo "queue $Q not ended"; exit 1; }
cd "$B/root/packs/MS1" && [ "$(cut -c1-64 pn1_pack_ms1.tar.sha256)" = "$PIN" ] || exit 1
C=$B/c2p; mkdir -p "$C/out" "$C/nets"
[ -d "$C/pn1" ] || { tar -C "$C" -xf pn1_pack_ms1.tar && (cd "$C/pn1" && sha256sum -c --quiet SHA256SUMS) || { echo "pack bad"; exit 1; }; }
(cd "$B/fs1" && sha256sum -c --quiet fs1_tars.sha256) || { echo "FS1 tars bad"; exit 1; }
D=$C/data; mkdir -p "$D/manifests"; ln -sfn "$C/pn1/data/eval" "$D/eval"; ln -sf "$C/pn1/data/manifests/pn1_eval.csv" "$D/manifests/pn1_eval.csv"
python -c "import sys, torch, timm; print('env', sys.version.split()[0], torch.__version__, timm.__version__, 'tf32', torch.backends.cuda.matmul.allow_tf32)" > "$C/out/env.txt"
nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$C/out/gpu.txt" 2>&1 || true
for T in $(cd "$B/fs1" && ls PN1_*_s40[3-7].tar | sed 's/\.tar$//'); do
  tar -C "$C/nets" -xf "$B/fs1/$T.tar" "$T/meta.json" "$T/last_trainable.pt"
  for FAM in af0 ffhq ms1ffhq; do
    SMAD_DATA=$D HF_HOME=$C/pn1/hf HF_HUB_OFFLINE=1 python "$B/held/pn1/src/rescore.py" --resdir "$C/nets/$T" --code "$C/pn1/code" \
      --manifest pn1_eval.csv --fam "$FAM" --out "$C/out/C2P_${T}_${FAM}.npz" --workers 7 >> "$B/logs/c2p_$Q.log" 2>&1 \
      || echo "$(date +%T) $T $FAM failed" >> "$B/logs/c2p_$Q.log"
  done
done
tar -C "$C" -cf "$B/root/results/C2P_$Q.tar" out && (cd "$B/root/results" && sha256sum "C2P_$Q.tar" > "C2P_$Q.tar.sha256")
date > "$B/C2P_DONE_$Q"

#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2-c2p
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:30:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-c2p-%j.out
# Second backbone (BB2), amendments 1-2: score the BB2 networks (meta.json + last_trainable.pt from their verified
# result tars) with the unchanged src/PN1/rescore.py (6f6eede7) on (a) the platform-gate rows (fam af0 1,339, ffhq
# 5,000; already scored by pn1_score.py in each fit) and (b) the MS1 FFHQ hold-out (fam ms1ffhq, 1,480), with TF32 on
# through the unchanged wrapper src/TT1/rescore_tf32.py (0d0b6b6f; pn1_score.py's numerics; review fix F1), from the
# MS1 fit pack (c11b16bc..., same code and evaluation rows as C2P) with the BB2 overlay unpacked over it. Submitted only
# after every fit of the read set has ended; exits within a minute if a listed tar is missing or off its sha256.
# Overrides (registered, review fix F3/F4): BB2_TASKS (default: the 9 registered tasks; amendment 2: the 15),
# BB2_C2P_RESULTS (default results/BB2; the smoke uses results/BB2_smoke), BB2_C2P_OUT (default BB2C2P).
# One tar out: $BB2_C2P_RESULTS/$BB2_C2P_OUT.tar (+ .sha256). All IO in $TMPDIR.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2; R=${BB2_C2P_RESULTS:-$L/results/BB2}; OUTN=${BB2_C2P_OUT:-BB2C2P}
fail() { echo "BB2_C2P_FAIL $*"; exit 1; }
[ -e "$R/$OUTN.tar" ] && fail "$OUTN.tar exists (never overwritten)"
(cd "$L/packs/MS1" && sha256sum -c pn1_pack_ms1.tar.sha256) && [ "$(cut -c1-64 $L/packs/MS1/pn1_pack_ms1.tar.sha256)" = c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d ] || fail "MS1 pack"
(cd "$P" && sha256sum -c bb2_overlay.tar.sha256 rescore.py.sha256 rescore_tf32.py.sha256) || fail "overlay, rescore.py or wrapper"
[ "$(cut -c1-64 $P/rescore_tf32.py.sha256)" = 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 ] || fail "wrapper pin"
[ "$(cut -c1-64 $P/rescore.py.sha256)" = 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e ] || fail "rescore.py pin"
TASKS=${BB2_TASKS:-"BB2_A_s403 BB2_B_s403 BB2_Sb_s403 BB2_A_s404 BB2_B_s404 BB2_Sb_s404 BB2_A_s405 BB2_B_s405 BB2_Sb_s405"}
for T in $TASKS; do [ -f "$R/$T.tar" ] && (cd "$R" && sha256sum -c --quiet "$T.tar.sha256") || fail "$T tar"; done
hostname; nvidia-smi --query-gpu=name,uuid --format=csv,noheader; date -Is
C=$TMPDIR/c; mkdir -p "$C/out" "$C/nets"
cp "$L/packs/MS1/pn1_pack_ms1.tar" "$TMPDIR/" && tar -C "$C" -xf "$TMPDIR/pn1_pack_ms1.tar" && rm -f "$TMPDIR/pn1_pack_ms1.tar"
(cd "$C/pn1" && sha256sum -c --quiet SHA256SUMS) || fail "MS1 pack content"
[ "$(sha256sum $C/pn1/code/smadcvpr/archs_a12.py | cut -c1-64)" = bedfeb86af2c92aed717e4f43e0b6c466306756d911afc93bcbdd1aae9994876 ] || fail "MS1 archs_a12.py is not the pinned one"
tar -C "$C" -xf "$P/bb2_overlay.tar" && (cd "$C/pn1" && sha256sum -c --quiet BB2SUMS) || fail "overlay content"
D=$C/data; mkdir -p "$D/manifests"; ln -sfn "$C/pn1/data/eval" "$D/eval"; ln -sf "$C/pn1/data/manifests/pn1_eval.csv" "$D/manifests/pn1_eval.csv"
PY=$HOME/dmenv/bin/python
$PY -c "import sys, torch, timm; torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True; print('env', sys.version.split()[0], torch.__version__, timm.__version__, 'tf32 matmul', torch.backends.cuda.matmul.allow_tf32, 'cudnn', torch.backends.cudnn.allow_tf32, 'via rescore_tf32.py 0d0b6b6f')" > "$C/out/env.txt"
(cd "$P" && sha256sum rescore_tf32.py rescore.py) >> "$C/out/env.txt"     # amendment 2 fix 5: the scorer actually run
nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$C/out/gpu.txt" 2>&1 || true
n_fail=0
for T in $TASKS; do
  tar -C "$C/nets" -xf "$R/$T.tar" "$T/meta.json" "$T/last_trainable.pt"
  for FAM in af0 ffhq ms1ffhq; do
    SMAD_DATA=$D HF_HOME=$C/pn1/hf HF_HUB_OFFLINE=1 $PY "$P/rescore_tf32.py" "$P/rescore.py" --resdir "$C/nets/$T" --code "$C/pn1/code" \
      --manifest pn1_eval.csv --fam "$FAM" --out "$C/out/C2P_${T}_${FAM}.npz" --workers 7 >> "$C/out/rescore.log" 2>&1 \
      || { echo "$(date +%T) $T $FAM failed" | tee -a "$C/out/rescore.log"; n_fail=$((n_fail+1)); }
  done
done
echo "$TASKS" > "$C/out/tasks.txt"
tar -C "$C" -cf "$TMPDIR/$OUTN.tar" out && (cd "$TMPDIR" && sha256sum $OUTN.tar > $OUTN.tar.sha256)
cp "$TMPDIR/$OUTN.tar" "$R/$OUTN.tar.part" && [ "$(sha256sum "$R/$OUTN.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$TMPDIR/$OUTN.tar.sha256")" ] \
  && mv "$R/$OUTN.tar.part" "$R/$OUTN.tar" && cp "$TMPDIR/$OUTN.tar.sha256" "$R/" || fail "copy-back"
echo "BB2_C2P_DONE failures $n_fail $(date -Is)"

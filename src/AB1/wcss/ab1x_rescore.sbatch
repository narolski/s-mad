#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J ab1x-rescore
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-01:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1x-rescore-%j.out
# AB1 border-crossed arm (prereg_x.md): score the comparison networks AB1 Sb and B at seeds 408-412 (H100 fits, verified
# tars in results/AB1) on the border rows (fam border, 3,582) and, as a job-path check, on landmark_combined (fam
# ffhq_lcomb, 3,000; already scored in their fit jobs) with the unchanged src/PN1/rescore.py (6f6eede7) through
# src/TT1/rescore_tf32.py (0d0b6b6f; TF32 on, as pn1_score.py), from the FS1 pack + the AB1X overlay. Owner: AB1 owner.
# All inputs exist now (no dependency on the Sbx fits); exits within a minute if one is missing. One tar out.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/AB1; R=$L/results/AB1; O=$L/results/AB1X; OUTN=AB1Xrescore
fail() { echo "AB1X_RESCORE_FAIL $*"; exit 1; }
mkdir -p "$O"
[ -e "$O/$OUTN.tar" ] && fail "$OUTN.tar exists (never overwritten)"
[ "$(sha256sum $L/packs/BB2/pn1_pack_fs.tar | cut -c1-64)" = 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 ] || fail "FS1 pack"
[ "$(sha256sum $P/ab1x_overlay.tar | cut -c1-64)" = e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c ] || fail "overlay pin"
[ "$(sha256sum $P/rescore.py | cut -c1-64)" = 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e ] || fail "rescore.py pin"
[ "$(sha256sum $P/rescore_tf32.py | cut -c1-64)" = 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 ] || fail "wrapper pin"
TASKS="AB1_Sb_s408 AB1_Sb_s409 AB1_Sb_s410 AB1_Sb_s411 AB1_Sb_s412 AB1_B_s408 AB1_B_s409 AB1_B_s410 AB1_B_s411 AB1_B_s412"
for T in $TASKS; do [ -f "$R/$T.tar" ] && (cd "$R" && sha256sum -c --quiet "$T.tar.sha256") || fail "$T tar"; done
hostname; nvidia-smi --query-gpu=name,uuid --format=csv,noheader; date -Is
C=$TMPDIR/c; mkdir -p "$C/out" "$C/nets"
cp "$L/packs/BB2/pn1_pack_fs.tar" "$TMPDIR/" && tar -C "$C" -xf "$TMPDIR/pn1_pack_fs.tar" && rm -f "$TMPDIR/pn1_pack_fs.tar"
(cd "$C/pn1" && sha256sum -c --quiet SHA256SUMS) || fail "FS1 pack content"
tar -C "$C" --skip-old-files -xf "$P/ab1x_overlay.tar" && (cd "$C/pn1" && sha256sum -c --quiet AB1XSUMS) || fail "overlay content"
D=$C/data; mkdir -p "$D/manifests"; ln -sfn "$C/pn1/data/eval" "$D/eval"; ln -sf "$C/pn1/data/manifests/ab1x_eval.csv" "$D/manifests/ab1x_eval.csv"
PY=$HOME/dmenv/bin/python
nvidia-smi --query-gpu=uuid,name,driver_version --format=csv,noheader > "$C/out/gpu.txt" 2>&1 || true
$PY -c "import sys, torch, timm; print(sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__)" > "$C/out/env.txt" 2>&1 || true
n_fail=0
for T in $TASKS; do
  tar -C "$C/nets" -xf "$R/$T.tar" "$T/meta.json" "$T/last_trainable.pt"
  for FAM in border ffhq_lcomb; do
    SMAD_DATA=$D HF_HOME=$C/pn1/hf HF_HUB_OFFLINE=1 $PY "$P/rescore_tf32.py" "$P/rescore.py" --resdir "$C/nets/$T" --code "$C/pn1/code" \
      --manifest ab1x_eval.csv --fam "$FAM" --out "$C/out/X_${T}_${FAM}.npz" --workers 7 >> "$C/out/rescore.log" 2>&1 \
      || { echo "$(date +%T) $T $FAM failed" | tee -a "$C/out/rescore.log"; n_fail=$((n_fail+1)); }
  done
done
tar -C "$C" -cf "$TMPDIR/$OUTN.tar" out && (cd "$TMPDIR" && sha256sum $OUTN.tar > $OUTN.tar.sha256)
cp "$TMPDIR/$OUTN.tar" "$O/$OUTN.tar.part" && [ "$(sha256sum "$O/$OUTN.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$TMPDIR/$OUTN.tar.sha256")" ] \
  && mv "$O/$OUTN.tar.part" "$O/$OUTN.tar" && cp "$TMPDIR/$OUTN.tar.sha256" "$O/" || fail "copy-back"
echo "AB1X_RESCORE_DONE failures $n_fail $(date -Is)"

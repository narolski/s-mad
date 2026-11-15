#!/bin/bash
#SBATCH --extra=FORCE_RM_TMPDIR
#SBATCH -J bb2-e2
#SBATCH -p lem-gpu-short
#SBATCH -N 1
#SBATCH -c 8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:hopper:1,storage:local:80G
#SBATCH --no-requeue
#SBATCH --time=0-03:00:00
#SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-e2-%j.out
# BB2 amendment 5 (E2): zero-LoRA ablation of the 15 BB2 DINOv3 networks (results/BB2) and the 15 FS1 CLIP networks
# (packs/BB2/clip_fs1, tars copied from the DGX with sha256), plus the frozen DINOv3 features of train_Sb; CLIP nets
# also rescored with LoRA on the platform-gate rows. src/BB2/e2_score.py (sha256 pinned below) on the FS1 pack with the
# BB2 overlay. GPU name asserted and precision logged (precision_probe.py). All IO in $TMPDIR; one tar out:
# results/BB2/BB2E2.tar (+ .sha256). Overrides for the smoke: BB2_E2_TARS (space-separated tar paths), BB2_E2_OUT,
# BB2_E2_LIMIT (rows per set; default 0 = all). Exits within a minute if anything is missing or off its sha256.
set -uo pipefail
: "${TMPDIR:?no TMPDIR}"
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/BB2; R=$L/results/BB2; OUTN=${BB2_E2_OUT:-BB2E2}
fail() { echo "BB2_E2_FAIL $*"; exit 1; }
[ -e "$R/$OUTN.tar" ] && fail "$OUTN.tar exists (never overwritten)"
(cd "$P" && sha256sum -c pn1_pack_fs.tar.sha256 bb2_overlay.tar.sha256 e2_score.py.sha256 precision_probe.py.sha256) || fail "pack, overlay, e2_score.py or probe"
[ "$(cut -c1-64 $P/e2_score.py.sha256)" = d183171829ea07abbd13d47fca3548498cafb6c170ebaa6ed3db1d32ea1f8a99 ] || fail "e2_score.py pin"
[ "$(cut -c1-64 $P/precision_probe.py.sha256)" = b49c1e704bc8957db76398abfd5ab54218ee152ac32ed9e061c634378148605e ] || fail "probe pin"
DEF=""
for s in 403 404 405 406 407; do for a in A B Sb; do DEF="$DEF $R/BB2_${a}_s$s.tar"; done; done
for s in 403 404 405 406 407; do for a in A B Sb; do DEF="$DEF $P/clip_fs1/PN1_${a}_s$s.tar"; done; done
TARS=${BB2_E2_TARS:-$DEF}
for t in $TARS; do [ -f "$t" ] && (cd "$(dirname "$t")" && sha256sum -c --quiet "$(basename "$t").sha256") || fail "$t"; done
hostname; date -Is
W=$TMPDIR/w; mkdir -p "$W"
cp "$P/pn1_pack_fs.tar" "$TMPDIR/" && tar -C "$W" -xf "$TMPDIR/pn1_pack_fs.tar" && rm -f "$TMPDIR/pn1_pack_fs.tar"
(cd "$W/pn1" && sha256sum -c --quiet SHA256SUMS) || fail "FS1 pack content"
tar -C "$W" -xf "$P/bb2_overlay.tar" && (cd "$W/pn1" && sha256sum -c --quiet BB2SUMS) || fail "overlay content"
D=$W/data; mkdir -p "$D/manifests"; ln -s "$W/pn1/data/train" "$D/train"; ln -s "$W/pn1/data/eval" "$D/eval"
for f in "$W"/pn1/data/manifests/*.csv; do ln -s "$f" "$D/manifests/$(basename "$f")"; done
O=$TMPDIR/out; mkdir -p "$O"
PY=$HOME/dmenv/bin/python
$PY -I "$P/precision_probe.py" --expect-gpu "NVIDIA H100" > "$O/precision.txt" 2>&1 || fail "GPU or probe: $(tail -1 $O/precision.txt)"
(cd "$P" && sha256sum e2_score.py precision_probe.py) > "$O/scripts.sha256"
nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$O/gpu.txt" 2>&1 || true
SMAD_DATA=$D HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 $PY -I "$P/e2_score.py" --code "$W/pn1/code" --out "$O" --tars $TARS \
  --workers 7 --limit "${BB2_E2_LIMIT:-0}" > "$O/e2.log" 2>&1
rc=$?; echo "e2_score rc $rc"; tail -3 "$O/e2.log"
rm -rf "$O/_nets"
tar -C "$TMPDIR" -cf "$TMPDIR/$OUTN.tar" out && (cd "$TMPDIR" && sha256sum $OUTN.tar > $OUTN.tar.sha256)
cp "$TMPDIR/$OUTN.tar" "$R/$OUTN.tar.part" && [ "$(sha256sum "$R/$OUTN.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$TMPDIR/$OUTN.tar.sha256")" ] \
  && mv "$R/$OUTN.tar.part" "$R/$OUTN.tar" && cp "$TMPDIR/$OUTN.tar.sha256" "$R/" || fail "copy-back"
echo "BB2_E2_DONE rc $rc $(date -Is)"
exit $rc

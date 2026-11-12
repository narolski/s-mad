#!/bin/bash
# BB2 overlay: the files that turn the unchanged FS1 pack (pn1_pack_fs.tar, 96c31ae2...) into the BB2 pack when unpacked
# over it: pn1/code/smadcvpr/archs_a12.py (src/BB2/archs_a12.py: the pinned bedfeb86... plus the DINOv3 entry) and
# pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors (timm hub file, snapshot 30c11095..., sha256 45172f20...), with
# pn1/BB2SUMS (sha256 of both). Deterministic tar (sorted names, mtime 0, numeric owner 0).
# Usage: build_overlay.sh OUTDIR   -> OUTDIR/bb2_overlay.tar + .sha256
set -euo pipefail
OUT=${1:?outdir}
SRC=$(cd "$(dirname "$0")" && pwd)
WEIGHTS=/home/narolski/.cache/huggingface/hub/models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots/30c1109559f65dea34316b0d4842d35c5771fe11/model.safetensors
WSHA=45172f209c9583c40538afc26b60a07033e6fcc2e8c30228338e6b2e932e7941
PINNED_ARCHS=bedfeb86af2c92aed717e4f43e0b6c466306756d911afc93bcbdd1aae9994876
S=$OUT/overlay_stage
rm -rf "$S"; mkdir -p "$S/pn1/code/smadcvpr" "$S/pn1/hf/a12"
cp "$SRC/archs_a12.py" "$S/pn1/code/smadcvpr/archs_a12.py"
cp "$WEIGHTS" "$S/pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors"
[ "$(sha256sum "$S/pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors" | cut -c1-64)" = "$WSHA" ] || { echo "weights sha256 off"; exit 1; }
[ "$(sha256sum "$S/pn1/code/smadcvpr/archs_a12.py" | cut -c1-64)" != "$PINNED_ARCHS" ] || { echo "archs_a12.py is the pinned file"; exit 1; }
(cd "$S/pn1" && sha256sum code/smadcvpr/archs_a12.py hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors > BB2SUMS)
tar -C "$S" --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner -cf "$OUT/bb2_overlay.tar" \
  pn1/BB2SUMS pn1/code/smadcvpr/archs_a12.py pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors
(cd "$OUT" && sha256sum bb2_overlay.tar > bb2_overlay.tar.sha256)
rm -rf "$S"
cat "$OUT/bb2_overlay.tar.sha256"
tar -tvf "$OUT/bb2_overlay.tar"

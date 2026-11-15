#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): build the one tar pack for Athena on the DGX.
# Contents (root dg1pack/): repo/ (the pinned DiffAE checkout with .git, no __pycache__), repo_manifest.sha256 (every
# tracked file), ckpt/last.ckpt, inputs/a256/ (204 FRLL X3 a256 photos + the DiffAE-aligned FRGC / colorFERET photos),
# jobs/*.csv, code/dg1_gen.py, MANIFEST.sha256 (every file). Output: /mnt/t7/smad_next/DG1/packs/dg1_pack.tar + .sha256.
set -euo pipefail
D=/mnt/t7/smad_next/DG1
T=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4
X3A=/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256
B=$D/pack_build
P=$B/dg1pack
[ ! -e "$D/packs/dg1_pack.tar" ] || { echo "refused: $D/packs/dg1_pack.tar exists (move it aside first)"; exit 1; }
rm -rf "$B"; mkdir -p "$P/ckpt" "$P/inputs/a256" "$P/jobs" "$P/code" "$D/packs"
rsync -a --exclude __pycache__ "$T/repo/" "$P/repo/"
git -C "$P/repo" rev-parse HEAD
[ -z "$(git -C "$P/repo" status --porcelain)" ] || { echo "repo copy not clean"; exit 1; }
( cd "$P/repo" && git ls-files -z | xargs -0 sha256sum ) > "$P/repo_manifest.sha256"
cp "$T/checkpoints_download/ffhq256_autoenc/last.ckpt" "$P/ckpt/"
cp "$X3A"/*.png "$P/inputs/a256/"
cp "$D"/pool_a256/*.png "$P/inputs/a256/"
cp "$D"/jobs/*.csv "$P/jobs/"
cp /home/narolski/smad-next/src/DG1/dg1_gen.py "$P/code/"
( cd "$P" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum ) > "$P/MANIFEST.sha256"
tar -C "$B" -cf "$D/packs/dg1_pack.tar" dg1pack
( cd "$D/packs" && sha256sum dg1_pack.tar > dg1_pack.tar.sha256 && cat dg1_pack.tar.sha256 )
ls -l "$D/packs/dg1_pack.tar"; ls "$P/inputs/a256" | wc -l
rm -rf "$B"

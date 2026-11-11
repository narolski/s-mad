#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1), amendment 2: the small add-on pack (root dg1addon/: code/dg1_addon.py,
# jobs/addon_*.csv, MANIFEST.sha256) -> /mnt/t7/smad_next/DG1/packs/dg1_addon_pack.tar (+ .sha256). Used beside the
# unchanged base pack dg1_pack.tar (checkpoint, inputs, DiffAE repo).
set -euo pipefail
D=/mnt/t7/smad_next/DG1
B=$D/addon_pack_build
P=$B/dg1addon
[ ! -e "$D/packs/dg1_addon_pack.tar" ] || { echo "refused: $D/packs/dg1_addon_pack.tar exists"; exit 1; }
rm -rf "$B"; mkdir -p "$P/code" "$P/jobs"
cp /home/narolski/smad-next/src/DG1/dg1_addon.py "$P/code/"
cp "$D"/addon_jobs/addon_s*.csv "$D"/addon_jobs/addon_test8.csv "$P/jobs/"
( cd "$P" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum ) > "$P/MANIFEST.sha256"
tar -C "$B" -cf "$D/packs/dg1_addon_pack.tar" dg1addon
( cd "$D/packs" && sha256sum dg1_addon_pack.tar > dg1_addon_pack.tar.sha256 && cat dg1_addon_pack.tar.sha256 )
rm -rf "$B"

#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1): the 8-image check of the real command line on the DGX (shared
# GB10), before any Athena job. Inputs = one folder of symlinks to the FRLL X3 a256 photos and the DiffAE-aligned pool
# photos (the pack's inputs/a256 layout). Environment = the A43 DiffAE venv. Then the manifest / validity script on the
# output (DGX GPU, glintr100). Outputs under /mnt/t7/smad_next/DG1/dgx_test/.
set -euo pipefail
D=/mnt/t7/smad_next/DG1
T=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4
S=/home/narolski/smad-next/src/DG1
O=$D/dgx_test
[ ! -e "$O/gen" ] || { echo "refused: $O/gen exists"; exit 1; }
mkdir -p "$O/inputs_a256" "$O/run"
for f in /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256/*.png "$D"/pool_a256/*.png; do
  ln -sf "$f" "$O/inputs_a256/$(basename "$f")"
done
[ -f "$D/repo_manifest.sha256" ] || ( cd "$T/repo" && git ls-files -z | xargs -0 sha256sum ) > "$D/repo_manifest.sha256"
cd "$O/run"
/mnt/t7/thirdparty/diffae_venv/bin/python -I "$S/dg1_gen.py" --repo "$T/repo" --repo-manifest "$D/repo_manifest.sha256" \
  --ckpt "$T/checkpoints_download/ffhq256_autoenc/last.ckpt" --inputs "$O/inputs_a256" --jobs "$D/jobs/smoke8.csv" \
  --out-root "$O/gen/smoke8" --bs 16 2>&1 | tee "$O/gen_smoke8.log"
/home/narolski/mambamorph-code/.venv-spark/bin/python -I "$S/dg1_validity.py" manifest --gen-root "$O/gen" \
  --pool /home/narolski/smad-next/experiments/AR1/pool.csv --out-dir "$O/validity" --gen-run dgx_test 2>&1 | tee "$O/validity.log"

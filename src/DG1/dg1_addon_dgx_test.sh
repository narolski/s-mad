#!/bin/bash
# Diffusion-autoencoder generation on Athena (DG1), amendment 2: the 8-image check of dg1_addon.py on the DGX with its
# real command line (9 jobs of addon_test8.csv: every mode, a second fresh draw, one 100-step render), retried on a
# CUDA out-of-memory at model load (shared GB10; the output folder is created only after the model is on the GPU).
T=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4
O=/mnt/t7/smad_next/DG1/dgx_test
cd "$O/run"
for i in 1 2 3 4 5 6; do
  [ -e "$O/addon_test8" ] && break
  /mnt/t7/thirdparty/diffae_venv/bin/python -I /home/narolski/smad-next/src/DG1/dg1_addon.py --repo "$T/repo" \
    --repo-manifest /mnt/t7/smad_next/DG1/repo_manifest.sha256 --ckpt "$T/checkpoints_download/ffhq256_autoenc/last.ckpt" \
    --inputs "$O/inputs_a256" --jobs /mnt/t7/smad_next/DG1/addon_jobs/addon_test8.csv --out-root "$O/addon_test8" --bs 16 \
    > "$O/addon_test8_attempt$i.log" 2>&1 && { echo "attempt $i ok"; exit 0; }
  echo "attempt $i failed: $(grep -m1 -o 'out of memory' "$O/addon_test8_attempt$i.log")"
  grep -q "out of memory" "$O/addon_test8_attempt$i.log" || exit 1
  [ -e "$O/addon_test8" ] && exit 1
  sleep 60
done
exit 1

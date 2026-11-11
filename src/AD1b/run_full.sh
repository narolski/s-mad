#!/bin/bash
# AD1b full run with retry on CUDA OOM at start-up (shared GB10); stops once the output folder exists.
T=/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4
O=/mnt/t7/smad_next/AD1b
cd $T/run
for i in $(seq 1 30); do
  [ -e $O/gen ] && break
  /mnt/t7/thirdparty/diffae_venv/bin/python -I /home/narolski/smad-next/src/AD1b/ad1b_gen.py --repo $T/repo \
    --ckpt $T/checkpoints_download/ffhq256_autoenc/last.ckpt --a256 /mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256 \
    --pool-a256 $O/pool_a256 --pool-sel $O/pool_selection.csv --self-pairs /mnt/t7/smad_heldout/a41_diffae/data/provenance/self_pairs.csv \
    --out-root $O/gen --n-img 32 --n-xt 16 > $O/gen_attempt$i.log 2>&1 && { echo "attempt $i ok"; exit 0; }
  echo "attempt $i failed: $(grep -m1 -o 'out of memory' $O/gen_attempt$i.log)"
  sleep 300
done
exit 1

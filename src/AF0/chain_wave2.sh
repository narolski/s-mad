#!/usr/bin/env bash
# wave 2 (ghost energy g, disagreement D) + wave-3 fourth target G, beside alpha, at wave-1 scale (+ halves of
# wave-1 pairs as all-zero negatives). Ridge + MLP seed 401 only (compute). Usage: chain_wave2.sh <backbone> <eval lists>
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python; B=$1; EV=$2
for T in alpha g D G; do
  [ -f /mnt/t7/smad_next/AF0/heads/$B/w2_$T/log.json ] && grep -q seconds_last /mnt/t7/smad_next/AF0/heads/$B/w2_$T/log.json && continue
  OMP_NUM_THREADS=2 nice -n 10 $P -I heads.py --backbone $B --train af0_w1,af0_h --eval $EV --heads ridge,mlp --seeds 401 \
    --target $T --tag w2_$T --train-ids /mnt/t7/smad_next/AF0/w2_train_ids.npy --partial
done
echo WAVE2_DONE $B

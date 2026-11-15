#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python; B=$1
for T in alpha g D G; do
  OMP_NUM_THREADS=1 nice -n 10 $P -I metrics.py --backbone $B --tag w2_$T --af0 af0_w1 --bench bench_s \
    --keys score,score_top10,score_inner,score_periph --target $T > /mnt/t7/smad_next/AF0/metrics_${B}_w2_$T.log 2>&1
done
echo W2_METRICS_DONE $B

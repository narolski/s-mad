#!/bin/bash
# CB1: FD-MAD fused branch, res 256 then 512, seeds 1-3 (DGX CPU, thread caps).
E="env OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/CB1/fdmad_cb1.py --branch fused --images /mnt/t7/smad_next/CB1/manifests/cb1_cnn_images_v2.csv --workers 2"
for res in 256 512; do for s in 1 2 3; do
  f=/mnt/t7/smad_next/CB1/scores_fdmad/fdmad_fused_r${res}_s$s.npz; [ -f $f ] && continue
  $E --res $res --seed $s --out $f >> /mnt/t7/smad_next/CB1/logs/fdmad_fused_r${res}_s$s.log 2>&1
done; done

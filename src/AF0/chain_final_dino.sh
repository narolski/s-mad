#!/usr/bin/env bash
cd /home/narolski/smad-next/src/AF0; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
./run_w2_metrics.sh dinov3_512
$P -I w2report.py dinov3_512 > /mnt/t7/smad_next/AF0/w2report_dinov3.md 2>&1
OMP_NUM_THREADS=1 nice -n 10 $P -I graded.py dinov3_512:full dinov3_512:w2_alpha dinov3_512:w2_g dinov3_512:w2_D dinov3_512:w2_G clip224:full clip224:w2_alpha clip224:w2_g clip224:w2_D clip224:w2_G > /mnt/t7/smad_next/AF0/graded_all.log 2>&1
OMP_NUM_THREADS=1 nice -n 10 $P -I wave3_floor.py read --specs dinov3_512:full,dinov3_512:w2_alpha,dinov3_512:w2_g,dinov3_512:w2_D,dinov3_512:w2_G,clip224:full,clip224:w2_alpha,clip224:w2_g,clip224:w2_D,clip224:w2_G > /mnt/t7/smad_next/AF0/wave3_floor_all.log 2>&1
OMP_NUM_THREADS=1 nice -n 10 $P -I metrics.py --backbone dinov3_512 --tag full --af0 af0_w1,af0_w2 --bench bench_s --keys score,score_top10,score_median > /mnt/t7/smad_next/AF0/metrics_dino_full2.log 2>&1
echo FINAL_DINO_DONE

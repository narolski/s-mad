#!/bin/bash
# SM1 Part 2 secondary (whole files, five primary releases) and the reader, under the 11 Nov 20:50 DGX rule:
# OMP and BLAS threads 2, nice 10, 2 loader workers.
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /tmp
$P $S/rel_multi.py --manifest $O/flists/audit.csv --out-dir $O/p2scores/whole --dets madation_vitb16,madation_fe_vitb16,mixfacenet_mad_smdd,madation_vitl14,madation_fe_vitl14 --bs 32 --workers 2
$P $S/read_p2.py
echo P2W_DONE

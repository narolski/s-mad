#!/bin/bash
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/AR1; O=/mnt/t7/smad_next/AR1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; V=/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python
cd /tmp
retry() { for i in 1 2 3 4 5 6; do "$@" && return 0; echo "retry $i: $*" >&2; sleep 90; done; return 1; }
[ -f $O/crops/swap/crops.csv ] || retry nice -n 10 $V -I $S/crop_rgb.py --manifest $O/manifest_swap.csv --out $O/crops/swap
$P -I $S/lists.py crops $O/crops/swap/crops.csv $O/lists/crops_swap.csv
for d in madation_vitb16 mixfacenet_mad_smdd madation_vitl14; do
  [ -f $O/scores/scores_rel_${d}__swap.npz ] || retry nice -n 10 $P -I $S/score.py --det $d --mode rel --manifest $O/lists/crops_swap.csv --out-dir $O/scores --tag rel_${d}__swap
done
[ -f $O/scores/scores_own_selfmad__swap.npz ] || retry nice -n 10 $P -I $S/score.py --det selfmad_hrnet_w18 --mode own --manifest $O/manifest_swap.csv --out-dir $O/scores --tag own_selfmad__swap
echo SWAP_DONE

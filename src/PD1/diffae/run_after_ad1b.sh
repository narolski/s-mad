#!/bin/bash
# PD1 DiffAE: once AD1b's full run has written gen/PAF/png256 and gen/D20r/png256, rebuild the item list (ad1b rows
# from gen), extract the ad1b features (both models), score the mirror mixes with the saved final heads, refresh the
# external blocks (mirror rows) and the tables. My own earlier 4-person ad1b files are kept as *_smoke4.npz.
set -euo pipefail
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
S=/home/narolski/smad-next/src/PD1/diffae
B=/mnt/t7/smad_next/PD1/diffae
L=$B/logs
cd /home/narolski/smad-next
test -d /mnt/t7/smad_next/AD1b/gen/PAF/png256 && test -d /mnt/t7/smad_next/AD1b/gen/D20r/png256
for m in clip dino; do [ -f $B/feat/$m/ad1b.npz ] && mv $B/feat/$m/ad1b.npz $B/feat/$m/ad1b_smoke4.npz; done
[ -f $B/stats/ad1b.npz ] && mv $B/stats/ad1b.npz $B/stats/ad1b_smoke4.npz
nice -n 10 $PY -I $S/pd1_items.py > $L/items_after_ad1b.log 2>&1
$S/run_feats.sh clip ad1b --workers 2
$S/run_feats.sh dino ad1b --workers 2
OMP_NUM_THREADS=2 nice -n 10 $PY -I $S/pd1_mirror.py > $L/mirror.log 2>&1
for f in clip_pool clip_patch dino_pool; do
  OMP_NUM_THREADS=1 nice -n 10 $PY -I $S/pd1_rescore.py --feats $f > $L/rescore2_$f.log 2>&1 &
done
wait
nice -n 10 $PY -I $S/pd1_report.py > $B/report.md 2>&1
echo "after_ad1b done $(date)" >> $L/feat_progress.txt

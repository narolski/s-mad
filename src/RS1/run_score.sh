#!/bin/bash
# Own-crop re-score of the audit rows (RS1): score the crops with the landmark ladder's score.py (via rs1_score.py).
#   run_score.sh a46   -> the registered A46 RGB crops of the raw files (needs no new crop)
#   run_score.sh new   -> the new crops (after manifest.py merge)
# One GPU process at a time; DataLoader workers 1 (CPU budget shared with the crop shards). The GPU is shared and
# unified memory is tight: a run that fails (CUDA out of memory at start) is retried up to 6 times, 3 min apart.
set -uo pipefail
S=/home/narolski/smad-next/src/RS1; O=/mnt/t7/smad_next/RS1
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /tmp
part=$1
if [ "$part" = new ]; then
  $P -I -c "import csv
ids={r['id'] for r in csv.DictReader(open('$O/manifest.csv')) if r['crop_origin']=='rs1'}
rows=[r for r in csv.DictReader(open('$O/lists/score.csv')) if r['id'] in ids]
w=csv.writer(open('$O/lists/score_new.csv','w',newline='')); w.writerow(['id','path']); [w.writerow([r['id'],r['path']]) for r in rows]
print('new', len(rows))" || exit 1
fi
mkdir -p $O/scores
for d in madation_vitb16 madation_vitl14 madation_fe_vitl14 mixfacenet_mad_smdd madation_fe_vitb16; do
  for k in 1 2 3 4 5 6; do
    [ -f $O/scores/scores_rel_${d}__$part.npz ] && break
    t0=$(date +%s)
    nice -n 10 $P -I $S/rs1_score.py --det $d --mode rel --manifest $O/lists/score_$part.csv --out-dir $O/scores \
      --tag rel_${d}__$part --workers ${W:-1} --bs 32 > $O/scores/log_${d}__${part}_try$k.log 2>&1
    echo "$d $part try $k exit $? $(( $(date +%s) - t0 )) s $(date +%H:%M)"
    [ -f $O/scores/scores_rel_${d}__$part.npz ] || sleep 180
  done
  [ -f $O/scores/scores_rel_${d}__$part.npz ] || { echo "FAILED $d $part"; exit 1; }
done
echo SCORE_${part}_DONE

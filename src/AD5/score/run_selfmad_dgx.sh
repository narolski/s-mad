#!/bin/bash
# Retrains of released methods (AD5): score the SelfMAD release and the SelfMAD retrains on the DGX through RS1's
# score.py --mode own (the release's own preprocessing), on every RS1 manifest image (raw source files; set names as RS1).
#   run_selfmad_dgx.sh [NAMES...]   default: selfmad_hrnet_w18 selfmad_S_s401 ... selfmad_S_s405
# Retrain tars are read from /mnt/t7/smad_next/AD5/results/<name>.tar (hash-checked copies from Athena).
# One network at a time, dlib workers 6, nice 10; a run that fails with CUDA out of memory is retried (shared GPU).
set -uo pipefail
A=/mnt/t7/smad_next/AD5; O=$A/scores_selfmad; mkdir -p $O $A/conv_selfmad
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
REL=/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors
$PY -I -c "
import csv
rows=[r for r in csv.DictReader(open('/mnt/t7/smad_next/RS1/manifest.csv')) if r['src_path']]
w=csv.writer(open('$O/list_all.csv','w',newline='')); w.writerow(['id','path']); [w.writerow([r['id'],r['src_path']]) for r in rows]
print('images', len(rows))"
NAMES=${*:-selfmad_hrnet_w18 selfmad_S_s401 selfmad_S_s402 selfmad_S_s403 selfmad_S_s404 selfmad_S_s405}
cd /tmp
for n in $NAMES; do
  [ -f $O/scores_own_${n}__ad5.npz ] && { echo "$n done"; continue; }
  if [ $n = selfmad_hrnet_w18 ]; then wf=$REL
  else
    t=$A/results/$n.tar; (cd $A/results && sha256sum -c $n.tar.sha256) || { echo "missing or bad $t"; continue; }
    d=$A/conv_selfmad/$n; mkdir -p $d; tar -xf $t -C $d
    $PY -I /home/narolski/smad-next/src/AD5/score/convert_selfmad.py $d/epoch_100.tar $d/model.safetensors $REL > $d/convert.json || exit 1
    wf=$d/model.safetensors
  fi
  for k in 1 2 3 4 5 6; do
    nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/score/ad5_score_dgx.py --name $n --weights $wf -- --mode own \
      --manifest $O/list_all.csv --out-dir $O --tag own_${n}__ad5 --workers ${W:-6} > $O/log_$n.log 2>&1 && break
    grep -q "out of memory" $O/log_$n.log || { echo "FAILED $n"; tail -5 $O/log_$n.log; break; }
    sleep 180
  done
  tail -1 $O/log_$n.log
done
echo SELFMAD_SCORING_DONE

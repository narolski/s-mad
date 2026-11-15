#!/bin/bash
# Retrains of released methods (AD5): dry run of the scoring + analysis path on the DGX with RS1's smoke crops
# (job 3545869, 8 images per set, both variants). Networks: the MixFaceNet-MAD 8-image check network as a stand-in
# "retrain" (named mixfacenet_X_s401) and the releases mixfacenet_mad_smdd, madation_vitb16. Analysis with B=50 into
# a scratch folder that is deleted afterwards (dry run: only that the code runs is checked; no number is read).
set -uo pipefail
C=/mnt/t7/smad_next/AD5/checks/dryrun; SM=/mnt/t7/smad_next/RS1/athena/smoke_3545869; PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
mkdir -p $C/scores; cd /tmp
for v in v1 v2; do $PY -I -c "
import csv
rows=list(csv.DictReader(open('$SM/score_$v.csv')))
w=csv.writer(open('$C/score_$v.csv','w',newline='')); w.writerow(['id','path'])
for r in rows: w.writerow([r['id'], '$SM/crops/$v/'+r['path'].rsplit('/',1)[1]])"; done
PAY=/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models
for spec in "mixfacenet_mad_smdd mixfacenet_X_s401 /mnt/t7/smad_next/AD5/checks/mixfacenet8v2/mixfacenet_SMDD.pth" \
            "mixfacenet_mad_smdd mixfacenet_mad_smdd /mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth" \
            "madation_vitb16 madation_vitb16 $PAY/ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors"; do
  set -- $spec
  for v in v1 v2; do
    for k in 1 2 3 4 5; do
      nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/score/ad5_score_athena.py /mnt/t7/smad_next/AD5/checks/score8/root /mnt/t7/smad_next/AD5/checks/score8/site \
        --as $1 --name $2 --weights $3 -- --mode rel --manifest $C/score_$v.csv --out-dir $C/scores --tag rel_$2__ad5$v --workers 1 --bs 16 > $C/log_$2_$v.log 2>&1 && break
      grep -q "out of memory" $C/log_$2_$v.log || { tail -5 $C/log_$2_$v.log; break; }; sleep 60
    done; tail -1 $C/log_$2_$v.log
  done
done
mkdir -p $C/analysis && nice -n 10 $PY -I /home/narolski/smad-next/src/AD5/ad5_analyse.py --scores $C/scores --B 50 --out-dir $C/analysis --arms X,B 2>&1 | tail -3
ls $C/analysis; rm -rf $C/analysis; echo DRYRUN_DONE

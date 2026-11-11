#!/usr/bin/env bash
# ID0 GPU feature runner: retries (the shared GB10 sometimes refuses the first allocation); resumable via parts.
# usage: run_feat.sh spark|diffae LOG [extra args]
set -uo pipefail
cd /home/narolski/smad-next/src/ID0
which=$1; log=$2; shift 2
for t in 1 2 3 4 5; do
  echo "$(date +%T) start $which try $t $*" >> "$log"
  if [ "$which" = spark ]; then
    nice -n 5 /home/narolski/mambamorph-code/.venv-spark/bin/python -I feat.py "$@" >> "$log" 2>&1
  else
    nice -n 5 /mnt/t7/thirdparty/diffae_venv/bin/python -I feat_diffae.py "$@" >> "$log" 2>&1
  fi
  rc=$?
  if [ $rc = 0 ]; then echo "$(date +%T) ok" >> "$log"; exit 0; fi
  echo "$(date +%T) failed rc=$rc try $t" >> "$log"; sleep 30
done
exit 1

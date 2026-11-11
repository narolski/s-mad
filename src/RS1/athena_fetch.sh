#!/bin/bash
# Own-crop re-score of the audit rows (RS1): copy one Athena result tar back, check its sha256, unpack it.
#   athena_fetch.sh TAG   (e.g. smoke_3544220 or prod_<jobid>) -> /mnt/t7/smad_next/RS1/athena/<TAG>/
set -euo pipefail
T=$1; A=/mnt/t7/smad_next/RS1/athena; G=/net/pr2/projects/plgrid/plggrestoration/smad-next
mkdir -p $A/fetch
flock -w 1800 /tmp/smadnext-athena.lock rsync -a -e "ssh -o BatchMode=yes" \
  plgpnarolski@athena.cyfronet.pl:$G/results/RS1/rs1a_$T.tar plgpnarolski@athena.cyfronet.pl:$G/results/RS1/rs1a_$T.tar.sha256 $A/fetch/
( cd $A/fetch && sha256sum -c rs1a_$T.tar.sha256 )
mkdir -p $A/$T && tar -xf $A/fetch/rs1a_$T.tar -C $A/$T
echo "fetched $T"

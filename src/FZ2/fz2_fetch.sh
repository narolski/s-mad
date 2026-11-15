#!/bin/bash
# FZ2: copy back result tars from Athena (transfer lock), check sha256, unpack into /mnt/t7/smad_next/FZ2/results/<TAG>/.
# usage: bash fz2_fetch.sh TAG...
set -euo pipefail
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
L=/mnt/t7/smad_next/FZ2/results
mkdir -p $L
for T in "$@"; do
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a -e "ssh -o BatchMode=yes" \
    plgpnarolski@athena.cyfronet.pl:$G/results/FZ2/FZ2_$T.tar plgpnarolski@athena.cyfronet.pl:$G/results/FZ2/FZ2_$T.tar.sha256 $L/
  ( cd $L && sha256sum -c FZ2_$T.tar.sha256 )
  mkdir -p $L/$T && tar -xf $L/FZ2_$T.tar -C $L/$T
  ls -la $L/$T/out
done

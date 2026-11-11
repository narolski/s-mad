#!/bin/bash
# SM1: upload GPU-pack tars to Athena packs/SM1, one rsync (one connection, under the lock) per tar; sha256 last.
set -euo pipefail
D=/mnt/t7/smad_next/SM1/gpupack
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
for n in "$@"; do
  T0=$(date +%s)
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial --timeout=300 -e "ssh -o BatchMode=yes -o ConnectTimeout=20" "$D/$n" "plgpnarolski@athena.cyfronet.pl:$G/packs/SM1/"
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a --timeout=120 -e "ssh -o BatchMode=yes -o ConnectTimeout=20" "$D/$n.sha256" "plgpnarolski@athena.cyfronet.pl:$G/packs/SM1/"
  echo "$(date -Is) uploaded $n in $(( $(date +%s) - T0 )) s" | tee -a /mnt/t7/smad_next/SM1/gpupack/athena_upload.log
done

#!/bin/bash
# Retrains of released methods (AD5): copy finished result tars back from Athena and check their hashes.
#   fetch_results.sh [PATTERN]   default: every *.tar with a .sha256 beside it in results/AD5 (and *_epochs/ folders
#   when FETCH_EPOCHS=1). Transfer lock /tmp/smadnext-athena.lock (ATHENA.md). Prints OK / BAD per tar.
set -uo pipefail
L=/mnt/t7/smad_next/AD5/results; mkdir -p $L
R=/net/pr2/projects/plgrid/plggrestoration/smad-next/results/AD5
PAT=${1:-*}
INC=(--include="$PAT.tar" --include="$PAT.tar.sha256" --include="*.json")
[ "${FETCH_EPOCHS:-0}" = 1 ] && INC+=(--include="*_epochs/" --include="*_epochs/**")
flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial "${INC[@]}" --exclude="*" \
  -e "ssh -o BatchMode=yes -o ConnectTimeout=30" plgpnarolski@athena.cyfronet.pl:$R/ $L/ || { echo "rsync failed"; exit 1; }
cd $L
for s in $PAT.tar.sha256; do
  [ -f "$s" ] || continue
  if sha256sum -c --quiet "$s"; then echo "OK ${s%.sha256}"; else echo "BAD ${s%.sha256}"; fi
done

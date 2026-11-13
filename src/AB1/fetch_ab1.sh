#!/bin/bash
# AB1: fetch result tars from WCSS Lustre to the T7 drive and verify each against the job's own sha256 (copy 1: Lustre
# results/AB1, copy 2: /mnt/t7/smad_next/AB1/results). One rsync connection under the shared WCSS lock.
#   bash fetch_ab1.sh fits     # results/AB1/AB1_*.tar(.sha256)
#   bash fetch_ab1.sh smoke    # results/AB1_smoke/* (smoke tar and platform tar)
set -euo pipefail
WHAT=${1:?fits|smoke}
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
case "$WHAT" in
  fits) SRC=$L/results/AB1/; DST=/mnt/t7/smad_next/AB1/results/; INC=(--include='AB1_*.tar' --include='AB1_*.tar.sha256') ;;
  smoke) SRC=$L/results/AB1_smoke/; DST=/mnt/t7/smad_next/AB1/smoke/; INC=(--include='*.tar' --include='*.tar.sha256') ;;
  *) echo "fits|smoke"; exit 1 ;;
esac
avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
[ "$avail" -ge 50 ] || { echo "T7 has ${avail} GB free (< 50 GB floor): not fetching"; exit 1; }
mkdir -p "$DST"
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a --partial "${INC[@]}" --exclude='*' \
  -e "ssh -o BatchMode=yes -o ConnectTimeout=30" "narolski@ui.wcss.pl:$SRC" "$DST"
n=0; bad=0
for s in "$DST"/*.tar.sha256; do
  [ -e "$s" ] || continue
  t=${s%.sha256}
  if (cd "$DST" && sha256sum -c --quiet "$(basename "$s")" 2>/dev/null); then n=$((n + 1)); else bad=$((bad + 1)); echo "NOT VERIFIED $(basename "$t")"; fi
done
echo "verified $n, not verified $bad in $DST"

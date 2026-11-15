#!/bin/bash
# BB2 fetch: copy every finished BB2 fit tar (+ .sha256) and the fit logs from WCSS to /mnt/t7/smad_next/BB2/results,
# verify each tar against its .sha256 and against a sha256 computed on WCSS; append one line per verified tar to
# results/fetch.log (time, name, sha256). Run at each expected end (no polling loop). WCSS copies are left in place.
#   bash fetch_bb2.sh
set -uo pipefail
L=/lustre/pd03/hpc-narolski-1790461090/smad-next; OUT=/mnt/t7/smad_next/BB2/results
mkdir -p "$OUT/logs"
avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' '); [ "$avail" -ge 20 ] || { echo "T7 under 20 GB free"; exit 1; }
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a --timeout=120 -e "ssh -o BatchMode=yes -o ConnectTimeout=30" \
  --include='BB2_*_s40[3-7].tar' --include='BB2_*_s40[3-7].tar.sha256' --exclude='*' "narolski@ui.wcss.pl:$L/results/BB2/" "$OUT/" || { echo "fetch failed (unreachable): no decision"; exit 1; }
flock -w 600 /tmp/opencode/wcss-client.lock rsync -a --timeout=120 -e "ssh -o BatchMode=yes -o ConnectTimeout=30" \
  --include='bb2-fit*.out' --exclude='*' "narolski@ui.wcss.pl:$L/logs/" "$OUT/logs/" || echo "log fetch failed"
REM=$(flock -w 600 /tmp/opencode/wcss-client.lock ssh -o BatchMode=yes -o ConnectTimeout=30 narolski@ui.wcss.pl "cd $L/results/BB2 && sha256sum BB2_*.tar 2>/dev/null") || { echo "remote listing failed: no decision"; exit 1; }
for t in "$OUT"/BB2_*_s40[3-7].tar; do
  [ -e "$t" ] || continue
  n=$(basename "$t"); l=$(sha256sum "$t" | cut -c1-64); r=$(echo "$REM" | awk -v n="$n" '$2 == n {print $1}')
  if [ "$l" = "$(cut -c1-64 "$t.sha256")" ] && [ "$l" = "$r" ]; then
    grep -q " $n $l" "$OUT/fetch.log" 2>/dev/null || echo "$(date -Is) $n $l" >> "$OUT/fetch.log"
    echo "OK $n"
  else echo "MISMATCH $n"; fi
done
(cd "$OUT/logs" && sha256sum bb2-fit*.out > ../logs.sha256) 2>/dev/null || true

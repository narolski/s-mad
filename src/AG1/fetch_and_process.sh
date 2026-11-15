#!/bin/bash
# AG1 copy-back, one result tar at a time (lead's option (c), 11 Nov): for each shard named in the arguments (or in
# core.txt, ag3.txt and the four spread names) whose result exists on Athena and is not yet processed locally:
#   1. check free space on /mnt/t7 (>= 40 GB after the fetch, lead 11 Nov, else stop);
#   2. rsync <shard>.tar, .tar.sha256 and .log.csv from Athena (transfer lock);
#   3. check the local tar's sha256 against the .sha256 written on Athena (the hash of the Athena copy);
#   4. ag1_manifest.py shard <tar> (thread caps, nice 10): frames, oracle crops / embeddings, RT check;
#   5. append "shard, sha256, bytes, processed time" to experiments/AG1/fetched_tars.csv and remove the local tar
#      (the verified original stays on Athena; .sha256 and .log.csv are kept).
# Usage: fetch_and_process.sh [shard ...]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
B=/mnt/t7/smad_next/AG1
R=$B/results
LEDGER=/home/narolski/smad-next/experiments/AG1/fetched_tars.csv
A=plgpnarolski@athena.cyfronet.pl
AR=/net/pr2/projects/plgrid/plggrestoration/smad-next/results/AG1
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
mkdir -p "$R"
[ -s "$LEDGER" ] || echo "shard,sha256,bytes,processed_at" > "$LEDGER"
if [ $# -gt 0 ]; then NAMES=("$@"); else
  mapfile -t NAMES < <(cat "$B/athena/tasks/core.txt" "$B/athena/tasks/ag3.txt"; printf "AG1_spread_mip1_frll\nAG1_spread_mip1_feret\nAG1_spread_mip1_frgc\nAG1_spread_mip2_frll\n")
fi
AVAIL=$(flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes "$A" "cd $AR && ls -1 AG1_*.tar.sha256 2>/dev/null" || true)
for n in "${NAMES[@]}"; do
  [ -n "$n" ] || continue
  [ -s "$B/data/shards/$n.json" ] && { echo "$n: already processed"; continue; }
  grep -qx "$n.tar.sha256" <<< "$AVAIL" || { echo "$n: no result on Athena yet"; continue; }
  free_gb=$(df --output=avail -BG /mnt/t7 | tail -1 | tr -dc 0-9)
  [ "$free_gb" -ge 21 ] || { echo "only ${free_gb} GB free on /mnt/t7; stopping (lead 12 Nov: floor 20 GB)"; exit 7; }
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a "$A:$AR/$n.tar" "$A:$AR/$n.tar.sha256" "$A:$AR/$n.log.csv" "$R/"
  [ "$(sha256sum "$R/$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$R/$n.tar.sha256")" ] || { echo "$n: sha256 mismatch after fetch"; exit 8; }
  nice -n 10 "$PY" "$HERE/ag1_manifest.py" shard "$R/$n.tar"
  echo "$n,$(cut -c1-64 "$R/$n.tar.sha256"),$(stat -c %s "$R/$n.tar"),$(date +%FT%T)" >> "$LEDGER"
  rm -f "$R/$n.tar"
  echo "$n: processed; local tar removed (verified original on Athena)"
done

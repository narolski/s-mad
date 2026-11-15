#!/bin/bash
# Writes the 20 AD4 slot-queue task directories into $1 (local), each: run.sh (src/AD4/run.sh), task.env,
# est_minutes. Estimates: A47 I-3 M3 train_hours 0.52 h, A12BR M3L 1.94 h (H100, 14 workers) + about 20 min for
# pack staging and scoring, rounded up with margin.
set -euo pipefail
DST=${1:?destination}
SRC=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$DST"
for RECIPE in m3 m3l; do
  for ARM in mf perm; do
    for SEED in 401 402 403 404 405; do
      T=AD4_${RECIPE}${ARM}_s$SEED
      [ ! -e "$DST/$T" ] || { echo "exists: $DST/$T"; exit 1; }
      mkdir "$DST/$T"
      cp "$SRC/run.sh" "$DST/$T/run.sh"
      printf 'TASK=%s\nRECIPE=%s\nARM=%s\nSEED=%s\n' "$T" "$RECIPE" "$ARM" "$SEED" > "$DST/$T/task.env"
      if [ "$RECIPE" = m3 ]; then echo 75 > "$DST/$T/est_minutes"; else echo 180 > "$DST/$T/est_minutes"; fi
    done
  done
done
ls "$DST" | wc -l

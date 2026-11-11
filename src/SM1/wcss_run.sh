#!/bin/bash
# SM1 WCSS CPU build task (SMDD five-partner audit and rebuild, rebuild arms). One tar in, one tar out, all IO in
# $TMPDIR. Builds the listed pairs with the UNCHANGED 68/78 engine (packed copies, sha256 logged) through build.py
# (halves asserted per pair), checks the wrapper against the unchanged 78 command line on 8 pairs, compares the first
# 8 rows of each list with the DGX reference outputs (pixel max abs diff, logged; not a gate), then tars out/ + logs.
# Env (task.env next to this file sets SM1_TASK / SM1_LISTS); overrides for the DGX test: SM1_PACK, SM1_RESULTS,
# SM1_PY, SM1_LIMIT, TMPDIR, SLURM_CPUS_PER_TASK.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
source "$HERE/task.env"
LUS=/lustre/pd03/hpc-narolski-1790461090/smad-next
PACK=${SM1_PACK:-$LUS/packs/SM1/sm1_${SM1_TASK}_pack.tar}
RES=${SM1_RESULTS:-$LUS/results/SM1}
PY=${SM1_PY:-$HOME/dmenv/bin/python}
LIMIT=${SM1_LIMIT:-0}
BASE=${TMPDIR:-${TASK_WORK:-}}
[ -n "$BASE" ] || { echo "no TMPDIR / TASK_WORK" >&2; exit 2; }
NCPU=${SLURM_CPUS_PER_TASK:-$(cat "$HERE/cpus")}
WK=$BASE/sm1_${SM1_TASK}
rm -rf "$WK"; mkdir -p "$WK"; cd "$WK"
echo "start $(date -Is) host $(hostname) cpus $NCPU"
echo "$SM1_PACK_SHA256  $PACK" | sha256sum -c -
tar xf "$PACK"
export SM1_S78=$WK/code/scripts/78_tool_morph.py
mkdir -p out/logs
for L in $SM1_LISTS; do
  "$PY" -I code/sm1/build.py --list lists/$L.csv --root "$WK" --verify-cli 8 --log-dir out/logs
  "$PY" -I code/sm1/build.py --list lists/$L.csv --root "$WK" --workers "$NCPU" --limit "$LIMIT" --log-dir out/logs
done
"$PY" -I code/sm1/build.py --list lists/$L.csv --root "$WK" --compare lists/compare_ref.csv --log-dir out/logs
sha256sum code/scripts/68_hires_morph.py code/scripts/78_tool_morph.py code/sm1/build.py > out/logs/code_sha256.txt
(cd out && find . -name '*.png' | sort > logs/manifest.txt)
echo "pngs $(wc -l < out/logs/manifest.txt)"
TAG=sm1_${SM1_TASK}_out$([ "$LIMIT" = 0 ] || echo "_limit$LIMIT")
tar cf "$BASE/$TAG.tar" out
mkdir -p "$RES"
cp "$BASE/$TAG.tar" "$RES/$TAG.tar.part"
mv "$RES/$TAG.tar.part" "$RES/$TAG.tar"
sha256sum "$BASE/$TAG.tar" | awk '{print $1}' > "$RES/$TAG.tar.sha256"
echo "done $(date -Is) -> $RES/$TAG.tar"

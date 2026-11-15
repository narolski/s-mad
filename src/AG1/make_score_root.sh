#!/bin/bash
# Build the AG1 scoring job root: the registered A43 code tree (mambamorph-code branch a43 commit c669666: smadcvpr/,
# third_party/, a30code/) + src/AG1/ag1_score.py + plans/AG1/AG1_data_pins.sha256 (only when the AG1 data registration
# has written it). Usage: make_score_root.sh OUT_DIR [PINS_FILE]
set -euo pipefail
OUT=${1:?out dir}
PINS=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd)
[ ! -e "$OUT" ] || { echo "refusing: $OUT exists"; exit 1; }
mkdir -p "$OUT"
git -C /home/narolski/mambamorph-code archive c669666 smadcvpr third_party a30code \
  | tar -x -C "$OUT" --exclude='smadcvpr/results' --exclude='smadcvpr/PROTOCOL.md'
for p in smadcvpr/a41g_score.py smadcvpr/a12_released.py smadcvpr/common.py smadcvpr/rsx_selfmad_own.py; do
  sha256sum "$OUT/$p"
done
[ "$(sha256sum "$OUT/smadcvpr/a41g_score.py" | cut -c1-64)" = f53612cb146e72ca5598d9b01962dcf3fb2f9d4aa8c9d616d80bd99e273c6113 ] \
  || { echo "a41g_score.py is not amendment G's"; exit 1; }
cp "$HERE/ag1_score.py" "$OUT/smadcvpr/ag1_score.py"
if [ -n "$PINS" ]; then mkdir -p "$OUT/smadcvpr/plans/AG1"; cp "$PINS" "$OUT/smadcvpr/plans/AG1/AG1_data_pins.sha256"; fi
echo "SCORE_ROOT $OUT"

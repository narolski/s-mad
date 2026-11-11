#!/bin/bash
# AG1 spread-matched renders R2s for one (generator, pool) on Athena (amendment 3, rule 6). Usage: ag1_spread_task.sh GEN POOL
# Needs every core result tar AG1_<GEN>_<POOL>_* in results/AG1 (exit 3 otherwise). Code: the pack's vendored generator
# files + tasks/AG1/ag1_spread.py (sha256 in tasks/AG1/ag1_spread.py.sha256). Out: results/AG1/AG1_spread_<GEN>_<POOL>.tar.
set -euo pipefail
GEN=${1:?gen}; POOL=${2:?pool}; NAME=AG1_spread_${GEN}_${POOL}
G=${AG1_G:-/net/pr2/projects/plgrid/plggrestoration/smad-next}
P=$G/packs/AG1; RES=$G/results/AG1; PY=$G/envs/AG1/bin/python
: "${MEMFS:?RAM disk required (-C memfs)}"
if [ -s "$RES/$NAME.tar" ] && [ -s "$RES/$NAME.tar.sha256" ] && \
   [ "$(sha256sum "$RES/$NAME.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$NAME.tar.sha256")" ]; then
  echo "$NAME: verified result already present"; exit 0
fi
W=$MEMFS/$NAME; rm -rf "$W"; mkdir -p "$W/lat"; cd "$W"; export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
echo "$NAME on $(hostname) $(date +%FT%T)"; nvidia-smi --query-gpu=name --format=csv,noheader
[ "$(sha256sum "$P/ag1_pack.tar" | cut -c1-64)" = "$(cut -c1-64 "$P/ag1_pack.tar.sha256")" ] || { echo "pack sha256 mismatch"; exit 2; }
EXC=(--exclude=gan_weights/ffhq.pkl --exclude=gan_weights/w600k_r50.onnx)
[ "$GEN" = mip1 ] && EXC+=(--exclude=gan_weights/e4e_ffhq_encode.pt)
tar -xOf "$P/ag1_pack.tar" gan_weights.tar | tar -x "${EXC[@]}"
for f in gan_sg1.tar ag1_code.tar ag1_inputs.tar; do tar -xOf "$P/ag1_pack.tar" "$f" | tar -x; done
[ "$(sha256sum "$G/tasks/AG1/ag1_spread.py" | cut -c1-64)" = "$(cut -c1-64 "$G/tasks/AG1/ag1_spread.py.sha256")" ] || { echo "ag1_spread.py sha256 mismatch"; exit 2; }
cp "$G/tasks/AG1/ag1_spread.py" ag1_code/
N=0
for n in $(grep "^AG1_${GEN}_${POOL}_" "$G/tasks/AG1/core.txt"); do
  [ -s "$RES/$n.tar" ] && [ -s "$RES/$n.tar.sha256" ] || { echo "core shard $n has no result tar"; exit 3; }
  [ "$(sha256sum "$RES/$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$n.tar.sha256")" ] || { echo "$n sha256 mismatch"; exit 3; }
  tar -xf "$RES/$n.tar" --wildcards "$n/lat/inv_*" "$n/lat/${GEN}_R2_*__s1.npz" && mv "$n"/lat/* lat/ && rm -rf "$n"
  N=$((N + 1))
done
[ "$N" -gt 0 ] || { echo "no core shards for $GEN $POOL"; exit 3; }
OUT=$W/$NAME; mkdir -p "$OUT"
"$PY" -I ag1_code/ag1_spread.py --gen "$GEN" --pool "$POOL" --lat "$W/lat" --inputs "$W/ag1_inputs" \
  --weights "$W/gan_weights" --sg1 "$W/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT"
tar -C "$W" -cf "$RES/.$NAME.tar.partial" "$NAME"
H=$(sha256sum "$RES/.$NAME.tar.partial" | cut -c1-64)
cp "$OUT/log.csv" "$RES/$NAME.log.csv"
echo "$H  $NAME.tar" > "$RES/$NAME.tar.sha256"
mv -f "$RES/.$NAME.tar.partial" "$RES/$NAME.tar"
echo "SPREAD_TAR_DONE $RES/$NAME.tar sha256 $H in ${SECONDS}s"

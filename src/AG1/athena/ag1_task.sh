#!/bin/bash
# AG1 generation task on Athena (one shard). Usage: ag1_task.sh SHARD_NAME
# In: packs/AG1/ag1_pack.tar (+ .sha256): inner gan_weights.tar, gan_sg1.tar, ag1_code.tar, ag1_inputs.tar and
#     SHA256SUMS; all checked. AG3 shards also read the core shards' result tars from results/AG1 (exit 3 if absent).
# Work in $SCRATCH_LOCAL; python = envs/AG1 (pinned, built by the smoke job). Out: results/AG1/<shard>.tar + .sha256
# + .log.csv. Idempotent: a verified result tar present -> exit 0. Any failure -> non-zero.
set -euo pipefail
SHARD=${1:?shard name}
G=${AG1_G:-/net/pr2/projects/plgrid/plggrestoration/smad-next}   # AG1_G: local tests only
P=$G/packs/AG1
RES=$G/results/AG1
PY=$G/envs/AG1/bin/python
: "${SCRATCH_LOCAL:?node-local scratch required (-C localfs)}"
mkdir -p "$RES"
if [ -s "$RES/$SHARD.tar" ] && [ -s "$RES/$SHARD.tar.sha256" ] && \
   [ "$(sha256sum "$RES/$SHARD.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$SHARD.tar.sha256")" ]; then
  echo "AG1 $SHARD: verified result already present; nothing to do"; exit 0
fi
[ -x "$PY" ] || { echo "no $PY (the smoke job builds it)"; exit 6; }
W=$SCRATCH_LOCAL/ag1_$SHARD; rm -rf "$W"; mkdir -p "$W"; cd "$W"
export TMPDIR=$W/tmp; mkdir -p "$TMPDIR"
echo "AG1 $SHARD on $(hostname) $(date +%FT%T)"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
df -h "$SCRATCH_LOCAL" | tail -1
# smoke job 3544188 ran out of node-local space copying + unpacking the 2.9 GB pack: the outer tar is now checked in
# place on the project store (its sha256 covers the inner tars) and the inner tars are streamed out of it, keeping
# only the weights this generator needs.
[ "$(sha256sum "$P/ag1_pack.tar" | cut -c1-64)" = "$(cut -c1-64 "$P/ag1_pack.tar.sha256")" ] || { echo "pack sha256 mismatch"; exit 2; }
GEN=$(tar -xOf "$P/ag1_pack.tar" ag1_inputs.tar | tar -xO "ag1_inputs/shards/$SHARD.json" | "$PY" -I -c "import json,sys;print(json.load(sys.stdin)['gen'])")
EXC=(--exclude=gan_weights/ffhq.pkl --exclude=gan_weights/w600k_r50.onnx)
[ "$GEN" = mip1 ] && EXC+=(--exclude=gan_weights/e4e_ffhq_encode.pt)
tar -xOf "$P/ag1_pack.tar" gan_weights.tar | tar -x "${EXC[@]}"
for f in gan_sg1.tar ag1_code.tar ag1_inputs.tar; do tar -xOf "$P/ag1_pack.tar" "$f" | tar -x; done
du -sh "$W" | tail -1
LAT=()
NEEDS=$("$PY" -I -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['needs']))" "ag1_inputs/shards/$SHARD.json")
if [ -n "$NEEDS" ]; then
  mkdir -p needs_lat
  for n in $NEEDS; do
    [ -s "$RES/$n.tar" ] && [ -s "$RES/$n.tar.sha256" ] || { echo "needed core shard $n has no result tar"; exit 3; }
    [ "$(sha256sum "$RES/$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$n.tar.sha256")" ] || { echo "$n sha256 mismatch"; exit 3; }
    tar -xf "$RES/$n.tar" --wildcards "$n/lat/inv_*" && mv "$n"/lat/inv_* needs_lat/ && rm -rf "$n"
  done
  LAT=(--latents "$W/needs_lat")
fi
OUT=$W/$SHARD; mkdir -p "$OUT"
( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$OUT/gpumem.csv"; sleep 10; done ) & MON=$!
set +e
"$PY" -I "$W/ag1_code/ag1_gen.py" --shard "$W/ag1_inputs/shards/$SHARD.json" --inputs "$W/ag1_inputs" \
  --weights "$W/gan_weights" --sg1 "$W/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT" "${LAT[@]}"
RC=$?
set -e
kill $MON 2>/dev/null || true
echo "AG1 $SHARD: python exit $RC; peak nvidia-smi MiB $(awk -F', ' '{if ($1+0>m) m=$1+0} END {print m}' "$OUT/gpumem.csv")"
[ "$RC" = 0 ] || exit "$RC"
"$PY" -I -c "
import json, pathlib, sys, zlib
from PIL import Image
out = pathlib.Path(sys.argv[1]); rep = {}
for f in sorted((out / 'png').glob('*.png')):
    im = Image.open(f); raw = f.read_bytes(); i, chunks = 8, []
    while i < len(raw):
        n = int.from_bytes(raw[i:i + 4], 'big'); chunks.append(raw[i + 4:i + 8].decode()); i += 12 + n
    rep[f.name] = {'size': im.size, 'mode': im.mode, 'chunks': sorted(set(chunks))}
bad = [k for k, v in rep.items() if v['size'] != (1024, 1024) or v['mode'] != 'RGB' or set(v['chunks']) - {'IHDR', 'IDAT', 'IEND'}]
json.dump({'n': len(rep), 'not_1024_rgb_plain': bad}, open(out / 'format_check.json', 'w'))
print('FORMAT', len(rep), 'files; deviating', len(bad)); sys.exit(1 if bad else 0)
" "$OUT"
# the result tar is written straight to the project store (no local copy) and hashed there; its listing is checked
tar -C "$W" -cf "$RES/.$SHARD.tar.partial" "$SHARD"
H=$(sha256sum "$RES/.$SHARD.tar.partial" | cut -c1-64)
NP=$(tar -tf "$RES/.$SHARD.tar.partial" | grep -c "/png/.*\.png$" || true)
[ "$NP" = "$(ls "$OUT/png" | wc -l)" ] || { echo "result tar holds $NP PNGs, expected $(ls "$OUT/png" | wc -l)"; exit 4; }
cp "$OUT/log.csv" "$RES/$SHARD.log.csv"
echo "$H  $SHARD.tar" > "$RES/$SHARD.tar.sha256"
mv -f "$RES/.$SHARD.tar.partial" "$RES/$SHARD.tar"
echo "AG1_TAR_DONE $RES/$SHARD.tar $(stat -c %s "$RES/$SHARD.tar") bytes sha256 $H in ${SECONDS}s"

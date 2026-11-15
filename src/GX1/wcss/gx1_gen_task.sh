#!/bin/bash
# GX1 generation task on WCSS H100 (one shard). Usage: gx1_gen_task.sh SHARD
# In (pinned sha256): packs/AG1/{gan_weights.tar e06f19af..., gan_sg1.tar 1571c1a3...}, packs/GX1/{gx1_inputs.tar,
# gx1_code.tar} (pins in packs/GX1/GX1SUMS, itself pinned in the sbatch). Work in $TMPDIR (FORCE_RM_TMPDIR).
# Python: ~/dmenv/bin/python -I, read-only. Out: results/GX1/<shard>.tar + .sha256 + .log.csv. Idempotent; any failure
# exits non-zero; a shard name not in the inputs exits within a minute.
set -euo pipefail
S=${1:?shard}
L=/lustre/pd03/hpc-narolski-1790461090/smad-next
P=$L/packs/GX1; A=$L/packs/AG1; RES=$L/results/GX1
PY=$HOME/dmenv/bin/python
: "${TMPDIR:?no TMPDIR}"
mkdir -p "$RES"
if [ -s "$RES/$S.tar" ] && [ -s "$RES/$S.tar.sha256" ] && \
   [ "$(sha256sum "$RES/$S.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$S.tar.sha256")" ]; then
  echo "GX1 $S: verified result already present"; exit 0
fi
W=$TMPDIR/gx1_$S; rm -rf "$W"; mkdir -p "$W"; cd "$W"
echo "GX1 $S on $(hostname) $(date -Is)"; nvidia-smi --query-gpu=name,uuid --format=csv,noheader || true
[ "$(sha256sum "$A/gan_weights.tar" | cut -c1-64)" = e06f19af2cbb8089e398af7dd7e1e9aaee3dd0065a605324b6edbb108fd2b732 ] || { echo "gan_weights pin"; exit 2; }
[ "$(sha256sum "$A/gan_sg1.tar" | cut -c1-64)" = 1571c1a36a20a76f3ff1c9e79528df71a5b0b70377fc1e733b1afb9090e5b34b ] || { echo "gan_sg1 pin"; exit 2; }
(cd "$P" && sha256sum -c --quiet GX1SUMS) || { echo "GX1 pack pin"; exit 2; }
tar -xf "$P/gx1_inputs.tar"; tar -xf "$P/gx1_code.tar"
[ -s "gx1_inputs/shards/$S.json" ] || { echo "no shard $S"; exit 3; }
GEN=$("$PY" -I -c "import json,sys;print(json.load(open(sys.argv[1]))['gen'])" "gx1_inputs/shards/$S.json")
EXC=(--exclude=gan_weights/ffhq.pkl --exclude=gan_weights/w600k_r50.onnx)
[ "$GEN" = mip1 ] && EXC+=(--exclude=gan_weights/e4e_ffhq_encode.pt)
tar -xf "$A/gan_weights.tar" "${EXC[@]}"; tar -xf "$A/gan_sg1.tar"
OUT=$W/$S; mkdir -p "$OUT"
( while :; do nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> "$OUT/gpumem.csv" 2>/dev/null; sleep 30; done ) & MON=$!
set +e
"$PY" -I "$W/ag1_code/ag1_gen.py" --shard "$W/gx1_inputs/shards/$S.json" --inputs "$W/gx1_inputs" \
  --weights "$W/gan_weights" --sg1 "$W/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT" ${GX1_MAXJOBS:+--max-jobs $GX1_MAXJOBS}
RC=$?; kill $MON 2>/dev/null; set -e
echo "GX1 $S python exit $RC"
[ "$RC" = 0 ] || exit "$RC"
tar -C "$W" -cf "$RES/.$S.tar.partial" "$S"
H=$(sha256sum "$RES/.$S.tar.partial" | cut -c1-64)
cp "$OUT/log.csv" "$RES/$S.log.csv"; echo "$H  $S.tar" > "$RES/$S.tar.sha256"; mv -f "$RES/.$S.tar.partial" "$RES/$S.tar"
echo "GX1_TAR_DONE $RES/$S.tar $H in ${SECONDS}s"

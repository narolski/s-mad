#!/bin/bash
# AG1 slot-queue task (one generation shard). Runs with TASK_DIR (task dir on Lustre) and TASK_WORK (node-local, cwd).
# In: packs/AG1/{gan_weights.tar, gan_sg1.tar, ag1_inputs.tar, ag1_code.tar} (sha256 in packs/AG1/SHA256SUMS), copied
# to $TASK_WORK and extracted there. For an AG3 shard also the inversion latents of the core shards listed in
# $TASK_DIR/needs (their result tars must exist and match their .sha256, else exit 3).
# Out: results/AG1/<shard>.tar (png/, lat/, log.csv, inv.csv, meta.json) + <shard>.tar.sha256 + <shard>.log.csv.
# Idempotent: a verified result tar already present -> exit 0 without work. Any failure -> non-zero.
set -euo pipefail
: "${TASK_DIR:?}" "${TASK_WORK:?}"
SN=${AG1_SN:-/lustre/pd03/hpc-narolski-1790461090/smad-next}   # AG1_SN / AG1_PY: local tests only
P=$SN/packs/AG1
RES=$SN/results/AG1
SIF=/lustre/software-data/container-images/pytorch_latest.sif
SHARD=$(cat "$TASK_DIR/shard_name")
mkdir -p "$RES"
if [ -s "$RES/$SHARD.tar" ] && [ -s "$RES/$SHARD.tar.sha256" ] && \
   [ "$(sha256sum "$RES/$SHARD.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$SHARD.tar.sha256")" ]; then
  echo "AG1 $SHARD: verified result already present; nothing to do"; exit 0
fi
cd "$TASK_WORK"
echo "AG1 $SHARD on $(hostname) $(date +%FT%T)"; nvidia-smi -L
for f in gan_weights.tar gan_sg1.tar ag1_inputs.tar ag1_code.tar; do
  cp "$P/$f" .
  want=$(awk -v f="$f" '$2==f{print $1}' "$P/SHA256SUMS")
  [ -n "$want" ] && [ "$(sha256sum "$f" | cut -c1-64)" = "$want" ] || { echo "pack $f sha256 mismatch"; exit 2; }
  tar -xf "$f" && rm -f "$f"
done
LAT=""
if [ -s "$TASK_DIR/needs" ]; then
  mkdir -p needs_lat
  while read -r n; do
    [ -z "$n" ] && continue
    [ -s "$RES/$n.tar" ] && [ -s "$RES/$n.tar.sha256" ] || { echo "needed core shard $n has no result tar yet"; exit 3; }
    cp "$RES/$n.tar" "need_$n.tar"
    [ "$(sha256sum "need_$n.tar" | cut -c1-64)" = "$(cut -c1-64 "$RES/$n.tar.sha256")" ] || { echo "$n sha256 mismatch"; exit 3; }
    tar -xf "need_$n.tar" --wildcards "$n/lat/inv_*" && mv "$n"/lat/inv_* needs_lat/ && rm -rf "$n" "need_$n.tar"
  done < "$TASK_DIR/needs"
  LAT="--latents $TASK_WORK/needs_lat"
fi
OUT=$TASK_WORK/$SHARD
mkdir -p "$OUT"
if [ -n "${AG1_PY:-}" ]; then
  PY=($AG1_PY)
elif command -v apptainer >/dev/null 2>&1 && [ -s "$SIF" ]; then
  PY=(apptainer exec --nv -B "$TASK_WORK" "$SIF" python)      # the container of H4 / H4b (jobs 6237081, 6237487)
else
  echo "AG1 $SHARD: no apptainer or no $SIF on $(hostname); refusing (one torch stack for every shard)"; exit 5
fi
echo "AG1 $SHARD: python = ${PY[*]}"
set +e
"${PY[@]}" -I "$TASK_WORK/ag1_code/ag1_gen.py" \
  --shard "$TASK_WORK/ag1_inputs/shards/$SHARD.json" --inputs "$TASK_WORK/ag1_inputs" \
  --weights "$TASK_WORK/gan_weights" --sg1 "$TASK_WORK/gan_sg1/stylegan1_ffhq1024.pt" --out "$OUT" $LAT
RC=$?
set -e
echo "AG1 $SHARD: python exit $RC"
[ "$RC" = 0 ] || exit "$RC"
tar -C "$TASK_WORK" -cf "$TASK_WORK/$SHARD.tar" "$SHARD"
H=$(sha256sum "$TASK_WORK/$SHARD.tar" | cut -c1-64)
cp "$TASK_WORK/$SHARD.tar" "$RES/.$SHARD.tar.partial"
[ "$(sha256sum "$RES/.$SHARD.tar.partial" | cut -c1-64)" = "$H" ] || { echo "Lustre copy sha256 mismatch"; exit 4; }
cp "$OUT/log.csv" "$RES/$SHARD.log.csv"
echo "$H  $SHARD.tar" > "$RES/$SHARD.tar.sha256"
mv -f "$RES/.$SHARD.tar.partial" "$RES/$SHARD.tar"
echo "AG1_TAR_DONE $RES/$SHARD.tar $(stat -c %s "$RES/$SHARD.tar") bytes sha256 $H in ${SECONDS}s"

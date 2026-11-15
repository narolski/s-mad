#!/bin/bash
# Build the AG1 packs and slot-queue task directories locally (/mnt/t7/smad_next/AG1/staging), ready to upload to
# /lustre/.../smad-next/{packs,staging}/AG1/. Task name = AG1_o<order>-<shard arm>_s0 (the slot takes ready/ in sort
# order, so the FRLL benchmark-linked and core shards come first, AG3 last). Weight packs are the registered
# gan_weights.tar (e06f19af...) and gan_sg1.tar (1571c1a3...) already on Lustre (smadcvpr/packs), hard-linked on WCSS.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
B=/mnt/t7/smad_next/AG1
ST=$B/staging
[ ! -e "$ST" ] || { echo "refusing: $ST exists (remove it yourself after checking)"; exit 1; }
mkdir -p "$ST/packs" "$ST/tasks" "$ST/build/ag1_inputs" "$ST/build/ag1_code"
cp -r "$B/inputs/pack/photos.json" "$B/inputs/pack/crops" "$B/inputs/shards" "$ST/build/ag1_inputs/"
cp "$HERE/ag1_gen.py" "$ST/build/ag1_code/"
cp -r "$HERE/vendor" "$ST/build/ag1_code/"
rm -rf "$ST/build/ag1_code/vendor/__pycache__"
tar --sort=name --owner=0 --group=0 --mtime=@0 -C "$ST/build" -cf "$ST/packs/ag1_inputs.tar" ag1_inputs
tar --sort=name --owner=0 --group=0 --mtime=@0 -C "$ST/build" -cf "$ST/packs/ag1_code.tar" ag1_code
(cd "$ST/packs" && sha256sum ag1_inputs.tar ag1_code.tar > SHA256SUMS)
cat "$B/packs_src/gan_weights.tar.sha256" "$B/packs_src/gan_sg1.tar.sha256" >> "$ST/packs/SHA256SUMS"
for j in "$B"/inputs/shards/*.json; do
  name=$(basename "$j" .json)
  order=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['order'])" "$j")
  est=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['est_minutes'])" "$j")
  arm=${name#AG1_}
  T="$ST/tasks/$(printf 'AG1_o%02d-%s_s0' "$order" "${arm//_/-}")"
  mkdir -p "$T"
  cp "$HERE/run.sh" "$T/run.sh"
  echo "$name" > "$T/shard_name"
  echo "$est" > "$T/est_minutes"
  python3 -c "import json,sys;[print(n) for n in json.load(open(sys.argv[1]))['needs']]" "$j" > "$T/needs"
done
(cd "$ST" && tar --sort=name --owner=0 --group=0 -cf ag1_tasks.tar -C tasks .)
ls "$ST/tasks"
cat "$ST/packs/SHA256SUMS"
du -sh "$ST/packs"/*

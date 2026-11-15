#!/bin/bash
# Build the single AG1 pack for Athena: ag1_pack.tar = {gan_weights.tar (e06f19af...), gan_sg1.tar (1571c1a3...),
# ag1_code.tar, ag1_inputs.tar, SHA256SUMS} + ag1_pack.tar.sha256, and the shard lists. Out: /mnt/t7/smad_next/AG1/athena
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
B=/mnt/t7/smad_next/AG1
A=$B/athena
rm -rf "$A/build" && mkdir -p "$A/build/ag1_inputs" "$A/build/ag1_code" "$A/pack" "$A/tasks"
cp -r "$B/inputs/pack/photos.json" "$B/inputs/pack/crops" "$B/inputs/shards" "$A/build/ag1_inputs/"
cp "$HERE/ag1_gen.py" "$A/build/ag1_code/"; cp -r "$HERE/vendor" "$A/build/ag1_code/"; rm -rf "$A/build/ag1_code/vendor/__pycache__"
T="tar --sort=name --owner=0 --group=0 --mtime=@0"
$T -C "$A/build" -cf "$A/pack/ag1_inputs.tar" ag1_inputs
$T -C "$A/build" -cf "$A/pack/ag1_code.tar" ag1_code
ln -f "$B/packs_src/gan_weights.tar" "$A/pack/gan_weights.tar"
ln -f "$B/packs_src/gan_sg1.tar" "$A/pack/gan_sg1.tar"
(cd "$A/pack" && sha256sum gan_weights.tar gan_sg1.tar ag1_code.tar ag1_inputs.tar > SHA256SUMS)
grep -q e06f19af2cbb8089e398af7dd7e1e9aaee3dd0065a605324b6edbb108fd2b732 "$A/pack/SHA256SUMS"
grep -q 1571c1a36a20a76f3ff1c9e79528df71a5b0b70377fc1e733b1afb9090e5b34b "$A/pack/SHA256SUMS"
$T -C "$A/pack" -cf "$A/ag1_pack.tar" SHA256SUMS gan_weights.tar gan_sg1.tar ag1_code.tar ag1_inputs.tar
(cd "$A" && sha256sum ag1_pack.tar > ag1_pack.tar.sha256)
python3 - "$B/inputs/shards" "$A/tasks" <<'PY'
import json, pathlib, sys
S = sorted((json.load(open(f)) for f in pathlib.Path(sys.argv[1]).glob("*.json")), key=lambda s: s["order"])
out = pathlib.Path(sys.argv[2])
core = [s["shard"] for s in S if not s.get("smoke") and not s["needs"]]
ag3 = [s["shard"] for s in S if s["needs"] and not s.get("smoke")]
(out / "core.txt").write_text("\n".join(core) + "\n")
(out / "ag3.txt").write_text("\n".join(ag3) + "\n")
print("core", len(core), core); print("ag3", len(ag3), ag3)
PY
cp "$HERE/athena/ag1_task.sh" "$HERE/athena/ag1_smoke.sbatch" "$HERE/athena/ag1_array.sbatch" "$A/tasks/"
cat "$A/pack/SHA256SUMS" "$A/ag1_pack.tar.sha256"; du -sh "$A/ag1_pack.tar"

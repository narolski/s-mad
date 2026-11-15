#!/bin/bash
# RS1 crop regen on GB10 (fallback for pending Athena job 3555043; 2026-11-16).
# Mirrors src/RS1/athena_rs1.sbatch: variant 1 = the authors' SMDD image_preprocess.py run unchanged;
# variant 2 = RS1's corrected crop (crop_rgb.py unchanged, via athena_run.py). Crops verified per-file
# against the rented prod crops_sha256 references (v1 and v2). SMOKEn=1 limits to the smoke subset test.
#   SMOKEn=1 smoke_regen.sh   -> 466-input smoke validation (byte-identity check vs prod v1 sha)
#   smoke_regen.sh            -> full 29,056-input regen + sha check + result tar
set -uo pipefail
W=/mnt/t7/smad_next/RS1/regen_run
R=/mnt/t7/smad_next/RS1/regen_pack
S=/home/narolski/smad-next/src/RS1
REF1=/mnt/t7/smad_next/RS1/results_rented/prod_v1_rented/crops_sha256.txt
REF2=/mnt/t7/smad_next/RS1/results_rented/prod_v2_rented/crops_sha256.txt
PY=/home/narolski/smad-next/envs/rs1regen/bin/python
SMDD=/mnt/t7/smad_next/AD5/thirdparty/smdd_repo_9683229/image_preprocess.py
N=3
LIMIT=${SMOKEn_LIMIT:-0}
[ "${SMOKEn:-0}" = 1 ] && { W=$W/smoke; LIMIT=${SMOKEn_LIMIT:-460}; TAG=smoke; } || TAG=prod
mkdir -p "$W/crops/v1" "$W/crops/v2" "$W/out/logs"; cd /tmp
[ "$(sha256sum "$SMDD" | cut -d' ' -f1)" = bcaecd2970cd8d95e37b005f793035f2d0222219bf99215edc1168519fe5ee2c ] || { echo "SMDD script not at its pin"; exit 3; }
# input list (pack manifests, origin=crop), like the sbatch
"$PY" -I - "$R" "$W" "$LIMIT" "$N" <<'EOF'
import csv, sys, pathlib, os
R, W, lim, n = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows = [r for r in csv.DictReader(open(R / "manifests/athena_manifest.csv")) if r["origin"] == "crop"]
if lim:
    seen, keep = {}, []
    for r in rows:
        if seen.get(r["set"], 0) < lim:
            seen[r["set"]] = seen.get(r["set"], 0) + 1; keep.append(r)
    rows = keep
with open(W / "inputs_abs.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "path"]); [w.writerow([r["id"], str(R / r["relpath"])]) for r in rows]
for i in range(n):
    d = W / f"v1in/s{i}"; d.mkdir(parents=True, exist_ok=True)
EOF
# rebuild v1in symlinks (idempotent)
"$PY" -I - "$R" "$W" "$N" <<'EOF'
import csv, sys, pathlib, os
R, W, n = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), int(sys.argv[3])
rows = [r for r in csv.DictReader(open(W / "inputs_abs.csv"))]
for i in range(n):
    (W / f"v1in/s{i}").mkdir(parents=True, exist_ok=True)
for k, r in enumerate(rows):
    src = pathlib.Path(r["path"])
    ln = W / f"v1in/s{k % n}" / src.name
    if not ln.exists():
        os.symlink(src, ln)
print("inputs", len(rows))
EOF
echo "variant 1: SMDD image_preprocess.py unchanged $(date +%T)"
for i in $(seq 0 $((N-1))); do
  ( cd "$W" && nice -n 10 "$PY" -I "$SMDD" --in_folder "$W/v1in/s$i" --out_folder "$W/crops/v1" > "$W/out/logs/v1_shard$i.log" 2>&1 ) &
done
FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
[ $FAIL = 0 ] || { tail -20 "$W"/out/logs/v1_shard*.log; exit 4; }
echo "variant 2: corrected crop, PNG (crop_rgb.py unchanged) $(date +%T)"
for i in $(seq 0 $((N-1))); do
  nice -n 10 "$PY" -I "$S/athena_run.py" "$R" /tmp/rs1_nosite crop --manifest "$W/inputs_abs.csv" --out "$W/crops/v2" --shard $i/$N > "$W/out/logs/v2_shard$i.log" 2>&1 &
done
FAIL=0; for j in $(jobs -p); do wait $j || FAIL=1; done
[ $FAIL = 0 ] || { tail -20 "$W"/out/logs/v2_shard*.log; exit 4; }
# lists
"$PY" -I - "$W" <<'EOF'
import csv, sys, pathlib, glob, collections, json
W = pathlib.Path(sys.argv[1])
inp = list(csv.DictReader(open(W / "inputs_abs.csv")))
v1, miss1 = [], []
for r in inp:
    p = W / "crops/v1" / pathlib.Path(r["path"]).name
    (v1.append((r["id"], str(p))) if p.exists() else miss1.append(r["id"]))
v2, st = [], collections.Counter()
for f in sorted(glob.glob(str(W / "crops/v2/crops_*of3.csv"))):
    for r in csv.DictReader(open(f)):
        st[r["status"].split(":")[0]] += 1
        if r["status"] == "retained" or r["status"].startswith("flag:"):
            v2.append((r["id"], r["path"]))
for name, rows in (("score_v1.csv", v1), ("score_v2.csv", v2)):
    with open(W / name, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(rows)
json.dump(dict(n_inputs=len(inp), v1_written=len(v1), v1_missing=miss1, v2_status=dict(st)),
          open(W / "out/crop_summary.json", "w"), indent=1)
print("v1", len(v1), "missing", len(miss1), "| v2", len(v2), dict(st))
EOF
mkdir -p /tmp/rs1_nosite
# sha verification vs rented prod references
"$PY" -I - "$W" "$REF1" "$REF2" "$TAG" <<'EOF'
import csv, sys, pathlib, hashlib
W, r1, r2, tag = map(pathlib.Path, sys.argv[1:4])
def shafs(ref):
    d = {}
    for line in open(ref):
        h, name = line.split(maxsplit=1)
        d[name.strip()] = h
    return d
for v, ref in (("v1", r1), ("v2", r2)):
    rows = list(csv.DictReader(open(W / f"score_{v}.csv")))
    refsha, match, diff, nofile = shafs(ref), 0, 0, 0
    for _id, p in rows:
        f = pathlib.Path(p)
        if not f.exists():
            nofile += 1; continue
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if refsha.get(f.name) == h: match += 1
        elif f.name in refsha: diff += 1
    via = [f.name for _id, p in rows if (f := pathlib.Path(p)).exists() and f.name not in refsha and len(refsha) > 0]
    line = f"REGEN_SHA[{tag}] {v}: rows={len(rows)} match={match} diff={diff} nofile={nofile} not_in_ref={len(via)}"
    print(line, flush=True)
    open(W / f"out/logs/regen_sha_{v}.txt", "a").write(line + "\n")
EOF
echo "REGEN_DONE $TAG $(date +%T)"

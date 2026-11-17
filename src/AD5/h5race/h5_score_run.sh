#!/bin/bash
# H5 race (2026-11-17): SelfMAD MAD22 scoring on a cluster GPU, a duplicate of the GB10 run
# src/AD5/score/selfmad_m22_dgx_20261117.sh (H5 amendment 1, commit 9253df0). Same frozen score.py / ar1_common.py
# (sha pins asserted by ad5_score_athena.py), same RS1 regen-pack code (a12_released / common at their pins), same
# weights files (sha-listed in PACK_sha256.txt), same rows as RS1/regen_run/score_v{1,2}.csv, and the EXACT GB10 regen
# crop files (shipped as one tar split in parts, checked file by file against the GB10 crops_sha256.txt).
# Retrains are scored as --det selfmad_hrnet_w18 with their own weights (rel mode resolves the spec by name), output
# tag rel_<name>__m22v{1,2}, as on the GB10. Inference only.
#   h5_score_run.sh W PARTS PACKTAR OUT "NETS" LIMIT WORKERS
# W = local scratch work dir, PARTS = dir with crops_regen.tar.part_* + parts.sha256, PACKTAR = h5pack.tar (+ .sha256),
# OUT = persistent result dir, NETS = space-separated names (scored in parallel, one stream each), LIMIT = 0 | 8.
# Needs $PY (python with torch/timm/safetensors/PIL/numpy).
set -euo pipefail
W=$1 PARTS=$2 PACKTAR=$3 OUT=$4 NETS=$5 LIMIT=$6 WORKERS=${7:-6}
: "${PY:?python}"
mkdir -p "$W" "$OUT"
t0=$(date +%s)
( cd "$(dirname "$PACKTAR")" && sha256sum -c "$(basename "$PACKTAR").sha256" )
( cd "$PARTS" && sha256sum -c --quiet parts.sha256 ) || { echo "PARTS HASH MISMATCH"; exit 3; }
mkdir -p "$W/pack" "$W/out" "$W/nosite"
tar -xf "$PACKTAR" -C "$W/pack"
( cd "$W/pack" && sha256sum -c --quiet PACK_sha256.txt ) || { echo "PACK HASH MISMATCH"; exit 3; }
cat "$PARTS"/crops_regen.tar.part_* | tar -xf - -C "$W"
( cd "$W" && sha256sum -c --quiet pack/crops_sha256.txt ) || { echo "CROPS DIFFER FROM GB10 crops_sha256.txt"; exit 3; }
echo "crops verified byte-identical to GB10 list: $(wc -l < "$W/pack/crops_sha256.txt") files; staged in $(( $(date +%s) - t0 )) s"
"$PY" -I - "$W" <<'EOF'
import csv, sys, pathlib
W = pathlib.Path(sys.argv[1])
for v in ("v1", "v2"):
    rows = [(r["id"], str(W / "crops" / v / pathlib.Path(r["path"]).name)) for r in csv.DictReader(open(W / f"pack/manifests/score_{v}.csv"))]
    assert all(pathlib.Path(p).exists() for _, p in rows), v
    with open(W / f"score_{v}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "path"]); w.writerows(rows)
    print(v, len(rows), "rows")
EOF
"$PY" -I -c "import torch, timm; print('torch', torch.__version__, 'timm', timm.__version__, torch.cuda.get_device_name(0))"
LIM=(); SFX=""; [ "$LIMIT" != 0 ] && { LIM=(--limit "$LIMIT"); SFX=_limit$LIMIT; }
stream() {  # stream NAME: v1 then v2
  local n=$1 v tag wf=$W/pack/weights/$1.safetensors ts
  for v in v1 v2; do
    tag=rel_${n}__m22$v; ts=$(date +%s)
    "$PY" -I "$W/pack/ad5_score_athena.py" "$W/pack" "$W/nosite" --as selfmad_hrnet_w18 --name selfmad_hrnet_w18 \
      --weights "$wf" -- --mode rel --manifest "$W/score_$v.csv" --out-dir "$W/out" --tag "$tag" \
      --workers "$WORKERS" --bs 32 "${LIM[@]}" > "$W/out/log_$tag$SFX.log" 2>&1 \
      || { echo "FAILED $tag"; tail -20 "$W/out/log_$tag$SFX.log"; cp "$W/out/log_$tag$SFX.log" "$OUT/"; return 1; }
    npz=$W/out/scores_$tag$SFX.npz
    printf '%s,%s,%s,%s\n' "scores_$tag$SFX.npz" "$(sha256sum "$npz" | cut -c1-64)" "$(stat -c%s "$npz")" \
      "$(sha256sum "$wf" | cut -c1-64)" > "$W/out/receipt_$tag$SFX.csv"
    cp "$npz" "$W/out/log_$tag$SFX.log" "$W/out/receipt_$tag$SFX.csv" "$OUT/"
    echo "$tag scored $(( $(date +%s) - ts )) s $(date +%T): $(tail -1 "$W/out/log_$tag$SFX.log")"
  done
}
pids=()
for n in $NETS; do stream "$n" & pids+=($!); done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "RUN_END rc=$rc $(ls "$OUT"/scores_rel_*"$SFX".npz 2>/dev/null | wc -l) npz in $OUT, total $(( $(date +%s) - t0 )) s"
exit $rc

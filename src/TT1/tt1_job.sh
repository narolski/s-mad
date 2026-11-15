#!/bin/bash
# Threshold transfer on unseen genuine sources (TT1), registration TT1-S: scoring job body (WCSS H100 in the container,
# or local DGX test with TT1_LOCAL=1). Workload, all present before submission:
#   $ROOT/smad-next/packs/TT1/tt1_pack.tar (+.sha256)  images, list, PN1 code, base weights, rescore.py, gate_check.py
#   $ROOT/smad-next/packs/TT1/tt1_nets_<NETS>.tar (+.sha256)  networks (meta.json, last_trainable.pt) + gate references
#   $ROOT/smadcvpr/packs/pylib.tar, pylib_a12.tar (+.sha256)   python libraries for the container (as the AD4 tasks)
# Order: copy and verify tars into $TMPDIR; score the gate rows (fam gate) for every network; gate_check.py -> gate.json;
# on gate failure write the result tar (gate only) and exit 2 without scoring any TT1 row; else score fam tt1 for every
# network; one result tar back to $ROOT/smad-next/results/TT1/. TT1_MODE=test: 8 gate rows per network only (rows with
# stored scores), no gate decision, no TT1 row.
# Env: TT1_MODE (test|full), TT1_NETS (s401402), TT1_PACK_SHA, TT1_NETS_SHA; TT1_LOCAL=1 + TT1_PY + TT1_ROOT for DGX tests.
set -euo pipefail
MODE=${TT1_MODE:?test|full}; NETS=${TT1_NETS:?}; PSHA=${TT1_PACK_SHA:?}; NSHA=${TT1_NETS_SHA:?}
ROOT=${TT1_ROOT:-/lustre/pd03/hpc-narolski-1790461090}
SIF=/lustre/software-data/container-images/pytorch_latest.sif
W=${TMPDIR:?local scratch required}/tt1w; mkdir -p "$W"
case "$W" in /lustre*) echo "TT1 FAIL: work on Lustre"; exit 1 ;; esac
TAG=TT1_${NETS}_${MODE}_${SLURM_JOB_ID:-local}
OUTD=$ROOT/smad-next/results/TT1; mkdir -p "$OUTD"
die() { echo "TT1 FAIL: $*" >&2; exit 1; }
T0=$SECONDS
echo "TT1 $TAG host $(hostname) $(date +%FT%T)"
P=$ROOT/smad-next/packs/TT1
for f in "tt1_pack.tar:$PSHA" "tt1_nets_$NETS.tar:$NSHA"; do
  n=${f%%:*}; h=${f##*:}
  [ -f "$P/$n" ] || { echo "TT1: $P/$n missing; nothing to do"; exit 3; }
  cp "$P/$n" "$W/$n"
  [ "$(sha256sum "$W/$n" | cut -c1-64)" = "$h" ] || die "$n sha256"
  tar -C "$W" -xf "$W/$n" && rm -f "$W/$n"
done
(cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || die "pack SHA256SUMS"
(cd "$W/tt1nets" && sha256sum -c --quiet SHA256SUMS) || die "nets SHA256SUMS"
echo "TT1 packs ok ($((SECONDS - T0)) s)"
if [ "${TT1_LOCAL:-0}" != 1 ]; then
  for n in pylib pylib_a12; do
    cp "$ROOT/smadcvpr/packs/$n.tar" "$W/$n.tar"
    [ "$(sha256sum "$W/$n.tar" | cut -c1-64)" = "$(awk 'NR==1{print $1}' "$ROOT/smadcvpr/packs/$n.tar.sha256")" ] || die "$n sha256"
    tar -C "$W" -xf "$W/$n.tar" && rm -f "$W/$n.tar"
  done
fi
D=$W/tt1/data
if [ "$MODE" = test ]; then
  python3 - "$D/manifests/tt1_score.csv" "$D/manifests/tt1_test8.csv" <<'EOF'
import csv, sys
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["fam"] == "gate"][:8]
w = csv.DictWriter(open(sys.argv[2], "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
EOF
  MAN=tt1_test8.csv
else
  MAN=tt1_score.csv
fi
ENVS=(SMAD_DATA=$D HF_HOME=$W/tt1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1)
py() {
  if [ "${TT1_LOCAL:-0}" = 1 ]; then env "${ENVS[@]}" ${TT1_PY:?} "$@"
  else
    local e; e=$(IFS=,; echo "PYTHONPATH=$W/pylib_a12:$W/pylib:$W/tt1/code,${ENVS[*]}")
    apptainer exec --nv -B /lustre -B "$W" -B "$TMPDIR" --env "$e" "$SIF" python "$@"
  fi
}
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader || true
py -c "import sys, torch, timm, numpy, PIL; print('TT1 env', sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))" | tee "$W/versions.txt"
R=$W/res/$TAG; mkdir -p "$R/scores"
cp "$W/versions.txt" "$R/"; nvidia-smi --query-gpu=name,uuid,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
NETL=$(ls "$W/tt1nets/nets")
finish() {
  echo "pack_sha256 $PSHA nets_sha256 $NSHA mode $MODE wall_s $((SECONDS - T0)) host $(hostname) job ${SLURM_JOB_ID:-local}" > "$R/task_info.txt"
  tar -C "$W/res" -cf "$W/$TAG.tar" "$TAG"
  cp "$W/$TAG.tar" "$OUTD/$TAG.tar.part"
  (cd "$W" && sha256sum "$TAG.tar") > "$W/$TAG.tar.sha256"
  [ "$(sha256sum "$OUTD/$TAG.tar.part" | cut -c1-64)" = "$(cut -c1-64 "$W/$TAG.tar.sha256")" ] || die "copy-back sha256"
  mv "$OUTD/$TAG.tar.part" "$OUTD/$TAG.tar"; cp "$W/$TAG.tar.sha256" "$OUTD/"
  echo "TT1_RESULT $OUTD/$TAG.tar $(cut -c1-64 "$W/$TAG.tar.sha256")"
}
for n in $NETL; do
  py "$W/tt1/bin/rescore.py" --resdir "$W/tt1nets/nets/$n" --code "$W/tt1/code" --manifest "$MAN" --fam gate \
    --out "$R/scores/${n}__gate.npz" --workers 7 2>&1 | tail -1
done
echo "TT1 gate rows scored ($((SECONDS - T0)) s)"
if [ "$MODE" = test ]; then
  py - "$R/scores" "$W/tt1nets/gate_ref" <<'EOF' | tee "$R/test8_diff.txt"
import sys, pathlib, numpy as np
for f in sorted(pathlib.Path(sys.argv[1]).glob("*__gate.npz")):
    t = f.name.split("__")[0]; z = np.load(f); r = np.load(pathlib.Path(sys.argv[2]) / f"{t}.npz")
    m = dict(zip(r["id"].tolist(), r["logit"].tolist()))
    d = [abs(float(l) - m[i]) for i, l in zip(z["id"].tolist(), z["logit"].tolist())]
    print(t, len(d), "max_abs", max(d))
EOF
  finish; exit 0
fi
set +e
py "$W/tt1/bin/gate_check.py" --scores "$R/scores" --ref "$W/tt1nets/gate_ref" --manifest "$D/manifests/tt1_score.csv" \
  --out "$R/gate.json" | tee "$R/gate.txt"
rc=${PIPESTATUS[0]}
set -e
if [ "$rc" != 0 ]; then echo "TT1 GATE FAILED (rc $rc): no TT1 row scored"; finish; exit 2; fi
for n in $NETL; do
  py "$W/tt1/bin/rescore.py" --resdir "$W/tt1nets/nets/$n" --code "$W/tt1/code" --manifest "$MAN" --fam tt1 \
    --out "$R/scores/${n}__tt1.npz" --workers 7 2>&1 | tail -1
done
echo "TT1 tt1 rows scored ($((SECONDS - T0)) s)"
finish

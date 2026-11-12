#!/bin/bash
# TT1 deviation TT1-D1: the rented A100 side (image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, as the PN1 hosts).
# Layout /workspace/tt1/{packs,bin,work,results,logs,rc}. Steps:
#  1 pins: pack, network tar and bin scripts against the sha256 given as arguments / in bin/SHA256SUMS;
#  2 pip pins exactly as src/PN1/rented/remote_setup.sh (torch held at the image's version), versions asserted;
#  3 extract the pack and the network tar, check both SHA256SUMS;
#  4 zero-GPU-budget diagnostic diag_stack.py on 5 FFHQ genuine ids (A_s401) -> diag_a100.npz;
#  5 gate rows (fam gate) for all 12 networks with rescore.py from the pack -> gate_check_a100.py -> gate.json;
#    on failure: result tar with rc GATE_FAILED, exit 2, no TT1 row scored;
#  6 TT1 rows (fam tt1) for all 12 networks; result tar with rc 0.
# The result tar always carries: scores, gate.json, diag, versions, pip log, GPU, rc. Args: PACK_SHA NETS_SHA [test]
set -u
PSHA=${1:?}; NSHA=${2:?}; MODE=${3:-full}
B=${TT1_REMOTE_BASE:-/workspace/tt1}; PY=${TT1_REMOTE_PY:-python}
T=TT1_A100_s401402_$MODE; W=$B/work; R=$W/res/$T
mkdir -p "$B/results" "$B/logs" "$B/rc" "$R/scores"
log() { echo "$(date +%FT%T) $*" | tee -a "$R/calls.log"; }
finish() {
  local rc=$1
  echo "$rc" > "$R/rc"; cp "$R/rc" "$B/rc/$T"
  cp "$B/logs/pip.log" "$R/" 2>/dev/null || true
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
  tar -C "$W/res" -cf "$B/results/$T.tar" "$T" && (cd "$B/results" && sha256sum "$T.tar" > "$T.tar.sha256")
  (cd "$B/logs" && sha256sum * > "$B/results/logs.sha256") 2>/dev/null || true
  date > "$B/DONE"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
log "start mode $MODE"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 20 ] || abort "disk"
[ "$(sha256sum < "$B/packs/tt1_pack.tar" | cut -c1-64)" = "$PSHA" ] || abort "pack pin"
[ "$(sha256sum < "$B/packs/tt1_nets_s401402.tar" | cut -c1-64)" = "$NSHA" ] || abort "nets pin"
(cd "$B/bin" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins"
if [ "${TT1_SKIP_PIP:-0}" != 1 ]; then
  $PY -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt" || abort torch
  $PY -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
    numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || abort pip
  $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1" || abort versions
fi
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0))" > "$R/versions.txt" 2>&1 || abort env
log "env $(cat "$R/versions.txt")"
rm -rf "$W/tt1" "$W/tt1nets"
tar -C "$W" -xf "$B/packs/tt1_pack.tar" 2>/dev/null && (cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || abort "pack sums"
tar -C "$W" -xf "$B/packs/tt1_nets_s401402.tar" 2>/dev/null && (cd "$W/tt1nets" && sha256sum -c --quiet SHA256SUMS) || abort "nets sums"
log "packs ok"
D=$W/tt1/data
export SMAD_DATA=$D HF_HOME=$W/tt1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
MAN=tt1_score.csv
if [ "$MODE" = test ]; then
  $PY - "$D/manifests/tt1_score.csv" "$D/manifests/tt1_test8.csv" <<'EOF'
import csv, sys
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["fam"] == "gate"][:8]
w = csv.DictWriter(open(sys.argv[2], "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
EOF
  MAN=tt1_test8.csv
fi
$PY "$B/bin/diag_stack.py" --data "$D" --code "$W/tt1/code" --net "$W/tt1nets/nets/PN1_A_s401" \
  --ids fq016604,fq010376,fq008900,fq008528,fq011276 --out "$R/diag_a100.npz" > "$R/diag_a100.log" 2>&1 \
  && log "diag ok" || log "diag FAILED (diagnostic only; continuing)"
NETL=$(ls "$W/tt1nets/nets")
# deviation TT1-D2: the FFHQ gate rows are scored as in the runs that produced the stored scores: the HN2 list alone
# (pn1_hn2.csv, 5,000 rows, fam ffhq, original order, rescore.py batch 64)
[ "$(sha256sum < "$B/packs/tt1_hn2.tar" | cut -c1-64)" = "7648b15ac67798e7601e24b790e62ef86687949f9af0ac440065c2fcb6ac42a7" ] || abort "hn2 pin"
rm -rf "$W/pn1h"; tar -C "$W" -xf "$B/packs/tt1_hn2.tar" && (cd "$W/pn1h" && sha256sum -c --quiet SHA256SUMS) || abort "hn2 sums"
for n in $NETL; do
  SMAD_DATA=$W/pn1h/data $PY "$W/tt1/bin/rescore.py" --resdir "$W/tt1nets/nets/$n" --code "$W/tt1/code" --manifest pn1_hn2.csv \
    --fam ffhq --out "$R/scores/${n}__hn2.npz" --workers 7 >> "$B/logs/score.log" 2>&1 || abort "hn2 score $n"
  log "hn2 scored $n"
done
for n in $NETL; do
  $PY "$W/tt1/bin/rescore.py" --resdir "$W/tt1nets/nets/$n" --code "$W/tt1/code" --manifest "$MAN" --fam gate \
    --out "$R/scores/${n}__gate.npz" --workers 7 >> "$B/logs/score.log" 2>&1 || abort "gate score $n"
  log "gate scored $n"
done
if [ "$MODE" = test ]; then log "test done"; finish 0; exit 0; fi
$PY "$B/bin/gate_check_a100.py" --require-hn2 --scores "$R/scores" --ref "$W/tt1nets/gate_ref" --manifest "$D/manifests/tt1_score.csv" \
  --out "$R/gate.json" > "$R/gate.txt" 2>&1
grc=$?
log "gate rc $grc: $(head -c 300 "$R/gate.txt")"
if [ "$grc" != 0 ]; then finish GATE_FAILED; exit 2; fi
for n in $NETL; do
  $PY "$W/tt1/bin/rescore.py" --resdir "$W/tt1nets/nets/$n" --code "$W/tt1/code" --manifest "$MAN" --fam tt1 \
    --out "$R/scores/${n}__tt1.npz" --workers 7 >> "$B/logs/score.log" 2>&1 || abort "tt1 score $n"
  log "tt1 scored $n"
done
finish 0

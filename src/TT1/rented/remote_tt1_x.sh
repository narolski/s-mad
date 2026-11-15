#!/bin/bash
# TT1 extension block TT1-X (prereg_x_block.md): same steps as remote_tt1_fs.sh (TT1-FS), parameterized by TAG and
# BIN so that it can run after the main job on the same host without touching its files. Copy of remote_tt1_fs.sh., run ON THE FRESH-SEED HOST pn1fs (A100 PCIe 40 GB, image
# pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, pip pins of remote_setup.sh already installed by the FS1 setup).
# Inputs on the host: /workspace/tt1/packs/tt1_pack.tar (staged), /workspace/pn1/root/packs/PN1/pn1_pack_fs.tar and the
# FS1 result tars /workspace/pn1/root/results/PN1/PN1_<arm>_s<seed>.tar (+ .sha256) (made there by the FS1 queue);
# /workspace/tt1/bin/{remote_tt1_fs.sh, rescore_tf32.py, gate_check_fs.py, SHA256SUMS, nets_pins.txt}.
# Steps: pins; versions asserted (no pip); takes the host's FS1 queue lock so no fit runs at the same time; extract;
# per network: gate = every FS1 eval row (19,797) scored in manifest order, batch 64, TF32 on (rescore_tf32.py) against
# the fit's stored scores_eval.npz (byte identity); passing networks only: the 30,994 TT1 rows (fam tt1) with rescore.py
# unchanged (PyTorch defaults, as for seeds 401/402); one result tar TT1_A100_<lease>_fs.tar + sha256; DONE.
# Args: TT1_PACK_SHA FS_PACK_SHA LEASE TAG [GATE_PACK_PATH]
set -u
PSHA=${1:?}; FSHA=${2:?}; LEASE=${3:-pn1fs}; TAG=${4:?tag}
B=${TT1_FS_B:-/workspace/tt1}; P=${TT1_FS_P:-/workspace/pn1}; PY=${TT1_FS_PY:-python}
T=TT1_${LEASE}_${TAG}; W=$B/work_${TAG}; R=$W/res/$T; BIN=$B/bin_${TAG}
GPACK=${5:-$P/root/packs/PN1/pn1_pack_fs.tar}; GTOP=${TT1_GATE_TOP:-pn1}; GMAN=${TT1_GATE_MANIFEST:-pn1_eval.csv}
mkdir -p "$B/results" "$B/logs" "$R/scores"
log() { echo "$(date +%FT%T) $*" | tee -a "$R/calls.log"; }
finish() {
  echo "$1" > "$R/rc"
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
  tar -C "$W/res" -cf "$B/results/$T.tar" "$T" && (cd "$B/results" && sha256sum "$T.tar" > "$T.tar.sha256")
  (cd "$B/logs" && sha256sum * > "$B/results/logs_${TAG}.sha256") 2>/dev/null || true
  date > "$B/DONE_${TAG}"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
log "start (waiting for the FS1 queue lock)"
exec 9> "$P/fs_queue.lock"; flock 9
log "lock taken"
# I4: deadline check (lease deadline 15:51 CET = epoch 1794581505): skip if under 60 min remain
[ "$(date +%s)" -le $(( ${TT1_DEADLINE_EPOCH:?} - 3600 )) ] || abort "under 60 min before the lease deadline"
# m5: pinned GPU (the GPU that stored the FS1 scores)
[ "${TT1_FS_SKIP_VERSIONS:-0}" = 1 ] || nvidia-smi --query-gpu=uuid --format=csv,noheader | grep -q "${TT1_GPU_UUID:?pinned GPU UUID}" || abort "GPU UUID"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 30 ] || abort "disk < 30 GB"
(cd "$BIN" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins"
[ "$(sha256sum < "$B/packs/tt1_pack.tar" | cut -c1-64)" = "$PSHA" ] || abort "tt1 pack pin"
[ "$(sha256sum < "$GPACK" | cut -c1-64)" = "$FSHA" ] || abort "fs pack pin"
[ "${TT1_FS_SKIP_VERSIONS:-0}" = 1 ] || $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'" || abort versions
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.backends.cudnn.version(), timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0)); print('cudnn.benchmark', torch.backends.cudnn.benchmark, 'cudnn.deterministic', torch.backends.cudnn.deterministic, 'matmul.allow_tf32', torch.backends.cuda.matmul.allow_tf32, 'cudnn.allow_tf32', torch.backends.cudnn.allow_tf32, 'sdp flash', torch.backends.cuda.flash_sdp_enabled(), 'mem_efficient', torch.backends.cuda.mem_efficient_sdp_enabled(), 'math', torch.backends.cuda.math_sdp_enabled())" > "$R/versions.txt"
rm -rf "$W/tt1" "$W/fs" "$W/nets"; mkdir -p "$W/fs" "$W/nets"
tar -C "$W" -xf "$B/packs/tt1_pack.tar" 2>/dev/null && (cd "$W/tt1" && sha256sum -c --quiet SHA256SUMS) || abort "tt1 pack sums"
tar -C "$W/fs" -xf "$GPACK" "$GTOP/data/eval" "$GTOP/data/manifests/$GMAN" 2>/dev/null || abort "fs extract"
# nets: every pinned FS1 result tar (nets_pins.txt: "<sha256>  <task>.tar")
while read -r h t; do
  f="$P/root/results/PN1/$t"
  [ "$(sha256sum < "$f" | cut -c1-64)" = "$h" ] || abort "net pin $t"
  n=${t%.tar}; mkdir -p "$W/nets/$n"
  tar -xOf "$f" "$n/meta.json" > "$W/nets/$n/meta.json" && tar -xOf "$f" "$n/last_trainable.pt" > "$W/nets/$n/last_trainable.pt" \
    && tar -xOf "$f" "$n/scores_eval.npz" > "$W/nets/$n/scores_eval.npz" || abort "net extract $t"
done < "$BIN/nets_pins.txt"
log "packs and $(ls "$W/nets" | wc -l) networks ok"
# gate manifest: the FS1 eval manifest with every fam set to 'all' (row order unchanged), so rescore.py scores every row
$PY - "$W/fs/$GTOP/data/manifests/$GMAN" "$W/fs/$GTOP/data/manifests/fsgate_all.csv" <<'EOF'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
import os
for r in rows: r["fam"] = "all"
if os.environ.get("TT1_FS_TEST") == "1": rows = rows[:64]
w = csv.DictWriter(open(sys.argv[2], "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
EOF
export HF_HOME=$W/tt1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
for n in $(ls "$W/nets"); do
  SMAD_DATA=$W/fs/$GTOP/data $PY "$BIN/rescore_tf32.py" "$W/tt1/bin/rescore.py" --resdir "$W/nets/$n" --code "$W/tt1/code" \
    --manifest fsgate_all.csv --fam all --out "$R/scores/${n}__fsgate.npz" --workers 7 >> "$B/logs/${TAG}_score.log" 2>&1 || abort "gate score $n"
  log "gate scored $n"
done
$PY "$BIN/gate_check_fs.py" --scores "$R/scores" --nets "$W/nets" --out "$R/gate_fs.json" > "$R/gate_fs.txt" 2>&1 || abort "gate check"
log "$(cat "$R/gate_fs.txt")"
if [ "${TT1_FS_TEST:-0}" = 1 ]; then log "test: stop after the gate"; finish 0; exit 0; fi
PASSED=$($PY -c "import json; print(' '.join(json.load(open('$R/gate_fs.json'))['passed']))")
for n in $PASSED; do
  SMAD_DATA=$W/tt1/data $PY "$W/tt1/bin/rescore.py" --resdir "$W/nets/$n" --code "$W/tt1/code" --manifest tt1_score.csv \
    --fam tt1 --out "$R/scores/${n}__tt1.npz" --workers 7 >> "$B/logs/${TAG}_score.log" 2>&1 || abort "tt1 score $n"
  SMAD_DATA=$W/tt1/data $PY "$W/tt1/bin/rescore.py" --resdir "$W/nets/$n" --code "$W/tt1/code" --manifest tt1_score.csv \
    --fam gate --out "$R/scores/${n}__gate.npz" --workers 7 >> "$B/logs/${TAG}_score.log" 2>&1 || abort "ref score $n"
  log "tt1 scored $n"
done
finish 0

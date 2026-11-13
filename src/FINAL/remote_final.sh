#!/bin/bash
# Sealed MAD22 read (FINAL), run on one fresh A100-PCIE-40GB lease (image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime).
# Inputs on the host: $B/packs/<read_id>_pack.tar, $B/bin/{remote_final.sh, gate_check_final.py, final_config.json,
# SHA256SUMS}. Two modes:
#   FINAL_DRYRUN=1  the GATE DRY RUN: steps 1-4 only (development rows only), once (marker STARTED_DRYRUN), result
#                   <read_id>_<lease>_dryrun.tar, DONE_DRYRUN. It never reads the benchmark manifest.
#   default         THE READ: steps 1-5, once (marker STARTED), result <read_id>_<lease>.tar, DONE.
# Steps:
#   1 pins (bin sums, pack sha256 and config sha256 as arguments), GPU model A100-PCIE-40GB, one GPU, GPU idle, disk
#   2 own venv (system site packages + the PN1 pip pins, torch held by constraints); versions asserted and recorded
#   3 extract the pack; SHA256SUMS checked; network tars checked against final_config.json; meta, weights and stored
#     development scores extracted per network
#   -> the one-start marker is created here, after every check that scores nothing and before the first score
#   4 GATE: every network scores final_gate.csv (rescore.py unchanged through rescore_tf32.py, TF32 on, batch 64);
#     gate_check_final.py requires byte identity on every row for every network. Any failure: stop, no benchmark row
#   5 MAD22 (read only): every network scores final_bench.csv (same scorer path), in config order
#   6 one result tar + sha256, logs sha256, DONE / DONE_DRYRUN (written on success and on FATAL)
# Args: PACK_SHA CONFIG_SHA LEASE
set -u
PSHA=${1:?}; CSHA=${2:?}; LEASE=${3:?}
B=${FINAL_B:-/workspace/final}; W=$B/work
DRY=${FINAL_DRYRUN:-0}
if [ "$DRY" = 1 ]; then MARK=STARTED_DRYRUN; DONEF=DONE_DRYRUN; SUF=_dryrun; LOGS=logs_dryrun.sha256; else MARK=STARTED; DONEF=DONE; SUF=; LOGS=logs_final.sha256; fi
mkdir -p "$B/results" "$B/logs"
exec 8> "$B/run.lock"
flock -n 8 || { echo "$(date +%FT%T) refused: another FINAL job (dry run or read) is running on this host" >> "$B/logs/second_start.log"; exit 8; }
rm -f "$B/$DONEF.prev"; [ -e "$B/$DONEF" ] && [ ! -e "$B/$MARK" ] && mv "$B/$DONEF" "$B/$DONEF.prev"
[ -e "$B/$MARK" ] && { echo "$(date +%FT%T) FATAL second start refused: $B/$MARK exists" >> "$B/logs/second_start.log"; exit 9; }
RID=$(python3 -c "import json; print(json.load(open('$B/bin/final_config.json'))['read_id'])" 2>/dev/null || echo FINAL)
T=${RID}_${LEASE}${SUF}; R=$W/res/$T
rm -rf "$R"; mkdir -p "$R/scores"
log() { echo "$(date +%FT%T) $*" | tee -a "$R/calls.log"; }
finish() {
  echo "$1" > "$R/rc"
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
  cp "$B/bin/final_config.json" "$R/final_config.json" 2>/dev/null || true
  tar -C "$W/res" -cf "$B/results/$T.tar" "$T" && (cd "$B/results" && sha256sum "$T.tar" > "$T.tar.sha256")
  (cd "$B/logs" && sha256sum * > "$B/results/$LOGS") 2>/dev/null || true
  date > "$B/$DONEF"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
log "start lease $LEASE mode $([ "$DRY" = 1 ] && echo dryrun || echo read)"
(cd "$B/bin" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins (before any score)"
[ "$(sha256sum < "$B/bin/final_config.json" | cut -c1-64)" = "$CSHA" ] || abort "config pin (before any score)"
PACK=$B/packs/${RID}_pack.tar
[ "$(sha256sum < "$PACK" | cut -c1-64)" = "$PSHA" ] || abort "pack pin (before any score)"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 20 ] || abort "disk < 20 GB (before any score)"
if [ "${FINAL_TEST:-0}" != 1 ]; then
  nvidia-smi --query-gpu=name --format=csv,noheader | grep -q "A100-PCIE-40GB" || abort "GPU model is not A100-PCIE-40GB (before any score)"
  [ "$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)" = 1 ] || abort "more than one GPU visible (before any score)"
  [ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ] || abort "GPU busy (before any score)"
fi
if [ "${FINAL_SKIP_VENV:-0}" != 1 ]; then
  [ -x "$B/venv/bin/python" ] || python -m venv --system-site-packages "$B/venv" || abort "venv (before any score)"
  PY=$B/venv/bin/python
  $PY -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt" || abort "torch (before any score)"
  $PY -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
    numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip$SUF.log" 2>&1 || abort "pip (before any score)"
  $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and torch.version.cuda == '12.1' and torch.backends.cudnn.version() == 8902 and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'" || abort "versions (before any score)"
else
  PY=${FINAL_PY:?}
fi
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.backends.cudnn.version(), timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0)); print('defaults: cudnn.benchmark', torch.backends.cudnn.benchmark, 'cudnn.deterministic', torch.backends.cudnn.deterministic, 'matmul.allow_tf32', torch.backends.cuda.matmul.allow_tf32, 'cudnn.allow_tf32', torch.backends.cudnn.allow_tf32, 'sdp flash', torch.backends.cuda.flash_sdp_enabled(), 'mem_efficient', torch.backends.cuda.mem_efficient_sdp_enabled(), 'math', torch.backends.cuda.math_sdp_enabled()); print('scoring: rescore_tf32.py sets matmul.allow_tf32=True, cudnn.allow_tf32=True; float32; eval; batch 64')" > "$R/versions.txt" 2>&1 || abort "env (before any score)"
$PY -m pip freeze > "$R/pip_freeze.txt" 2>/dev/null || true
rm -rf "$W/final" "$W/nets"; mkdir -p "$W/nets"
tar -C "$W" -xf "$PACK" 2>/dev/null && (cd "$W/final" && sha256sum -c --quiet SHA256SUMS) || abort "pack sums (before any score)"
log "pack ok"
NETS=$($PY -c "import json; print(' '.join(n['name'] for n in json.load(open('$B/bin/final_config.json'))['networks']))")
for n in $NETS; do
  h=$($PY -c "import json; print({x['name']: x['sha256'] for x in json.load(open('$B/bin/final_config.json'))['networks']}['$n'])")
  f=$W/final/nets/$n.tar
  [ "$(sha256sum < "$f" | cut -c1-64)" = "$h" ] || abort "net pin $n (before any score)"
  mkdir -p "$W/nets/$n"
  for m in meta.json last_trainable.pt scores_eval.npz; do tar -xOf "$f" "$n/$m" > "$W/nets/$n/$m" || abort "net extract $n $m (before any score)"; done
done
log "networks ok: $NETS"
# ---- the one-start marker: every check above scored nothing; from here on scores are made
set -o noclobber
if ! { echo "$(date +%FT%T) $LEASE" > "$B/$MARK"; } 2>/dev/null; then
  log "FATAL second start refused: $B/$MARK exists"; exit 9
fi
set +o noclobber
export HF_HOME=$W/final/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
SC="$PY $W/final/bin/rescore_tf32.py $W/final/bin/rescore.py"
for n in $NETS; do
  SMAD_DATA=$W/final/data $SC --resdir "$W/nets/$n" --code "$W/final/code" --manifest final_gate.csv --fam gate \
    --out "$R/scores/${n}__gate.npz" --workers 7 >> "$B/logs/score$SUF.log" 2>&1 || abort "gate score $n"
  log "gate scored $n"
done
$PY "$B/bin/gate_check_final.py" --config "$B/bin/final_config.json" --manifest "$W/final/data/manifests/final_gate.csv" \
  --scores "$R/scores" --nets "$W/nets" --out "$R/gate.json" > "$R/gate.txt" 2>&1
grc=$?
log "$(cat "$R/gate.txt")"
[ "$grc" = 0 ] || abort "GATE FAILED (no benchmark row scored)"
if [ "$DRY" = 1 ]; then log "dry run: gate passed; stop (no benchmark row is read in a dry run)"; finish 0; exit 0; fi
touch "$R/GATE_PASSED"
for n in $NETS; do
  SMAD_DATA=$W/final/data $SC --resdir "$W/nets/$n" --code "$W/final/code" --manifest final_bench.csv --fam final \
    --out "$R/scores/${n}__final.npz" --workers 7 >> "$B/logs/score.log" 2>&1 || abort "bench score $n"
  log "bench scored $n"
done
finish 0

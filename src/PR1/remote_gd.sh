#!/bin/bash
# PR1 GD0/GD1/GD2 scoring job (prereg.md section 6), run ON pn1fs (A100 PCIe 40 GB GPU-5bd20020, image
# pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime with the FS1 pip pins). Writes only under /workspace/pr1.
# Order (agreed with the TT1 owner and the lead): wait for /workspace/tt1/DONE_FS, then for DONE_sp or NO_SP for at
# most 30 min, then take /workspace/pn1/fs_queue.lock (no fit or other scoring runs at the same time).
# Per network (15 FS1 tars, pinned): gate = all 19,797 FS1 eval rows in manifest order, batch 64, TF32 on
# (rescore_tf32.py -> rescore.py unchanged) against the stored scores_eval.npz (gate_gd.py, tolerance rule);
# then the GD rows (fam gd0, gd1, gd2 of pr1_gd.csv), same scorer. GD rows of a gate-failed network are never read
# (the reader drops them). One tar /workspace/pr1/results/PR1_GD_pn1fs.tar + sha256; /workspace/pr1/PR1_DONE.
# Args: GD_PACK_SHA FS_PACK_SHA     (env PR1_TEST=1: 2 networks, 64 gate rows, the limit8 pack, no waits/lock)
set -u
GSHA=${1:?}; FSHA=${2:?}
B=${PR1_B:-/workspace/pr1}; P=${PR1_P:-/workspace/pn1}; T=${PR1_T:-/workspace/tt1}; PY=${PR1_PY:-python}
TEST=${PR1_TEST:-0}; SKIP=${PR1_SKIP_PLATFORM:-0}
NAME=PR1_GD_pn1fs; [ "$TEST" = 1 ] && NAME=PR1_GD_test
W=$B/work_$(date +%s); R=$W/res/$NAME   # F1: a new work folder per run; nothing is deleted
[ -e "$B/results/$NAME.tar" ] && { echo "result tar exists; refusing"; exit 1; }
mkdir -p "$B/results" "$B/logs" "$R/scores"
log() { echo "$(date +%FT%T) $*" | tee -a "$R/calls.log"; }
finish() {
  echo "$1" > "$R/rc"
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$R/gpu.txt" 2>&1 || true
  cp "$B/logs/gd_score.log" "$R/" 2>/dev/null || true
  tar -C "$W/res" -cf "$B/results/$NAME.tar" "$NAME" && (cd "$B/results" && sha256sum "$NAME.tar" > "$NAME.tar.sha256")
  [ "$TEST" = 1 ] || date > "$B/PR1_DONE"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
if [ "$TEST" != 1 ]; then
  log "waiting for $T/DONE_FS"
  until [ -f "$T/DONE_FS" ]; do sleep 30; done
  t0=$(date +%s); log "DONE_FS seen; waiting for DONE_sp or NO_SP (max 30 min)"
  until [ -f "$T/DONE_sp" ] || [ -f "$T/NO_SP" ] || [ $(( $(date +%s) - t0 )) -ge 1800 ]; do sleep 30; done
  log "waiting for the FS1 queue lock"
  exec 9> "$P/fs_queue.lock"; flock 9
  log "lock taken"
  [ "$(date +%s)" -le $((1794581505 - 2700)) ] || abort "under 45 min before the lease deadline"
fi
[ "$SKIP" = 1 ] || nvidia-smi --query-gpu=uuid --format=csv,noheader | grep -q "GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad" || abort "GPU UUID"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 25 ] || abort "disk < 25 GB"
(cd "$B/bin" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins"
GP=$B/packs/pr1_gd.tar; [ "$TEST" = 1 ] && GP=$B/packs/pr1_gd_limit8.tar
[ "$(sha256sum < "$GP" | cut -c1-64)" = "$GSHA" ] || abort "gd pack pin"
[ "$(sha256sum < "$P/root/packs/PN1/pn1_pack_fs.tar" | cut -c1-64)" = "$FSHA" ] || abort "fs pack pin"
[ "$SKIP" = 1 ] || $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'" || abort versions
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.backends.cudnn.version(), timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0)); print('cudnn.benchmark', torch.backends.cudnn.benchmark, 'deterministic', torch.backends.cudnn.deterministic, 'sdp flash', torch.backends.cuda.flash_sdp_enabled(), 'mem_efficient', torch.backends.cuda.mem_efficient_sdp_enabled(), 'math', torch.backends.cuda.math_sdp_enabled())" > "$R/versions.txt"
mkdir -p "$W/fs" "$W/gd" "$W/nets"
tar -C "$W/fs" -xf "$P/root/packs/PN1/pn1_pack_fs.tar" pn1/code pn1/hf pn1/SHA256SUMS pn1/data/eval pn1/data/manifests/pn1_eval.csv 2>/dev/null || abort "fs extract"
(cd "$W/fs/pn1" && grep -E "  (code|hf)/|  data/manifests/pn1_eval.csv" SHA256SUMS | sha256sum -c --quiet) || abort "fs code/hf/manifest sums"
[ "$(sha256sum < "$W/fs/pn1/data/manifests/pn1_eval.csv" | cut -c1-64)" = f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045 ] || abort "eval manifest pin"
tar -C "$W/gd" -xf "$GP" && (cd "$W/gd/pr1g" && sha256sum -c --quiet SHA256SUMS) || abort "gd pack sums"
while read -r h t; do
  f="$P/root/results/PN1/$t"
  [ "$(sha256sum < "$f" | cut -c1-64)" = "$h" ] || abort "net pin $t"
  n=${t%.tar}; mkdir -p "$W/nets/$n"
  for m in meta.json last_trainable.pt scores_eval.npz; do tar -xOf "$f" "$n/$m" > "$W/nets/$n/$m" || abort "net extract $t"; done
done < <(if [ "$TEST" = 1 ]; then head -2 "$B/bin/nets_pins.txt"; else cat "$B/bin/nets_pins.txt"; fi)
log "packs and $(ls "$W/nets" | wc -l) networks ok"
$PY - "$W/fs/pn1/data/manifests/pn1_eval.csv" "$W/fs/pn1/data/manifests/gate_all.csv" <<'EOF'
import csv, os, sys
rows = list(csv.DictReader(open(sys.argv[1])))
for r in rows: r["fam"] = "all"
if os.environ.get("PR1_TEST") == "1": rows = rows[:64]
w = csv.DictWriter(open(sys.argv[2], "w", newline=""), fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
EOF
export HF_HOME=$W/fs/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
RS=$B/bin/rescore.py
for n in $(ls "$W/nets"); do
  SMAD_DATA=$W/fs/pn1/data $PY "$B/bin/rescore_tf32.py" "$RS" --resdir "$W/nets/$n" --code "$W/fs/pn1/code" \
    --manifest gate_all.csv --fam all --out "$R/scores/${n}__gate.npz" --workers 7 >> "$B/logs/gd_score.log" 2>&1 || abort "gate score $n"
  for FAM in gd0 gd1 gd2; do
    SMAD_DATA=$W/gd/pr1g/data $PY "$B/bin/rescore_tf32.py" "$RS" --resdir "$W/nets/$n" --code "$W/fs/pn1/code" \
      --manifest pr1_gd.csv --fam $FAM --out "$R/scores/${n}__$FAM.npz" --workers 7 >> "$B/logs/gd_score.log" 2>&1 || abort "$FAM score $n"
  done
  log "scored $n"
done
$PY "$B/bin/gate_gd.py" --scores "$R/scores" --nets "$W/nets" --out "$R/gate_gd.json" $([ "$TEST" = 1 ] && echo --test) > "$R/gate_gd.txt" 2>&1 || abort "gate check"
log "$(cat "$R/gate_gd.txt")"
cp "$W/gd/pr1g/data/manifests/pr1_gd.csv" "$R/"
finish 0

#!/bin/bash
# Amendment C2P-R (draft): re-scoring of contrast 2-prime ON THE FRESH-SEED HOST pn1fs (A100 PCIe 40 GB that trained the
# FS1 networks; image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime with the FS1 pip pins, already installed).
# Inputs on the host: /workspace/pn1/root/packs/PN1/pn1_pack_fs.tar (code, base weights, FS1 eval images),
# the FS1 result tars /workspace/pn1/root/results/PN1/PN1_<arm>_s<seed>.tar, /workspace/c2pr/packs/c2pr_pack.tar
# (hold-out images + MS1 manifest), /workspace/c2pr/bin/{remote_c2pr.sh, rescore.py, rescore_tf32.py, SHA256SUMS,
# nets_pins.txt}. Steps: takes the host's FS1 queue lock; deadline, GPU UUID, disk, pins, versions; extract; per
# network (15) and family (af0, ffhq, ms1ffhq): rescore.py unchanged through rescore_tf32.py (TF32 on, batch 64), in
# one job; result tar C2P_fs.tar (out/C2P_<task>_<fam>.npz, env.txt, gpu.txt, rc) + sha256; DONE.
# Args: FS_PACK_SHA C2PR_PACK_SHA
set -u
FSHA=${1:?}; CSHA=${2:?}
B=${C2PR_B:-/workspace/c2pr}; P=${C2PR_P:-/workspace/pn1}; PY=${C2PR_PY:-python}
W=$B/work_$(date +%s); O=$W/out
mkdir -p "$B/results" "$B/logs"
log() { echo "$(date +%FT%T) $*" | tee -a "$B/logs/calls.log"; }
finish() {
  mkdir -p "$O"; echo "$1" > "$O/rc"
  nvidia-smi --query-gpu=index,uuid,name,driver_version --format=csv,noheader > "$O/gpu.txt" 2>&1 || true
  tar -C "$W" -cf "$B/results/C2P_fs.tar" out && (cd "$B/results" && sha256sum C2P_fs.tar > C2P_fs.tar.sha256)
  (cd "$B/logs" && sha256sum * > "$B/results/logs.sha256") 2>/dev/null || true
  date > "$B/DONE"
}
abort() { log "FATAL $1"; finish "FATAL $1"; exit 1; }
log "start (waiting for the FS1 queue lock)"
exec 9> "$P/fs_queue.lock"; flock 9
log "lock taken"
[ "$(date +%s)" -le $((${C2PR_DEADLINE:-1794581505} - 3600)) ] || abort "under 60 min before the lease deadline"
[ "${C2PR_SKIP_GPU:-0}" = 1 ] || nvidia-smi --query-gpu=uuid --format=csv,noheader | grep -q "GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad" || abort "GPU UUID"
[ "$(df --output=avail -B1G "$B" | tail -1 | tr -d ' ')" -ge 20 ] || abort "disk < 20 GB"
(cd "$B/bin" && sha256sum -c --quiet SHA256SUMS) || abort "bin pins"
[ "$(sha256sum < "$P/root/packs/PN1/pn1_pack_fs.tar" | cut -c1-64)" = "$FSHA" ] || abort "fs pack pin"
[ "$(sha256sum < "$B/packs/c2pr_pack.tar" | cut -c1-64)" = "$CSHA" ] || abort "c2pr pack pin"
[ "${C2PR_SKIP_GPU:-0}" = 1 ] || $PY -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'" || abort versions
[ ! -e "$B/results/C2P_fs.tar" ] || { log "a result tar exists already: refusing (nothing overwritten)"; exit 1; }
mkdir -p "$O" "$W/nets"
tar -C "$W" -xf "$P/root/packs/PN1/pn1_pack_fs.tar" pn1/code pn1/hf pn1/data/eval 2>/dev/null || abort "fs extract"
tar -C "$W" -xf "$B/packs/c2pr_pack.tar" 2>/dev/null && (cd "$W/pn1c" && sha256sum -c --quiet SHA256SUMS) || abort "c2pr pack sums"
mkdir -p "$W/pn1/data/eval/ms1" "$W/pn1/data/manifests"
cp -r "$W/pn1c/data/eval/ms1/." "$W/pn1/data/eval/ms1/" && cp "$W/pn1c/data/manifests/ms1_eval.csv" "$W/pn1/data/manifests/" || abort "merge"
while read -r h t; do
  f="$P/root/results/PN1/$t"
  [ "$(sha256sum < "$f" | cut -c1-64)" = "$h" ] || abort "net pin $t"
  n=${t%.tar}; mkdir -p "$W/nets/$n"
  tar -xOf "$f" "$n/meta.json" > "$W/nets/$n/meta.json" && tar -xOf "$f" "$n/last_trainable.pt" > "$W/nets/$n/last_trainable.pt" || abort "net extract $t"
done < "$B/bin/nets_pins.txt"
log "packs and $(ls "$W/nets" | wc -l) networks ok"
$PY -c "import sys, torch, timm, numpy, PIL; print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.backends.cudnn.version(), timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda'); print('defaults before rescore_tf32.py: cudnn.benchmark', torch.backends.cudnn.benchmark, 'cudnn.deterministic', torch.backends.cudnn.deterministic, 'matmul.allow_tf32', torch.backends.cuda.matmul.allow_tf32, 'cudnn.allow_tf32', torch.backends.cudnn.allow_tf32, 'sdp flash', torch.backends.cuda.flash_sdp_enabled(), 'mem_efficient', torch.backends.cuda.mem_efficient_sdp_enabled(), 'math', torch.backends.cuda.math_sdp_enabled()); print('rescore_tf32.py sets matmul.allow_tf32=True and cudnn.allow_tf32=True before rescore.py')" > "$O/env.txt" 2>&1
echo "skip_gpu=${C2PR_SKIP_GPU:-0}" >> "$O/env.txt"
export SMAD_DATA=$W/pn1/data HF_HOME=$W/pn1/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
for n in $(ls "$W/nets"); do
  for fam in af0 ffhq ms1ffhq; do
    $PY "$B/bin/rescore_tf32.py" "$B/bin/rescore.py" --resdir "$W/nets/$n" --code "$W/pn1/code" --manifest ms1_eval.csv \
      --fam "$fam" --out "$O/C2P_${n}_${fam}.npz" --workers 7 >> "$B/logs/rescore.log" 2>&1 || abort "rescore $n $fam"
  done
  log "$n scored"
done
log "done"
finish 0

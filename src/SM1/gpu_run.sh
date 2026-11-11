#!/bin/bash
# SM1 frozen-feature pass on one x86 CUDA machine (amendment A7). Inputs: a folder IN with sm1gpu_code.tar and the
# image tars sm1gpu_img_<set>.tar (each with its .sha256). Work folder W (node-local disk). Output: one tar
# OUT/sm1gpu_feats.tar (+ .sha256) holding feats/*.npz, env.json, the log.
#   IN=/path/to/tars W=/local/scratch/sm1 OUT=/path/to/results PY=/path/to/python bash gpu_run.sh [lists]
# Environment expected (AD4's): torch 2.2.1 cu121, timm 1.0.27, pillow 10.2.0, numpy 1.26.4. Resumable: rerunning
# skips finished shards if W is kept.
set -euo pipefail
: "${IN:?}" "${W:?}" "${OUT:?}" "${PY:?}"
LISTS=${1:-}
mkdir -p "$W/pack/images" "$W/feats" "$OUT"
cd "$W"
for t in "$IN"/sm1gpu_code.tar "$IN"/sm1gpu_img_*.tar; do
  n=$(basename "$t")
  if [ ! -f "$W/.done_$n" ]; then
    (cd "$IN" && sha256sum -c "$n.sha256") || { echo "sha256 mismatch $n" >&2; exit 2; }
    case "$n" in
      sm1gpu_code.tar) tar -C "$W/pack" -xf "$t" ;;
      *) tar -C "$W/pack/images" -xf "$t" ;;
    esac
    touch "$W/.done_$n"
  fi
done
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
"$PY" -c "import torch, timm, numpy, PIL, sys; print(sys.version.split()[0], torch.__version__, timm.__version__, numpy.__version__, PIL.__version__, torch.cuda.is_available())"
"$PY" "$W/pack/code/feats_gpu.py" --pack "$W/pack" --out "$W/feats" ${LISTS:+--lists "$LISTS"} --workers "${WORKERS:-8}" --bs "${BS:-128}" 2>&1 | tee -a "$W/feats/run.log"
tar -C "$W" -cf "$W/sm1gpu_feats.tar" feats
sha256sum "$W/sm1gpu_feats.tar" | awk '{print $1"  sm1gpu_feats.tar"}' > "$W/sm1gpu_feats.tar.sha256"
cp "$W/sm1gpu_feats.tar" "$OUT/sm1gpu_feats.tar.part" && mv "$OUT/sm1gpu_feats.tar.part" "$OUT/sm1gpu_feats.tar"
cp "$W/sm1gpu_feats.tar.sha256" "$OUT/"
echo "SM1_GPU_FEATS_DONE $OUT/sm1gpu_feats.tar"

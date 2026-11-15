#!/bin/bash -l
#SBATCH -J smadnext-NE1
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-now
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/NE1-%j.out
# NE1 (experiments/NE1_nuisance-erasure/prereg.md section 8): feature extraction for the five frozen Sb networks
# (seeds 403-407) on development rows only. Pack ne1_pack.tar (code, base weights, images, three manifests) and
# ne1_nets.tar (meta.json + last_trainable.pt per network, TT1-FS pn1fs gate references), both sha256-checked.
# In the torch 2.2.1 / CUDA 12.1 container: ne1_extract.py (rescore.py's build, batch 64, list order, PyTorch defaults),
# then ne1_gate.py (byte identity of H0 logits on the 3,417 G rows against pn1fs). One result tar NE1_feats.tar + sha256.
set -eo pipefail
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
P=$G/packs/NE1; T=$G/tasks/NE1; OUT=$G/results/NE1; mkdir -p "$OUT"
if [ -e "$OUT/NE1_feats.tar" ]; then echo "NE1 already done"; exit 0; fi
W=$MEMFS/work_NE1; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR" "$W"; cd "$W"
SIF=$G/containers/smad_torch221_cu121_v1.sif
R=$W/res/NE1_feats; mkdir -p "$R/feats"
hostname | tee "$R/host.txt"; date -Is
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader | tee "$R/gpu.txt"
(cd "$P" && sha256sum -c ne1_pack.tar.sha256 && sha256sum -c ne1_nets.tar.sha256) | tee "$R/inputs_check.txt"
sha256sum "$SIF" | tee "$R/container.sha256"
(cd "$T" && sha256sum -c --quiet SHA256SUMS)
tar -C "$W" -xf "$P/ne1_pack.tar"; tar -C "$W" -xf "$P/ne1_nets.tar"
(cd "$W/ne1" && sha256sum -c --quiet SHA256SUMS) && (cd "$W/ne1nets" && sha256sum -c --quiet SHA256SUMS)
echo "inputs ok $(date -Is)"
X() { apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" "$SIF" env SMAD_DATA="$W/ne1/data" HF_HOME="$W/ne1/hf" \
      HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 python "$@"; }
X -c "import torch,timm,numpy,PIL,sys;print(sys.version.split()[0],torch.__version__,torch.version.cuda,torch.backends.cudnn.version(),timm.__version__,numpy.__version__,PIL.__version__,torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0),'matmul_tf32',torch.backends.cuda.matmul.allow_tf32,'cudnn_tf32',torch.backends.cudnn.allow_tf32,'benchmark',torch.backends.cudnn.benchmark,'deterministic',torch.backends.cudnn.deterministic)" | tee "$R/versions.txt"
X "$T/ne1_extract.py" --code "$W/ne1/code" --nets "$W/ne1nets/nets" --out "$R/feats" --workers 14 2>&1 | tee "$R/extract.log"
X "$T/ne1_gate.py" --feats "$R/feats" --ref "$W/ne1nets/gate_ref" --nets "$W/ne1nets/nets" --out "$R/gate.json" 2>&1 | tee "$R/gate.txt"
(cd "$R" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
tar -C "$W/res" -cf "$W/NE1_feats.tar" NE1_feats; (cd "$W" && sha256sum NE1_feats.tar) > "$W/NE1_feats.tar.sha256"
cp "$W/NE1_feats.tar" "$OUT/NE1_feats.tar.part" && mv "$OUT/NE1_feats.tar.part" "$OUT/NE1_feats.tar"; cp "$W/NE1_feats.tar.sha256" "$OUT/"
echo "NE1_DONE $(date -Is)"

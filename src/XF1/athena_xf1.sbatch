#!/bin/bash -l
#SBATCH -J smadnext-XF1
#SBATCH -A plgmultivision-gpu-a100
#SBATCH -p plgrid-now
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 16
#SBATCH --mem=120G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/XF1-%j.out
# XF1 (experiments/XF1_ffhq-facemorpher-matched-render/prereg.md, registration hash in the queue file header):
# revision b: development scoring of the 15 FS1 networks (A, B, Sb at seeds 403-407) on the 1,495 rows of xf1b_rows.csv
# (FM(H,B) and the D12b warp-only image W, whole frame and face-only; H whole frame for flag prints only).
# Per network: the unchanged PN1 rescore.py on the 3,417 registered gate rows (fam gate), the byte-identity gate
# xf1_gate.py against the TT1-FS pn1fs reference, and only if it passes rescore.py on the xf1 rows (fam xf1).
# A network whose gate fails is not scored. Container smad_torch221_cu121_v1.sif (torch 2.2.1 / CUDA 12.1).
set -eo pipefail
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
P=$G/packs/XF1; T=$G/tasks/XF1; OUT=$G/results/XF1; mkdir -p "$OUT"
if [ -e "$OUT/XF1_scores.tar" ]; then echo "XF1 already done"; exit 0; fi
W=$MEMFS/work_XF1; export TMPDIR=$MEMFS/tmp; mkdir -p "$TMPDIR" "$W"; cd "$W"
SIF=$G/containers/smad_torch221_cu121_v1.sif
R=$W/res/XF1_scores; mkdir -p "$R/scores"
hostname | tee "$R/host.txt"; date -Is
nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader | tee "$R/gpu.txt"
(cd "$P" && sha256sum -c xf1b_pack.tar.sha256 && sha256sum -c xf1b_nets.tar.sha256) | tee "$R/inputs_check.txt"
sha256sum "$SIF" | tee "$R/container.sha256"
(cd "$T" && sha256sum -c --quiet SHA256SUMS)
tar -C "$W" -xf "$P/xf1b_pack.tar"; tar -C "$W" -xf "$P/xf1b_nets.tar"
(cd "$W/xf1" && sha256sum -c --quiet SHA256SUMS) && (cd "$W/xf1nets" && sha256sum -c --quiet SHA256SUMS)
echo "inputs ok $(date -Is)"
X() { apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" "$SIF" env SMAD_DATA="$W/xf1/data" HF_HOME="$W/xf1/hf" \
      HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 python "$@"; }
X -c "import torch,timm,numpy,PIL,sys;print(sys.version.split()[0],torch.__version__,torch.version.cuda,torch.backends.cudnn.version(),timm.__version__,numpy.__version__,PIL.__version__,torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0),'matmul_tf32',torch.backends.cuda.matmul.allow_tf32,'cudnn_tf32',torch.backends.cudnn.allow_tf32,'benchmark',torch.backends.cudnn.benchmark,'deterministic',torch.backends.cudnn.deterministic)" | tee "$R/versions.txt"
for N in $(ls "$W/xf1nets/nets" | sort); do
  X "$T/rescore.py" --resdir "$W/xf1nets/nets/$N" --code "$W/xf1/code" --manifest xf1b_eval.csv --fam gate --out "$R/scores/${N}__gate.npz" --workers 14 2>&1 | tee -a "$R/score.log"
  if X "$T/xf1_gate.py" --scores "$R/scores/${N}__gate.npz" --ref "$W/xf1nets/gate_ref/$N.npz" --out "$R/scores/${N}__gate.json" 2>&1 | tee -a "$R/gate.txt"; then
    X "$T/rescore.py" --resdir "$W/xf1nets/nets/$N" --code "$W/xf1/code" --manifest xf1b_eval.csv --fam xf1 --out "$R/scores/${N}__xf1.npz" --workers 14 2>&1 | tee -a "$R/score.log"
  else
    echo "GATE_FAILED $N: not scored" | tee -a "$R/gate.txt"
  fi
done
(cd "$R" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
tar -C "$W/res" -cf "$W/XF1_scores.tar" XF1_scores; (cd "$W" && sha256sum XF1_scores.tar) > "$W/XF1_scores.tar.sha256"
cp "$W/XF1_scores.tar" "$OUT/XF1_scores.tar.part" && mv "$OUT/XF1_scores.tar.part" "$OUT/XF1_scores.tar"; cp "$W/XF1_scores.tar.sha256" "$OUT/"
echo "XF1_DONE $(date -Is)"

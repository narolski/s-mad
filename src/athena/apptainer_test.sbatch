#!/bin/bash -l
#SBATCH -J smadnext-apptainer
#SBATCH -A plgrestorearc-gpu-a100
#SBATCH -p plgrid-gpu-a100
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH -C memfs
#SBATCH -o /net/pr2/projects/plgrid/plggrestoration/smad-next/logs/apptainer-test-%j.out
# Test (author's question, 11 Nov): can jobs on Athena run from a container image instead of a per-cluster Python
# environment? Docker itself is not installed; Apptainer 1.4.5 exists on compute nodes and runs Docker images.
# Tries, in order: (1) an unprivileged build of our own image from a definition file (public PyTorch image plus the
# pinned packages of this project); (2) the same with --fakeroot; (3) pulling the public base image only.
# Then runs the image with the GPU and with the project folder bound, and keeps the image if it works.
set -u
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
: "${MEMFS:?RAM disk required (-C memfs)}"
export APPTAINER_CACHEDIR=$MEMFS/cache APPTAINER_TMPDIR=$MEMFS/tmp
mkdir -p "$APPTAINER_CACHEDIR" "$APPTAINER_TMPDIR" "$G/containers"
hostname; apptainer --version; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
cat > "$MEMFS/smad.def" <<'EOF'
Bootstrap: docker
From: pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

%post
    pip install --no-cache-dir timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0

%labels
    project smad-next
    base pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime
EOF
IMG=""
t0=$SECONDS
if apptainer build "$MEMFS/smad.sif" "$MEMFS/smad.def" > "$MEMFS/build1.log" 2>&1; then
  echo "BUILD_UNPRIVILEGED_OK $((SECONDS - t0)) s"; IMG=$MEMFS/smad.sif
else
  echo "BUILD_UNPRIVILEGED_FAILED"; tail -n 6 "$MEMFS/build1.log" | cut -c1-300
  t0=$SECONDS
  if apptainer build --fakeroot "$MEMFS/smad.sif" "$MEMFS/smad.def" > "$MEMFS/build2.log" 2>&1; then
    echo "BUILD_FAKEROOT_OK $((SECONDS - t0)) s"; IMG=$MEMFS/smad.sif
  else
    echo "BUILD_FAKEROOT_FAILED"; tail -n 6 "$MEMFS/build2.log" | cut -c1-300
    t0=$SECONDS
    if apptainer pull "$MEMFS/base.sif" docker://pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime > "$MEMFS/pull.log" 2>&1; then
      echo "PULL_BASE_OK $((SECONDS - t0)) s"; IMG=$MEMFS/base.sif
    else
      echo "PULL_BASE_FAILED"; tail -n 6 "$MEMFS/pull.log" | cut -c1-300
    fi
  fi
fi
[ -n "$IMG" ] || { echo "APPTAINER_TEST_RC=1"; exit 1; }
ls -la "$IMG"
apptainer exec --nv -B "$G:$G" -B "$MEMFS:$MEMFS" "$IMG" python -c "
import sys, torch, numpy, PIL
print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'available', torch.cuda.is_available(), 'gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, 'numpy', numpy.__version__, 'pillow', PIL.__version__)
try:
    import timm, safetensors; print('timm', timm.__version__, 'safetensors', safetensors.__version__)
except Exception as e: print('extra packages missing:', e)
x = torch.randn(4096, 4096, device='cuda'); print('gpu matmul ok', float((x @ x).mean()) == float((x @ x).mean()))
import os; print('project folder visible:', os.path.isdir('$G/packs'), 'ram disk writable:', os.access('$MEMFS', os.W_OK))
"
rc=$?
if [ $rc -eq 0 ] && [ "$IMG" = "$MEMFS/smad.sif" ]; then
  cp "$IMG" "$G/containers/smad_torch221_cu121_v1.sif" && (cd "$G/containers" && sha256sum smad_torch221_cu121_v1.sif > smad_torch221_cu121_v1.sif.sha256 && cat smad_torch221_cu121_v1.sif.sha256) && cp "$MEMFS/smad.def" "$G/containers/smad_torch221_cu121_v1.def"
fi
echo "APPTAINER_TEST_RC=$rc"
exit $rc

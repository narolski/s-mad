#!/bin/bash
# Diffusion-autoencoder generation (DG1), amendment 3: runs ON the rented Docker machine (root, one GPU), driven by
# drive.sh from the DGX. Layout: /root/dg1/{packs,work,results,venv}.
#   remote_run.sh setup        build the pinned environment (as src/DG1/dg1_env.sh) and unpack both packs
#   remote_run.sh eq           the 8 equivalence images (eq.csv) through dg1_gen.py -> results/DG1_eq_rented.tar
#   remote_run.sh shard K      add-on shard K through dg1_addon.py -> results/DG1_addon_sK.tar and _codes.tar
# Every tar gets a .sha256. A generator failure still writes the tar (exit code kept).
set -uo pipefail
R=${DG1_ROOT:-/root/dg1}
PY=$R/venv/bin/python
K=$R/work/dg1pack
A=$R/work/dg1addon
export TMPDIR=$R/tmp TORCH_HOME=$R/torch XDG_CACHE_HOME=$R/cache
mkdir -p "$TMPDIR" "$R/results" "$R/work"
CHECK='import sys, torch, torchvision, numpy, PIL, pytorch_lightning, torchmetrics, scipy, pandas, lmdb, lpips, pytorch_fid; print("python", sys.version.split()[0], "torch", torch.__version__, "cuda", torch.version.cuda, "torchvision", torchvision.__version__, "numpy", numpy.__version__, "pillow", PIL.__version__, "pytorch_lightning", pytorch_lightning.__version__, "gpu", torch.cuda.get_device_name(0)); assert torch.cuda.is_available(); assert numpy.__version__ == "1.26.4" and PIL.__version__ == "12.2.0" and torch.__version__.startswith("2.12.1") and torchvision.__version__.startswith("0.27.1"), "core versions differ"; import numpy.lib.function_base'
PINS="numpy==1.26.4 pillow==12.2.0 pytorch-lightning==2.5.5 torchmetrics==1.8.2 lightning-utilities==0.15.2 lmdb==1.7.3 pandas==2.2.3 python-dateutil==2.9.0.post0 pytz==2025.2 tzdata==2025.2 pytorch-fid==0.3.0 scipy==1.17.1 lpips==0.1.4 tqdm==4.68.3 PyYAML==6.0.3"

info() { hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; df -h /root | tail -1; }

case "${1:-}" in
setup)
  set -e
  info
  ( cd "$R/packs" && sha256sum -c dg1_pack.tar.sha256 dg1_addon_pack.tar.sha256 )
  rm -rf "$R/work"; mkdir -p "$R/work"
  # root keeps the tar's owner (uid 1000) by default, and git then refuses the repo as "dubious ownership" (HEAD '';
  # the first rented run, 11 Nov 22:57): extract as root-owned and also mark exactly this repo as safe
  tar --no-same-owner -C "$R/work" -xf "$R/packs/dg1_pack.tar"; tar --no-same-owner -C "$R/work" -xf "$R/packs/dg1_addon_pack.tar"
  # the pack manifest is checked BEFORE any git command: `git status` refreshes .git/index, which is in the manifest
  # (second rented run, 11 Nov 23:20: "./repo/.git/index: FAILED")
  ( cd "$K" && sha256sum -c --quiet MANIFEST.sha256 ); ( cd "$A" && sha256sum -c --quiet MANIFEST.sha256 )
  echo "packs ok"
  git config --global --add safe.directory "$K/repo" 2>/dev/null || true
  if command -v git >/dev/null; then [ "$(git -C "$K/repo" rev-parse HEAD)" = 00c57d3f626f28bf9ed8aff58d90baab25de3af4 ] && [ -z "$(git -C "$K/repo" status --porcelain)" ] || { echo "repo check failed after unpack"; exit 6; }; echo "repo ok (git)"; fi
  ( cd "$K/repo" && sha256sum -c --quiet ../repo_manifest.sha256 ) && echo "repo ok (file manifest)"
  python3 -m pip install -q uv
  UV="python3 -m uv"
  if [ "${DG1_REHEARSE:-0}" = 1 ]; then   # DGX rehearsal: resolve the exact x86_64 wheel set for driver class DG1_DRV
    $UV python install 3.12.3
    for CU in cu130 cu128; do
      $UV pip compile --python-version 3.12.3 --python-platform x86_64-manylinux_2_28 --no-header --index-url "https://download.pytorch.org/whl/$CU" <(printf 'torch==2.12.1\ntorchvision==0.27.1\n') > "$R/rehearse_torch_$CU.txt" && echo "torch $CU resolves: $(grep -E '^torch==|^torchvision==' "$R/rehearse_torch_$CU.txt" | tr '\n' ' ')"
    done
    printf 'torch==2.12.1+cu130\ntorchvision==0.27.1+cu130\nnumpy==1.26.4\npillow==12.2.0\n' > "$R/constraints.txt"
    $UV pip compile --python-version 3.12.3 --python-platform x86_64-manylinux_2_28 --no-header -c "$R/constraints.txt" \
      --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match <(printf '%s\n' $PINS torch==2.12.1+cu130 torchvision==0.27.1+cu130) > "$R/rehearse_all.txt"
    grep -E '^(numpy|pillow|torch|torchvision|scipy|pandas|pytorch-lightning)==' "$R/rehearse_all.txt"
    echo REHEARSAL_OK; exit 0
  fi
  $UV python install 3.12.3
  rm -rf "$R/venv"; $UV venv --python 3.12.3 "$R/venv"
  DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1); DMAJ=${DRV%%.*}
  CUS="cu128 cu126"; [ "$DMAJ" -ge 580 ] && CUS="cu130 cu128 cu126"
  TOK=""
  for CU in $CUS; do
    if $UV pip install --python "$PY" -q torch==2.12.1 torchvision==0.27.1 --index-url "https://download.pytorch.org/whl/$CU"; then TOK=$CU; break; fi
    echo "torch 2.12.1 with $CU did not install"
  done
  [ -n "$TOK" ] || { echo "no torch 2.12.1 build installed"; exit 3; }
  TV=$("$PY" -I -c 'import torch, torchvision; print(torch.__version__, torchvision.__version__)')
  printf 'torch==%s\ntorchvision==%s\nnumpy==1.26.4\npillow==12.2.0\n' ${TV} > "$R/constraints.txt"
  $UV pip install --python "$PY" -q -c "$R/constraints.txt" --extra-index-url "https://download.pytorch.org/whl/$TOK" --index-strategy unsafe-best-match $PINS
  {
    echo "built $(date -Is) on $(hostname) driver $DRV torch index $TOK uv $($UV --version)"
    "$PY" -I -c "$CHECK"
    $UV pip freeze --python "$PY"
  } > "$R/versions.txt"
  head -2 "$R/versions.txt"
  echo SETUP_OK
  ;;
eq|shard)
  if [ "$1" = eq ]; then TAG=eq_rented; L=eq; GEN=$K/code/dg1_gen.py; JOBS=$K/jobs/eq.csv
  else TAG=addon_s$2; L=addon_s$2; GEN=$A/code/dg1_addon.py; JOBS=$A/jobs/$L.csv; fi
  [ ! -e "$R/results/DG1_$TAG.tar" ] || { echo "refused: DG1_$TAG.tar exists"; exit 4; }
  O=$R/out_$TAG; rm -rf "$O"; mkdir -p "$O" "$R/run"
  info > "$O/host.txt"
  ( while :; do nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits >> "$O/gpumem.csv"; sleep 10; done ) & SM=$!
  t0=$(date +%s)
  ( cd "$R/run" && "$PY" -I "$GEN" --repo "$K/repo" --repo-manifest "$K/repo_manifest.sha256" --ckpt "$K/ckpt/last.ckpt" \
      --inputs "$K/inputs/a256" --jobs "$JOBS" --out-root "$O/$L" --bs 16 ) > "$O/$L.log" 2>&1
  RC=$?
  kill $SM 2>/dev/null
  tail -n 25 "$O/$L.log"
  cp "$R/versions.txt" "$O/versions.txt"; echo "rented rc=$RC $(( $(date +%s) - t0 )) s" > "$O/platform.txt"
  if [ "$1" = shard ]; then
    C=$R/codes_$TAG; rm -rf "$C"; mkdir -p "$C/$L"
    for f in codes.npz fresh.npz; do [ -f "$O/$L/$f" ] && mv "$O/$L/$f" "$C/$L/"; done
    ( cd "$C/$L" && sha256sum ./*.npz > "$O/$L/codes_sha256.txt" 2>/dev/null )
    tar -C "$R" -cf "$R/results/DG1_${TAG}_codes.tar" "codes_$TAG"
    ( cd "$R/results" && sha256sum "DG1_${TAG}_codes.tar" > "DG1_${TAG}_codes.tar.sha256" )
  fi
  tar -C "$R" -cf "$R/results/DG1_$TAG.tar" "out_$TAG"
  ( cd "$R/results" && sha256sum "DG1_$TAG.tar" > "DG1_$TAG.tar.sha256" )
  echo "TASK_END $TAG rc=$RC $(( $(date +%s) - t0 )) s"
  exit $RC
  ;;
*) echo "usage: remote_run.sh setup | eq | shard K"; exit 2 ;;
esac

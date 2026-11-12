#!/bin/bash
# MS1 rented fallback (deviation MS1-D1), runs ON the rented A100 PCIe 40 GB host. Adapted from src/PN1/rented/remote_fs.sh.
#   bash remote_ms1.sh setup PACKPIN HPIN   check both packs, disk >= 50 GB, pip pins (as FS1), versions -> logs
#   bash remote_ms1.sh queue PACKPIN HPIN "T1 T2 ..." Q   fits one after another through run.sh (MS1), one result tar per
#        task in root/results/MS1 (a failed task is re-run once unless the log shows a non-finite loss; rc per task);
#        then the held-out step: every finished fit of this queue rescored on CFD and KDEF with the unchanged rescore.py
#        (MS1H_<arm>_s<seed>_<fam>.npz, one tar root/results/MS1H/MS1H_<Q>.tar + .sha256); ALL_DONE_<Q> at the end.
set -u
B=${MS1_B:-/workspace/ms1}; MODE=${1:?mode}; PIN=${2:?pack pin}; HPIN=${3:?heldout pin}
cd "$B/root/packs/MS1" || exit 1
[ "$(cut -c1-64 pn1_pack_ms1.tar.sha256)" = "$PIN" ] || { echo "pack .sha256 differs from the pin"; exit 1; }
[ "$(cut -c1-64 ms1_heldout_pack.tar.sha256)" = "$HPIN" ] || { echo "held-out pack .sha256 differs from the pin"; exit 1; }
case "$MODE" in
  setup)
    avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' ')
    [ "$avail" -ge "${MS1_MIN_FREE_GB:-50}" ] || { echo "workspace has ${avail} GB free (< ${MS1_MIN_FREE_GB:-50} GB)"; exit 1; }
    sha256sum -c pn1_pack_ms1.tar.sha256 ms1_heldout_pack.tar.sha256 || exit 1
    python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
    python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
      numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || { tail -20 "$B/logs/pip.log"; exit 1; }
    python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1"
    python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)" | tee "$B/logs/versions.txt"
    nvidia-smi --query-gpu=uuid,name,memory.total,driver_version --format=csv | tee "$B/logs/gpus.txt"
    df -h /workspace | tail -1 | tee "$B/logs/disk.txt"
    echo SETUP_OK
    ;;
  queue)
    TASKS=${4:?tasks}; Q=${5:?queue id}
    exec 9> "$B/ms1_queue.lock"; flock 9
    date > "$B/QUEUE_STARTED_$Q"
    for T in $TASKS; do
      for try in 1 2; do
        W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
        ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$B/root/packs/MS1/pn1_pack_ms1.tar" \
          MS1_RESULTS="$B/root/results/MS1" PN1_LOCAL=1 PN1_PY=python PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
        rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$W"
        echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_$Q.log"
        [ $rc -eq 0 ] && break
        grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_$Q.log"; break; }
      done
    done
    # held-out step (CFD, KDEF) on this queue's finished fits
    H=$B/held; rm -rf "$H"; mkdir -p "$H/out" "$B/root/results/MS1H"
    tar -C "$H" -xf "$B/root/packs/MS1/ms1_heldout_pack.tar" && (cd "$H/pn1" && sha256sum -c --quiet SHA256SUMS) || { echo "held-out pack bad" >> "$B/queue_$Q.log"; date > "$B/ALL_DONE_$Q"; exit 1; }
    D=$H/data; mkdir -p "$D"; ln -s "$H/pn1/data/eval" "$D/eval"; ln -s "$H/pn1/data/manifests" "$D/manifests"
    python -c "import sys, torch, timm; print('env', sys.version.split()[0], torch.__version__, timm.__version__)" > "$H/out/env.txt"
    nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$H/out/gpu.txt" 2>&1 || true
    for T in $TASKS; do
      [ -f "$B/root/results/MS1/$T.tar" ] || continue
      tar -C "$H" -xf "$B/root/results/MS1/$T.tar" "$T/meta.json" "$T/last_trainable.pt"
      ARM=${T#MS1_}; ARM=${ARM%_s*}; SEED=${T##*_s}
      for FAM in cfd kdef tt1ref; do
        SMAD_DATA=$D HF_HOME=$H/pn1/hf HF_HUB_OFFLINE=1 python "$H/pn1/src/rescore.py" --resdir "$H/$T" --code "$H/pn1/code" \
          --manifest ms1_heldout.csv --fam "$FAM" --out "$H/out/MS1H_${ARM}_s${SEED}_${FAM}.npz" --workers 7 >> "$B/logs/heldout_$Q.log" 2>&1 \
          || echo "$(date +%T) heldout $T $FAM failed" >> "$B/queue_$Q.log"
      done
      rm -rf "$H/$T"
    done
    tar -C "$H" -cf "$B/root/results/MS1H/MS1H_$Q.tar" out && (cd "$B/root/results/MS1H" && sha256sum "MS1H_$Q.tar" > "MS1H_$Q.tar.sha256")
    echo "$(date +%T) heldout tar written" >> "$B/queue_$Q.log"
    date > "$B/ALL_DONE_$Q"
    ;;
esac

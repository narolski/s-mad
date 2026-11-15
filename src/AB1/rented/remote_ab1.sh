#!/bin/bash
# AB1 rented fallback (only if the lead moves SE1 and AB1 off WCSS; AB1 follows SE1's platform), runs ON the rented host.
# Adapted from src/MS1/rented/remote_ms1.sh: two pack files (FS1 pack + AB1 overlay), no held-out step (the hold-out
# rows are inside ab1_eval.csv), results in root/results/AB1.
#   bash remote_ab1.sh setup PACKPIN OVPIN   check both files, disk >= 50 GB, pip pins (as FS1/MS1), versions -> logs
#   bash remote_ab1.sh queue PACKPIN OVPIN "T1 T2 ..." Q   fits one after another through src/AB1/run.sh, one result tar
#        per task (a failed task is re-run once unless the log shows a non-finite loss; rc per task); ALL_DONE_<Q> at the end.
set -u
B=${AB1_B:-/workspace/ab1}; MODE=${1:?mode}; PIN=${2:?pack pin}; OVPIN=${3:?overlay pin}
[ "$(cut -c1-64 $B/root/packs/BB2/pn1_pack_fs.tar.sha256)" = "$PIN" ] || { echo "pack .sha256 differs from the pin"; exit 1; }
[ "$(cut -c1-64 $B/root/packs/AB1/ab1_overlay.tar.sha256)" = "$OVPIN" ] || { echo "overlay .sha256 differs from the pin"; exit 1; }
case "$MODE" in
  setup)
    avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' ')
    [ "$avail" -ge "${AB1_MIN_FREE_GB:-50}" ] || { echo "workspace has ${avail} GB free (< ${AB1_MIN_FREE_GB:-50} GB)"; exit 1; }
    (cd $B/root/packs/BB2 && sha256sum -c pn1_pack_fs.tar.sha256) && (cd $B/root/packs/AB1 && sha256sum -c ab1_overlay.tar.sha256) || exit 1
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
    exec 9> "$B/ab1_queue.lock"; flock 9
    date > "$B/QUEUE_STARTED_$Q"
    for T in $TASKS; do
      for try in 1 2; do
        W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
        ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$B/root/packs/BB2/pn1_pack_fs.tar" \
          AB1_OVERLAY="$B/root/packs/AB1/ab1_overlay.tar" AB1_RESULTS="$B/root/results/AB1" PN1_PY=python PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
        rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$W"
        echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_$Q.log"
        [ $rc -eq 0 ] && break
        grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_$Q.log"; break; }
      done
    done
    date > "$B/ALL_DONE_$Q"
    ;;
esac

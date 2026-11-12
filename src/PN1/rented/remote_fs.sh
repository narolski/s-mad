#!/bin/bash
# PN1 fresh seeds (registration FS1), rented machine. Modes:
#   bash remote_fs.sh setup PIN2      check the development pack against its pin, pip pins (as remote_setup.sh), versions -> logs
#   bash remote_fs.sh queue PIN2 "T1 T2 ..." Q [after_a14]   Q = queue id m1 | m2 (markers QUEUE_FS_STARTED_Q,
#        ALL_DONE_FS_Q, queue_fs_Q.log); the GPU is chosen by the caller's CUDA_VISIBLE_DEVICES (one-host layout:
#        m1 on GPU 0, m2 on GPU 1); after_a14: wait for A14_DONE first   run the tasks one after another with the development pack through run.sh (v3), one
#        result tar per task in root/results/PN1; a failed task is re-run once unless the log shows a non-finite loss;
#        rc per task in rc/; ALL_DONE_FS at the end. The pack holds no benchmark image: run.sh scores the development pn1_eval.csv only.
set -u
B=/workspace/pn1; MODE=${1:?mode}; PIN2=${2:?pin}
cd "$B/root/packs/PN1" || exit 1
[ "$(cut -c1-64 pn1_pack_fs.tar.sha256)" = "$PIN2" ] || { echo "pack .sha256 differs from the pin"; exit 1; }
case "$MODE" in
  setup)
    sha256sum -c pn1_pack_fs.tar.sha256 || exit 1
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
    TASKS=${3:?tasks}; Q=${4:?queue id}
    date > "$B/QUEUE_FS_STARTED_$Q"
    echo "$(date +%T) queue $Q CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}" >> "$B/queue_fs_$Q.log"
    [ "${5:-}" = after_a14 ] && { until [ -f "$B/A14_DONE" ]; do sleep 30; done; echo "$(date +%T) A14_DONE seen" >> "$B/queue_fs_$Q.log"; }
    for T in $TASKS; do
      for try in 1 2; do
        W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
        ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$B/root/packs/PN1/pn1_pack_fs.tar" \
          PN1_LOCAL=1 PN1_PY=python PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
        rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$W"
        echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_fs_$Q.log"
        [ $rc -eq 0 ] && break
        grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_fs_$Q.log"; break; }
      done
    done
    date > "$B/ALL_DONE_FS_$Q"
    ;;
esac

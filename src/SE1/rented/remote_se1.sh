#!/bin/bash
# SE1 rented fallback (only if the lead moves the fits off WCSS/Athena): runs ON the rented host. Adapted from
# src/MS1/rented/remote_ms1.sh. One lease = one queue = one or more whole seeds (arms A, Sb, SE of each seed).
#   bash remote_se1.sh setup PACKPIN OVPIN          check packs, disk >= 45 GB, pip pins (as FS1/MS1), versions -> logs
#   bash remote_se1.sh queue PACKPIN OVPIN "T1 ..." Q   fits one after another through src/SE1/run.sh, one result tar per
#        task in root/results/SE1 (an infrastructure failure re-run once unless the log shows a non-finite loss); then the
#        platform reproduction check (FS1 Sb s403 rescored on the gate rows, prereg section 9); ALL_DONE_<Q> at the end.
set -u
B=${SE1_B:-/workspace/se1}; MODE=${1:?mode}; PIN=${2:?pack pin}; OVPIN=${3:?overlay pin}
cd "$B/root/packs/SE1" || exit 1
[ "$(cut -c1-64 pn1_pack_fs.tar.sha256)" = "$PIN" ] || { echo "pack .sha256 differs from the pin"; exit 1; }
[ "$(cut -c1-64 se1_overlay.tar.sha256)" = "$OVPIN" ] || { echo "overlay .sha256 differs from the pin"; exit 1; }
case "$MODE" in
  setup)
    avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' ')
    [ "$avail" -ge 45 ] || { echo "workspace has ${avail} GB free (< 45 GB)"; exit 1; }
    sha256sum -c pn1_pack_fs.tar.sha256 se1_overlay.tar.sha256 run.sh.sha256 rescore.py.sha256 PN1_Sb_s403.tar.sha256 || exit 1
    python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
    python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
      numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || { tail -20 "$B/logs/pip.log"; exit 1; }
    python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0' and torch.cuda.device_count() >= 1"
    python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)" | tee "$B/logs/versions.txt"
    nvidia-smi --query-gpu=uuid,name,memory.total,driver_version --format=csv | tee "$B/logs/gpus.txt"
    echo SETUP_OK
    ;;
  queue)
    TASKS=${4:?tasks}; Q=${5:?queue id}
    exec 9> "$B/se1_queue.lock"; flock 9
    date > "$B/QUEUE_STARTED_$Q"
    for T in $TASKS; do
      for try in 1 2; do
        W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
        ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$B/root/packs/SE1/pn1_pack_fs.tar" \
          SE1_OVERLAY="$B/root/packs/SE1/se1_overlay.tar" SE1_OVERLAY_SHA="$OVPIN" SE1_RESULTS="$B/root/results/SE1" \
          PN1_PY=python PN1_WORKERS=7 bash "$B/root/packs/SE1/run.sh" ) >> "$B/logs/$T.log" 2>&1
        rc=$?; echo "$rc" > "$B/rc/$T"
        echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_$Q.log"
        [ $rc -eq 0 ] && { rm -rf "$W"; break; }
        grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_$Q.log"; rm -rf "$W"; break; }
        rm -rf "$W"
      done
    done
    # platform reproduction check (needs one unpacked pack tree): FS1 Sb s403 on the gate rows
    H=$B/pc; rm -rf "$H"; mkdir -p "$H/out" "$B/root/results/SE1"
    tar -C "$H" -xf "$B/root/packs/SE1/pn1_pack_fs.tar" && tar -C "$H" -xf "$B/root/packs/SE1/PN1_Sb_s403.tar" PN1_Sb_s403/meta.json PN1_Sb_s403/last_trainable.pt
    D=$H/data; mkdir -p "$D"; ln -s "$H/pn1/data/eval" "$D/eval"; ln -s "$H/pn1/data/manifests" "$D/manifests"
    for FAM in af0 ffhq; do
      SMAD_DATA=$D HF_HOME=$H/pn1/hf HF_HUB_OFFLINE=1 python "$B/root/packs/SE1/rescore.py" --resdir "$H/PN1_Sb_s403" --code "$H/pn1/code" \
        --manifest pn1_eval.csv --fam "$FAM" --out "$H/out/PC_PN1_Sb_s403_$FAM.npz" --workers 7 >> "$B/logs/pc_$Q.log" 2>&1 || echo "$(date +%T) pc $FAM failed" >> "$B/queue_$Q.log"
    done
    nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$H/out/gpu.txt" 2>&1 || true
    tar -C "$H" -cf "$B/root/results/SE1/SE1_platformcheck_$Q.tar" out && (cd "$B/root/results/SE1" && sha256sum "SE1_platformcheck_$Q.tar" > "SE1_platformcheck_$Q.tar.sha256")
    rm -rf "$H"
    date > "$B/ALL_DONE_$Q"
    ;;
esac

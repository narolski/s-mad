#!/bin/bash
# BB2 rented variant (prepared 13 Nov for the author's 09:00 decision; needs a committed platform deviation before any
# fit). Runs ON the rented host (Docker image pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime, root, /workspace).
#   bash remote_bb2.sh setup            check pack/overlay/run.sh/featcheck pins, pip pins (FS1's), versions, GPU, disk
#   bash remote_bb2.sh smoke            Sb s403, 100 steps, 64 rows, 256x1 then 128x2, GPU memory peaks, feature check
#   bash remote_bb2.sh queue BS ACCUM "T1 T2 ..."   fits one after another (host lock); BS/ACCUM 256/1 or 128/2 only;
#        a task that fails without a non-finite loss is rerun once (at 128x2 after out-of-memory, else unchanged;
#        registered rule), labelled in rerun/<T>;
#        a non-finite run is never rerun; ALL_DONE at the end.
set -u
B=/workspace/bb2; MODE=${1:?mode}
PIN_PACK=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
PIN_OV=7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad
PIN_RUN=0eaa4dce1df14537990d490bebbe01ad72d0719686cadfce832f3ce2b82f07c3
PIN_FC=430efddcd01b9c4713c42f6b59bc8fb74c3e529912d34063731960b4a43e837f
PIN_REF=89f3defe6a6f74ef1852f19ef6e9a2cc8b3867c8e55be895e9ae299425627b75
P=$B/root/packs/BB2
cd "$P" || exit 1
chk() { [ "$(sha256sum "$1" | cut -c1-64)" = "$2" ] || { echo "PIN FAIL $1"; exit 1; }; }
mkdir -p "$B/logs" "$B/rc" "$B/rerun" "$B/work" "$B/tmp"
run_task() {   # T BS ACCUM STEPS LIMIT RESULTS
  local T=$1 BS=$2 AC=$3 ST=$4 LI=$5 RES=$6 A S W
  A=$(echo "$T" | sed -E 's/^BB2(smoke)?_([A-Za-z]+)_s([0-9]+).*/\2/'); S=$(echo "$T" | sed -E 's/.*_s([0-9]+).*/\1/')
  mkdir -p "$B/tasks/$T"; printf 'TASK=%s\nARM=%s\nSEED=%s\n' "$T" "$A" "$S" > "$B/tasks/$T/task.env"
  W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
  ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$P/pn1_pack_fs.tar" \
    BB2_OVERLAY="$P/bb2_overlay.tar" BB2_RESULTS="$RES" BB2_BS=$BS BB2_ACCUM=$AC PN1_LOCAL=1 PN1_PY=python PN1_WORKERS=7 \
    PN1_STEPS=$ST PN1_LIMIT=$LI bash "$P/run.sh" ) >> "$B/logs/$T.log" 2>&1
}
case "$MODE" in
  setup)
    chk pn1_pack_fs.tar $PIN_PACK; chk bb2_overlay.tar $PIN_OV; chk run.sh $PIN_RUN; chk featcheck.py $PIN_FC; chk featref_cpu.npz $PIN_REF
    avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' ')
    [ "$avail" -ge 45 ] || { echo "workspace has ${avail} GB free (< 45 GB)"; exit 1; }
    python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
    python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
      numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || { tail -20 "$B/logs/pip.log"; exit 1; }
    python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and torch.cuda.device_count() >= 1"
    python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)" | tee "$B/logs/versions.txt"
    nvidia-smi --query-gpu=uuid,name,memory.total,driver_version --format=csv | tee "$B/logs/gpus.txt"
    echo SETUP_OK
    ;;
  smoke)
    for MODE2 in 256x1 128x2; do
      BS=${MODE2%x*}; AC=${MODE2#*x}; T=BB2smoke_Sb_s403_bs$MODE2
      nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -lms 2000 > "$B/logs/gpumem_$MODE2.csv" 2>&1 & MON=$!
      run_task "$T" "$BS" "$AC" 100 64 "$B/root/results/BB2_smoke"; rc=$?
      kill $MON 2>/dev/null; sleep 1
      echo "BB2_SMOKE_MODE $MODE2 rc $rc BB2_PEAK_MIB $(sort -n "$B/logs/gpumem_$MODE2.csv" | tail -1) $(grep -o 'step  *100/100.*it/s' "$B/logs/$T.log" | tail -1)" | tee -a "$B/logs/smoke.txt"
      if [ "$MODE2" = 256x1 ] && [ -d "$B/work/$T/pn1" ]; then
        SMAD_DATA=$B/work/$T/data HF_HOME=$B/work/$T/pn1/hf HF_HUB_OFFLINE=1 python -I "$P/featcheck.py" --root "$B/work/$T/pn1" \
          --out "$B/logs/feat_rented.npz" --ref "$P/featref_cpu.npz" | tee -a "$B/logs/smoke.txt"
        echo "BB2_FEATCHECK_RC ${PIPESTATUS[0]}" | tee -a "$B/logs/smoke.txt"
      fi
      rm -rf "$B/work/$T"
    done
    echo SMOKE_END | tee -a "$B/logs/smoke.txt"
    ;;
  queue)
    BS=${2:?bs}; AC=${3:?accum}; TASKS=${4:?tasks}
    case "$BS/$AC" in 256/1|128/2) ;; *) echo "refuse batch $BS/$AC"; exit 1 ;; esac
    exec 9> "$B/queue.lock"; flock -n 9 || { echo "a queue already runs"; exit 1; }
    date > "$B/QUEUE_STARTED"
    for T in $TASKS; do
      run_task "$T" "$BS" "$AC" 6250 0 "$B/root/results/BB2"; rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$B/work/$T"
      echo "$(date +%T) $T $BS/$AC rc $rc" >> "$B/queue.log"
      if [ $rc -ne 0 ]; then
        if grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log"; then echo "$(date +%T) $T non-finite: not rerun" >> "$B/queue.log"
        else
          if grep -qi "out of memory" "$B/logs/$T.log"; then RB=128; RA=2; else RB=$BS; RA=$AC; fi   # prereg section 4 / 6
          echo "rerun once at ${RB}x${RA} after rc $rc (registered infrastructure rule)" > "$B/rerun/$T"
          mv "$B/logs/$T.log" "$B/logs/$T.try1.log"
          run_task "$T" $RB $RA 6250 0 "$B/root/results/BB2"; rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$B/work/$T"
          echo "$(date +%T) $T rerun $RB/$RA rc $rc" >> "$B/queue.log"
        fi
      fi
    done
    date > "$B/ALL_DONE"
    ;;
  *) echo "mode setup|smoke|queue"; exit 1 ;;
esac

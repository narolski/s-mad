#!/bin/bash
# SE1 rented route (deviation SE1-D1), runs ON a rented host. Writes only under /workspace/se1. Two bases: a fresh lease
# holding the FS1 pack in /workspace/se1/packs (A100 route; the registered run.sh b2a975f1), or a host shared with the MS1
# owner (L40S route; the MS1 pack in place and run_rented.sh). WAITFILE 'none' on a fresh lease.
# Base pack: the MS1 owner's /workspace/ms1/root/packs/MS1/pn1_pack_ms1.tar (c11b16bc...), read in place, never written.
# Every GPU step first waits for the MS1 owner's marker (ms1m1b: /workspace/ms1/C2P_DONE_m1; ms1m2: /workspace/ms1/ALL_DONE_m2;
# agreed 13 Nov) and then takes the MS1 owner's lock /workspace/ms1/ms1_queue.lock (blocking), so it never runs beside MS1 work.
#   bash remote_se1.sh check WAITFILE            pins of every input, disk >= 45 GB, python/torch versions -> logs (no GPU)
#   bash remote_se1.sh smoke WAITFILE            run_rented.sh, arm SE seed 408, 100 steps, 64 rows (never read) + platform
#                                                check: FS1 Sb s403 rescored on the gate rows (fam af0, ffhq) -> results/
#   bash remote_se1.sh queue WAITFILE "T1 ..." Q  fits one after another (an infrastructure failure re-run once unless the
#                                                log shows a non-finite loss), one tar per task in results/; ALL_DONE_<Q>
set -u
B=/workspace/se1; MODE=${1:?mode}; WAITF=${2:?wait file}
K=$B/packs
if [ -f "$K/pn1_pack_fs.tar" ]; then                       # fresh lease (A100 route): the registered FS1 pack and run.sh
  BASE=fs1; BASEPACK=$K/pn1_pack_fs.tar; RUNSH=$K/run.sh; LOCK=$B/se1.lock
else                                                        # shared MS1 host (L40S route): MS1 pack in place, run_rented.sh
  BASE=ms1; BASEPACK=/workspace/ms1/root/packs/MS1/pn1_pack_ms1.tar; RUNSH=$K/run_rented.sh; LOCK=/workspace/ms1/ms1_queue.lock
fi
OVPIN=de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c
pins() {
  if [ $BASE = fs1 ]; then
    (cd "$K" && sha256sum -c --quiet pn1_pack_fs.tar.sha256) && [ "$(cut -c1-64 "$K/pn1_pack_fs.tar.sha256")" = 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 ] || { echo "FS1 pack pin"; return 1; }
    [ "$(sha256sum "$RUNSH" | cut -c1-64)" = b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb ] || { echo "run.sh pin"; return 1; }
  else
    [ "$(cut -c1-64 /workspace/ms1/root/packs/MS1/pn1_pack_ms1.tar.sha256)" = c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d ] || { echo "MS1 pack pin"; return 1; }
    (cd "$K" && sha256sum -c --quiet se1_fs1sup.tar.sha256 run_rented.sh.sha256) || return 1
  fi
  (cd "$K" && sha256sum -c --quiet se1_overlay.tar.sha256 rescore.py.sha256 PN1_Sb_s403.tar.sha256) || return 1
  [ "$(cut -c1-64 "$K/se1_overlay.tar.sha256")" = "$OVPIN" ] || { echo "overlay pin"; return 1; }
}
gpu_wait() {
  [ "$WAITF" = none ] || while [ ! -e "$WAITF" ]; do sleep 60; done
  exec 9> "$LOCK"; flock 9
  echo "$(date +%T) lock taken after $WAITF" >> "$B/queue.log"
}
run_task() {  # T ARM SEED STEPS LIMIT OUT
  local T=$1 W=$B/work/$1
  rm -rf "$W"; mkdir -p "$W" "$B/tasks/$T"
  printf 'TASK=%s\nARM=%s\nSEED=%s\n' "$T" "$2" "$3" > "$B/tasks/$T/task.env"
  ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B" PN1_PACK="$BASEPACK" SE1_SUP="$K/se1_fs1sup.tar" \
    SE1_OVERLAY="$K/se1_overlay.tar" SE1_OVERLAY_SHA="$OVPIN" SE1_RESULTS="$6" PN1_PY=python PN1_WORKERS=7 \
    PN1_STEPS=$4 PN1_LIMIT=$5 bash "$RUNSH" ) >> "$B/logs/$T.log" 2>&1
}
case "$MODE" in
  setup)                                                     # fresh lease only: pip pins as FS1 / MS1 (image pytorch 2.2.1)
    python -c "import torch, torchvision; print('torch==' + torch.__version__.split('+')[0]); print('torchvision==' + torchvision.__version__.split('+')[0])" > "$B/constraints.txt"
    python -m pip install --no-cache-dir -c "$B/constraints.txt" timm==1.0.27 huggingface_hub==0.36.2 safetensors==0.8.0 \
      numpy==1.26.4 pyyaml==6.0.3 pillow==10.2.0 > "$B/logs/pip.log" 2>&1 || { tail -20 "$B/logs/pip.log"; exit 1; }
    echo SE1_SETUP_OK
    ;;
  check)
    echo "base $BASE"; pins || exit 1
    avail=$(df --output=avail -B1G /workspace | tail -1 | tr -d ' '); echo "free ${avail} GB"
    [ "$avail" -ge 45 ] || { echo "less than 45 GB free"; exit 1; }
    python -c "import sys, torch, timm, numpy, PIL; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'timm', timm.__version__, 'numpy', numpy.__version__, 'pillow', PIL.__version__)" | tee "$B/logs/versions.txt"
    python -c "import torch, timm, numpy, PIL; assert torch.__version__.startswith('2.2.1') and timm.__version__ == '1.0.27' and numpy.__version__ == '1.26.4' and PIL.__version__ == '10.2.0'"
    nvidia-smi --query-gpu=uuid,name,memory.total,driver_version --format=csv | tee "$B/logs/gpus.txt"
    echo SE1_CHECK_OK
    ;;
  smoke)
    pins || exit 1
    gpu_wait
    run_task SE1smoke_SE_s408 SE 408 100 64 "$B/results_smoke"; rc=$?
    echo "$(date +%T) smoke rc $rc" >> "$B/queue.log"
    H=$B/work/SE1smoke_SE_s408; P=$B/pc; rm -rf "$P"; mkdir -p "$P/out" "$P/nets"
    tar -C "$P/nets" -xf "$K/PN1_Sb_s403.tar" PN1_Sb_s403/meta.json PN1_Sb_s403/last_trainable.pt
    for FAM in af0 ffhq; do
      SMAD_DATA=$H/data HF_HOME=$H/pn1/hf HF_HUB_OFFLINE=1 python "$K/rescore.py" --resdir "$P/nets/PN1_Sb_s403" --code "$H/pn1/code" \
        --manifest pn1_eval.csv --fam $FAM --out "$P/out/PC_PN1_Sb_s403_$FAM.npz" --workers 7 >> "$B/logs/pc.log" 2>&1 || echo "$(date +%T) pc $FAM failed" >> "$B/queue.log"
    done
    nvidia-smi --query-gpu=uuid,name --format=csv,noheader > "$P/out/gpu.txt"
    mkdir -p "$B/results_smoke"; tar -C "$P" -cf "$B/results_smoke/SE1_platformcheck_$(hostname).tar" out
    (cd "$B/results_smoke" && sha256sum SE1_platformcheck_$(hostname).tar > SE1_platformcheck_$(hostname).tar.sha256)
    rm -rf "$H" "$P"; date > "$B/SMOKE_DONE"; echo "SE1_SMOKE_RC $rc"
    ;;
  queue)
    TASKS=${3:?tasks}; Q=${4:?queue id}
    pins || exit 1
    gpu_wait
    date > "$B/QUEUE_STARTED_$Q"
    for T in $TASKS; do a=${T#SE1_}; a=${a%_s*}; s=${T##*_s}
      for try in 1 2; do
        run_task "$T" "$a" "$s" 6250 0 "$B/results"; rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$B/work/$T"
        echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_$Q.log"
        [ $rc -eq 0 ] && break
        grep -qiE "loss +-?nan|loss +-?inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_$Q.log"; break; }
      done
    done
    date > "$B/ALL_DONE_$Q"
    ;;
esac

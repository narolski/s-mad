#!/bin/bash
# SE1 rented route (deviation SE1-D1), DGX-side driver for one shared L40S host (the MS1 owner's leases ms1m1b / ms1m2, or
# further L40S leases rented by the lead). Never writes in the lease folder (HOLD / RELEASE belong to the lead and the MS1
# owner); own state in /mnt/t7/smad_next/SE1/rented_<NAME>/. SSH key by path only.
#   bash drive_se1.sh HOST PORT NAME WAITFILE push     upload run_rented.sh, remote_se1.sh (the packs are uploaded once by hand)
#   bash drive_se1.sh HOST PORT NAME none packs        fresh A100 lease: upload the FS1 pack (4 parallel streams) and the rest
#   bash drive_se1.sh HOST PORT NAME none setup        fresh lease: pip pins
#   bash drive_se1.sh HOST PORT NAME WAITFILE check    pins, disk, versions (no GPU)
#   bash drive_se1.sh HOST PORT NAME WAITFILE smoke    start the smoke + platform check, detached (waits for WAITFILE + MS1 lock)
#   bash drive_se1.sh HOST PORT NAME WAITFILE queue SEEDS   start the fits of whole seeds (e.g. 408-409), detached; ONLY on the lead's go
#   bash drive_se1.sh HOST PORT NAME WAITFILE pull     fetch result tars, smoke/platform tars and logs; verify; second copy
#   bash drive_se1.sh HOST PORT NAME WAITFILE status
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; NAME=${3:?name}; WAITF=${4:?wait file}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${SE1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
P=/mnt/t7/smad_next/SE1; S=$P/rented_$NAME; OUTD=$P/results; COPY=/home/narolski/se1_results_copy; B=/workspace/se1
KH=${SE1_KH:-/mnt/t7/smad_next/vast/$NAME/known_hosts}; [ -f "$KH" ] || KH=$S/known_hosts
mkdir -p "$S" "$OUTD/logs_$NAME" "$COPY"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$KH" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$S/drive.log"; }
case "$STEP" in
  push)
    (cd "$P" && sha256sum -c --quiet run_rented.sh.sha256) || { log "local run_rented.sh off its sha"; exit 1; }
    RS "$P/run_rented.sh" "$P/run_rented.sh.sha256" "root@$HOST:$B/packs/" && RS "$SRC/remote_se1.sh" "root@$HOST:$B/bin/"
    R "cd $B/packs && sha256sum -c run_rented.sh.sha256" | tee -a "$S/drive.log"
    ;;
  packs)          # fresh lease (A100 route): FS1 pack in 4 parallel chunk streams, reassembled and sha256-checked there;
                  # overlay, run.sh (registered pin), rescore.py, FS1 Sb s403 tar for the platform check
    R "mkdir -p $B/packs $B/bin $B/logs $B/rc $B/tmp $B/results $B/tasks $B/chunks && df -h /workspace | tail -1" | tee -a "$S/drive.log"
    C=$P/chunks; mkdir -p "$C"; [ -f "$C/fs.part.03" ] || split -n 4 -d -a 2 /mnt/t7/smad_next/PN1/pn1_pack_fs.tar "$C/fs.part."
    T0=$SECONDS
    for i in 00 01 02 03; do RS "$C/fs.part.$i" "root@$HOST:$B/chunks/" & done; wait
    R "cat $B/chunks/fs.part.0[0-3] > $B/packs/pn1_pack_fs.tar && rm -rf $B/chunks"
    RS /mnt/t7/smad_next/PN1/pn1_pack_fs.tar.sha256 "$P/se1_overlay.tar" "$P/se1_overlay.tar.sha256" "$P/run.sh" "$P/run.sh.sha256" \
      "$P/rescore.py" "$P/rescore.py.sha256" "$P/PN1_Sb_s403.tar" "$P/PN1_Sb_s403.tar.sha256" "root@$HOST:$B/packs/"
    RS "$SRC/remote_se1.sh" "root@$HOST:$B/bin/"
    R "cd $B/packs && sha256sum -c pn1_pack_fs.tar.sha256 se1_overlay.tar.sha256 run.sh.sha256 rescore.py.sha256 PN1_Sb_s403.tar.sha256" | tee -a "$S/drive.log"
    log "packs uploaded in $((SECONDS - T0)) s"
    ;;
  setup) R "bash $B/bin/remote_se1.sh setup $WAITF" 2>&1 | tee -a "$S/setup.log" ;;
  check) R "bash $B/bin/remote_se1.sh check $WAITF" 2>&1 | tee -a "$S/check.log" ;;
  smoke)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_se1.sh smoke $WAITF > $B/logs/smoke_driver.log 2>&1 < /dev/null & sleep 2; echo SE1_SMOKE_LAUNCHED" || true)
    echo "$msg" | grep -q SE1_SMOKE_LAUNCHED && log "smoke launched (waits for $WAITF and the MS1 lock)" || { log "smoke launch not confirmed"; exit 1; }
    ;;
  queue)
    SEEDS=${6:?seeds}; TASKS=""
    for s in ${SEEDS//-/ }; do case $s in 408|409|410|411|412) ;; *) log "seed $s"; exit 1 ;; esac
      for a in A Sb SE; do TASKS="$TASKS SE1_${a}_s$s"; done; done; TASKS=${TASKS# }
    R "[ -f $B/SMOKE_DONE ] && grep -q 'smoke rc 0' $B/queue.log" || { log "smoke not passed on this host: no queue"; exit 1; }
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_se1.sh queue $WAITF '$TASKS' $SEEDS > $B/logs/queue_driver_$SEEDS.log 2>&1 < /dev/null & sleep 2; echo SE1_QUEUE_LAUNCHED" || true)
    echo "$msg" | grep -q SE1_QUEUE_LAUNCHED && log "queue $SEEDS launched: $TASKS" || { log "queue launch not confirmed"; exit 1; }
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free: not pulling"; exit 1; }
    RS --include='SE1_*.tar' --include='SE1_*.tar.sha256' --exclude='*' "root@$HOST:$B/results/" "$OUTD/" || true
    mkdir -p "$P/smoke_$NAME"; RS "root@$HOST:$B/results_smoke/" "$P/smoke_$NAME/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs_$NAME/" || true
    RS "root@$HOST:$B/queue*.log" "root@$HOST:$B/rc" "$OUTD/logs_$NAME/" 2>/dev/null || true
    n=0; for f in "$OUTD"/SE1_*_s4*.tar; do [ -e "$f" ] || continue
      if (cd "$OUTD" && sha256sum -c --quiet "$(basename "$f").sha256"); then n=$((n + 1))
        cp -n "$f" "$f.sha256" "$COPY/"; (cd "$COPY" && sha256sum -c --quiet "$(basename "$f").sha256") || log "second copy of $(basename "$f") failed"
      else log "$(basename "$f") not verified"; fi; done
    log "verified fit tars in $OUTD: $n (second copies in $COPY)"
    ;;
  status) R "cat $B/queue*.log 2>/dev/null; ls $B/results $B/results_smoke 2>/dev/null; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1" ;;
esac

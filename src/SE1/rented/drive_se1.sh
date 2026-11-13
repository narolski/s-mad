#!/bin/bash
# SE1 rented fallback, DGX-side driver for one lease (adapted from src/MS1/rented/drive_ms1.sh). Used only if the lead
# moves the 15 fits to rented machines; then EVERY lease has the same GPU model (one platform for all 15 fits, their
# scoring and AB1's reads), each seed runs whole on one lease, and nothing runs on WCSS or Athena.
#   bash drive_se1.sh HOST PORT LEASE Q setup|queue|pull|loop|status    Q = a seed list joined by '-', e.g. 408-409
# Pull: tars + platform-check tar + logs, verified; second copies in /home/narolski/se1_results_copy; RELEASE only when
# everything of the queue is fetched and verified (OWNER_BRIEF rented-machine rule: trained weights are kept).
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; Q=${4:?seed list}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${SE1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
P=/mnt/t7/smad_next/SE1
OVPIN=de26d6ce3facc90a439209d690b099fea351ace91808a5256ba5bdee5ba27a7c
TASKS=""; for s in ${Q//-/ }; do case $s in 408|409|410|411|412) ;; *) echo "seed $s"; exit 1 ;; esac
  for a in A Sb SE; do TASKS="$TASKS SE1_${a}_s$s"; done; done; TASKS=${TASKS# }
OUTD=$P/results; COPY=/home/narolski/se1_results_copy; B=/workspace/se1
mkdir -p "$L" "$OUTD/logs_$Q" "$COPY"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/se1_drive.log"; }
case "$STEP" in
  setup)
    [ "$(cut -c1-64 /mnt/t7/smad_next/PN1/pn1_pack_fs.tar.sha256)" = "$PIN" ] || { log "local pack sha differs"; exit 1; }
    [ "$(sha256sum "$P/run.sh" | cut -c1-64)" = b2a975f1252fb87083085c535ce6630b6d92950440c5ab6ca36eba146c424fcb ] && (cd "$P" && sha256sum -c --quiet rescore.py.sha256 PN1_Sb_s403.tar.sha256) || { log "local files off their pins"; exit 1; }
    R "mkdir -p $B/root/packs/SE1 $B/root/results/SE1 $B/logs $B/rc $B/tmp $B/bin && nvidia-smi -L && nproc && df -h /workspace | tail -1" | tee -a "$L/se1_setup.log"
    T=$(mktemp -d -p "$P"); for t in $TASKS; do a=${t#SE1_}; a=${a%_s*}; s=${t##*_s}; mkdir -p "$T/$t"
      printf "TASK=%s\nARM=%s\nSEED=%s\n" "$t" "$a" "$s" > "$T/$t/task.env"; done
    RS /mnt/t7/smad_next/PN1/pn1_pack_fs.tar /mnt/t7/smad_next/PN1/pn1_pack_fs.tar.sha256 "$P/se1_overlay.tar" "$P/se1_overlay.tar.sha256" \
      "$P/run.sh" "$P/run.sh.sha256" "$P/rescore.py" "$P/rescore.py.sha256" "$P/PN1_Sb_s403.tar" "$P/PN1_Sb_s403.tar.sha256" "root@$HOST:$B/root/packs/SE1/"
    RS "$T/" "root@$HOST:$B/tasks/"; rm -rf "$T"
    RS "$SRC/remote_se1.sh" "root@$HOST:$B/bin/"
    R "bash $B/bin/remote_se1.sh setup $PIN $OVPIN" 2>&1 | tee -a "$L/se1_setup.log"
    grep -q SETUP_OK "$L/se1_setup.log" && log "SETUP_OK $Q" || { log "SETUP FAILED $Q"; exit 1; }
    ;;
  queue)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && CUDA_VISIBLE_DEVICES=0 nohup setsid bash $B/bin/remote_se1.sh queue $PIN $OVPIN '$TASKS' $Q > $B/logs/queue_driver_$Q.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_STARTED_$Q && echo SE1_QUEUE_STARTED" || true)
    echo "$msg" | grep -q SE1_QUEUE_STARTED || { log "queue start not confirmed"; exit 1; }
    log "queue $Q started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free: not pulling"; exit 1; }
    RS --include='SE1_*.tar' --include='SE1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/SE1/" "$OUTD/" || true
    ended=$(R "[ -f $B/ALL_DONE_$Q ] && echo ENDED || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    [ "$ended" = UNKNOWN ] && { log "remote state unreadable: no decision"; exit 0; }
    n=0; bad=""; for t in $TASKS SE1_platformcheck_$Q; do
      if [ -f "$OUTD/$t.tar" ] && (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256"); then n=$((n + 1)); else bad="$bad $t"; fi; done
    log "$Q verified $n of $(( $(echo $TASKS | wc -w) + 1 )) (remote $ended)"
    [ "$ended" = ENDED ] || exit 0
    RS "root@$HOST:$B/logs/" "$OUTD/logs_$Q/" && RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_$Q.log" "$OUTD/logs_$Q/" || { log "log fetch failed"; exit 0; }
    for t in $TASKS SE1_platformcheck_$Q; do [ -f "$OUTD/$t.tar" ] || continue
      cp "$OUTD/$t.tar" "$OUTD/$t.tar.sha256" "$COPY/"; (cd "$COPY" && sha256sum -c --quiet "$t.tar.sha256") || { log "second copy failed"; exit 0; }; done
    if [ -n "$bad" ]; then
      for t in $bad; do st=$(R "if [ -f $B/root/results/SE1/$t.tar ]; then echo PRESENT; elif [ -s $B/rc/$t ] && [ \"\$(cat $B/rc/$t)\" != 0 ]; then echo FAILED; else echo UNKNOWN; fi" 2>/dev/null || echo UNREACHABLE)
        [ "$st" = FAILED ] || { log "$t: remote $st, retry next loop"; exit 0; }; done
      [ -f "$L/HOLD" ] && { log "HOLD present"; exit 0; }
      echo "failed (remote-confirmed):$bad" > "$L/FAILED"; touch "$L/RELEASE"; log "RELEASE + FAILED ($bad)"
    else
      [ -f "$L/HOLD" ] && { log "HOLD present"; exit 0; }
      touch "$L/RELEASE"; log "RELEASE written (all verified, second copies in $COPY)"
    fi
    ;;
  loop) for k in $(seq 1 60); do bash "$0" "$HOST" "$PORT" "$L" "$Q" pull || true; [ -f "$L/RELEASE" ] && break; sleep 600; done ;;
  status) R "cat $B/queue_*.log 2>/dev/null; ls $B/root/results/SE1/; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader" ;;
esac

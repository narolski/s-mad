#!/bin/bash
# PN1 fresh seeds (registration FS1), DGX-side driver for one rented lease (no rental API; SSH key by path only).
#   bash drive_fs.sh HOST PORT LEASE M setup    # M = m1 | m2: upload the development pack (8.8 GB), run.sh v3 task folders,
#                                               # remote_fs.sh; pip pins; versions and GPU UUID -> LEASE/fs_setup.log
#   bash drive_fs.sh HOST PORT LEASE M queue    # start this machine's fixed queue, detached
#   bash drive_fs.sh HOST PORT LEASE M pull     # fetch finished tars + logs, verify sha256; RELEASE when the queue is
#                                               # fetched and verified; RELEASE + FAILED when the queue ended with a
#                                               # verified partial result
#   bash drive_fs.sh HOST PORT LEASE M loop     # pull every 10 min until RELEASE (at most 16 h)
#   bash drive_fs.sh HOST PORT LEASE M status
# Free-disk floor: no pull when /mnt/t7 has under 20 GB free (a fit tar is about 8 MB).
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; M=${4:?m1|m2}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN2=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
RUNSH=74a49b0baaeb99108664bf8243d079b708c94f4f87c154ff5840796288e48bb0
case "$M" in
  m1) TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s407 PN1_B_s407 PN1_Sb_s407" ;;
  m2) TASKS="PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_Arep_s401" ;;
  *) echo "machine must be m1 or m2"; exit 1 ;;
esac
P=/mnt/t7/smad_next/PN1; OUTD=$P/results_fs; B=/workspace/pn1
mkdir -p "$L" "$OUTD/logs_$M"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/fs_drive.log"; }
case "$STEP" in
  setup)
    [ "$(cut -c1-64 "$P/pn1_pack_fs.tar.sha256")" = "$PIN2" ] || { log "local pack sha file differs from pin"; exit 1; }
    [ "$(sha256sum "$SRC/../run.sh" | cut -c1-64)" = "$RUNSH" ] || { log "run.sh differs from its pin"; exit 1; }
    R "mkdir -p $B/root/packs/PN1 $B/root/results/PN1 $B/tasks $B/bin $B/logs $B/rc $B/tmp && nvidia-smi -L && nproc && df -h /workspace | tail -1" | tee -a "$L/fs_setup.log"
    T=$(mktemp -d -p "$P")
    for t in $TASKS; do
      a=${t#PN1_}; a=${a%_s*}; s=${t##*_s}; arm=$a; [ "$a" = Arep ] && arm=A
      mkdir -p "$T/$t"; cp "$SRC/../run.sh" "$T/$t/"; printf "TASK=%s\nARM=%s\nSEED=%s\n" "$t" "$arm" "$s" > "$T/$t/task.env"
    done
    T0=$SECONDS
    RS "$P/pn1_pack_fs.tar" "$P/pn1_pack_fs.tar.sha256" "root@$HOST:$B/root/packs/PN1/"
    log "pack upload $((SECONDS - T0)) s"
    RS "$T/" "root@$HOST:$B/tasks/"; rm -rf "$T"
    RS "$SRC/remote_fs.sh" "root@$HOST:$B/bin/"
    R "cat $B/tasks/*/task.env | paste -sd' '; sha256sum $B/tasks/*/run.sh | cut -c1-16 | sort | uniq -c" | tee -a "$L/fs_setup.log"
    R "bash $B/bin/remote_fs.sh setup $PIN2" 2>&1 | tee -a "$L/fs_setup.log"
    grep -q SETUP_OK "$L/fs_setup.log" && log "SETUP_OK $M" || { log "SETUP FAILED $M"; exit 1; }
    ;;
  queue)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_fs.sh queue $PIN2 '$TASKS' ${PN1_FS_AFTER_A14:+after_a14} > $B/logs/queue_fs_driver.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_FS_STARTED && echo FS_QUEUE_STARTED" || true)
    echo "$msg" | grep -q FS_QUEUE_STARTED || { log "queue start not confirmed"; exit 1; }
    log "queue $M started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free (< 20 GB floor): not pulling"; exit 1; }
    RS --include='PN1_*.tar' --include='PN1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs_$M/" || true
    RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_fs.log" "$OUTD/logs_$M/" 2>/dev/null || true
    ended=$(R "[ -f $B/ALL_DONE_FS ] && echo ENDED || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    n=0; NW=0; bad=""
    for t in $TASKS; do
      NW=$((NW + 1))
      if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ]; then
        (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256") && n=$((n + 1)) || { log "HASH MISMATCH $t"; bad="$bad $t"; }
      else bad="$bad $t"; fi
    done
    log "$M verified $n of $NW (remote $ended)"
    if [ "$n" -eq "$NW" ]; then touch "$L/RELEASE"; log "RELEASE written"
    elif [ "$ended" = ENDED ]; then
      sleep 60; RS --include='PN1_*.tar' --include='PN1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
      echo "missing or failed:$bad" > "$L/FAILED"; touch "$L/RELEASE"; log "RELEASE + FAILED written (missing or failed:$bad)"
    fi
    ;;
  loop)
    for k in $(seq 1 96); do bash "$0" "$HOST" "$PORT" "$L" "$M" pull || true; [ -f "$L/RELEASE" ] && break; sleep 600; done
    ;;
  status)
    R "cat $B/queue_fs.log 2>/dev/null; ls $B/root/results/PN1/; for f in $B/logs/PN1_*.log; do echo \$f; grep -E 'step|PN1_TASK_DONE|FAIL' \$f | tail -1; done 2>/dev/null | tail -8; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
esac

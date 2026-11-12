#!/bin/bash
# PN1 fresh seeds (registration FS1), DGX-side driver for one rented lease (no rental API; SSH key by path only).
#   bash drive_fs.sh HOST PORT LEASE M setup    # M = all (D3: one GPU, all 16 fits in one queue) | m1 | m2: upload the development pack (8.8 GB), run.sh v3 task folders,
#                                               # remote_fs.sh; pip pins; versions and GPU UUID -> LEASE/fs_setup.log
#   bash drive_fs.sh HOST PORT LEASE M queue    # start this machine's fixed queue, detached
#   bash drive_fs.sh HOST PORT LEASE M pull     # fetch finished tars + logs, verify sha256; RELEASE when the queue is
#                                               # fetched and verified; RELEASE + FAILED when the queue ended with a
#                                               # verified partial result
#   bash drive_fs.sh HOST PORT LEASE M loop     # pull every 10 min until RELEASE (at most 25 h)
#   bash drive_fs.sh HOST PORT LEASE M status
# Free-disk floor: no pull when /mnt/t7 has under 20 GB free (a fit tar is about 8 MB).
# One-host layout (PN1_FS_ONEHOST=1): both queues on one 2-GPU host, m1 on GPU 0, m2 on GPU 1 (PN1_GPU sets
# CUDA_VISIBLE_DEVICES for queue; default m1 -> 0, m2 -> 1). Each queue writes LEASE/DONE_<M> (+ FAILED_<M>);
# RELEASE (+ FAILED) only when DONE_m1 and DONE_m2 both exist. Without PN1_FS_ONEHOST, RELEASE per lease as before.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; M=${4:?m1|m2}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN2=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
RUNSH=04998a7c274229b861b840e2b5a793854a712a7fb031fb572e34e1c791a4c87e
case "$M" in
  m1) TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s407 PN1_B_s407 PN1_Sb_s407" ;;
  m2) TASKS="PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_Arep_s401" ;;
  all) TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_A_s407 PN1_B_s407 PN1_Sb_s407 PN1_Arep_s401" ;;   # deviation D3: one GPU, one queue
  *) echo "queue must be all, m1 or m2"; exit 1 ;;
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
    G=${PN1_GPU:-}; [ -z "$G" ] && { [ "$M" = m2 ] && G=1 || G=0; }; [ "${PN1_FS_ONEHOST:-0}" = 1 ] || G=0
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && CUDA_VISIBLE_DEVICES=$G nohup setsid bash $B/bin/remote_fs.sh queue $PIN2 '$TASKS' $M ${PN1_FS_AFTER_A14:+after_a14} > $B/logs/queue_fs_driver_$M.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_FS_STARTED_$M && echo FS_QUEUE_STARTED" || true)
    echo "$msg" | grep -q FS_QUEUE_STARTED || { log "queue start not confirmed"; exit 1; }
    log "queue $M started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free (< 20 GB floor): not pulling"; exit 1; }
    RS --include='PN1_*.tar' --include='PN1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs_$M/" || true
    RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_fs_$M.log" "$OUTD/logs_$M/" 2>/dev/null || true
    ended=$(R "[ -f $B/ALL_DONE_FS_$M ] && echo ENDED || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    verify() { n=0; NW=0; bad=""
      for t in $TASKS; do
        NW=$((NW + 1))
        if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256"); then n=$((n + 1))
        else bad="$bad $t"; fi
      done; }
    verify
    log "$M verified $n of $NW (remote $ended)"
    if [ "$n" -eq "$NW" ]; then touch "$L/DONE_$M"; log "DONE_$M"
    elif [ "$ended" = ENDED ]; then
      sleep ${PN1_FS_REPULL_WAIT:-60}
      RS --include='PN1_*.tar' --include='PN1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || { log "re-pull failed: retry next loop"; exit 0; }
      verify
      # a task counts as failed only if the remote confirms it: no tar there AND a non-zero rc file
      conf=""; for t in $bad; do
        st=$(R "if [ -f $B/root/results/PN1/$t.tar ]; then echo PRESENT; elif [ -s $B/rc/$t ] && [ \"\$(cat $B/rc/$t)\" != 0 ]; then echo FAILED; else echo UNKNOWN; fi" 2>/dev/null || echo UNREACHABLE)
        [ "$st" = FAILED ] || { log "$t: remote $st, not confirmed failed: retry next loop"; exit 0; }
        conf="$conf $t"
      done
      if [ -n "$conf" ]; then
        echo "failed (remote-confirmed: no tar, non-zero rc):$conf" > "$L/FAILED_$M"; touch "$L/DONE_$M"; log "DONE_$M + FAILED_$M ($conf)"
      else touch "$L/DONE_$M"; log "DONE_$M (after re-pull)"; fi
    fi
    if [ -f "$L/DONE_$M" ]; then
      if [ "${PN1_FS_ONEHOST:-0}" = 1 ]; then
        if [ -f "$L/DONE_m1" ] && [ -f "$L/DONE_m2" ]; then
          cat "$L"/FAILED_m* > "$L/FAILED" 2>/dev/null || rm -f "$L/FAILED"; [ -s "$L/FAILED" ] || rm -f "$L/FAILED"
          touch "$L/RELEASE"; log "RELEASE written (both queues)$( [ -f "$L/FAILED" ] && echo ' + FAILED')"
        else log "DONE_$M; waiting for the other queue before RELEASE"; fi
      else
        [ -f "$L/FAILED_$M" ] && cp "$L/FAILED_$M" "$L/FAILED"; touch "$L/RELEASE"; log "RELEASE written"
      fi
    fi
    ;;
  loop)
    for k in $(seq 1 150); do bash "$0" "$HOST" "$PORT" "$L" "$M" pull || true; { [ -f "$L/RELEASE" ] || [ -f "$L/DONE_$M" ]; } && break; sleep 600; done
    ;;
  status)
    R "cat $B/queue_fs_*.log 2>/dev/null; ls $B/root/results/PN1/; for f in $B/logs/PN1_*.log; do echo \$f; grep -E 'step|PN1_TASK_DONE|FAIL' \$f | tail -1; done 2>/dev/null | tail -8; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
esac

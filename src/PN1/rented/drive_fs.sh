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
# Chained queues (registration Sp, 1b8fe48): LEASE/QUEUES lists the queues of the host (e.g. "all sp"); when it exists,
# RELEASE (+ FAILED) is written only when every listed queue is DONE. `M=sp chain` writes QUEUES first, then uploads
# the Sp overlay, remote_sp.sh and the Sp task folders and starts remote_sp.sh (builds and checks the Sp pack, then
# waits for the host's fit lock). The keep step of a queue that is not the last listed one leaves out the logs of
# the later queues (they are still growing); the last queue verifies the whole logs folder.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; M=${4:?m1|m2}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN2=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
RUNSH=04998a7c274229b861b840e2b5a793854a712a7fb031fb572e34e1c791a4c87e
RUNSH_SP=6a23a7a4b3d22a9371e1a5929636c3e233952fe5f12846139dd4d703f3dcce02
PIN_OV=1c0d03f388834d59f293bdf2874b524c313948527ed646868ec3ebd7741a4bd9
PIN_SP=76528f16c17aa017d43ca6e872b332907e2c3c857ed02ff545a83e0831340089
case "$M" in
  m1) TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s407 PN1_B_s407 PN1_Sb_s407" ;;
  m2) TASKS="PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_Arep_s401" ;;
  all) TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_A_s407 PN1_B_s407 PN1_Sb_s407 PN1_Arep_s401" ;;   # deviation D3: one GPU, one queue
  sp) TASKS="PN1_Sp_s403 PN1_Sp_s404 PN1_Sp_s405" ;;   # registration Sp, chained after "all"
  *) echo "queue must be all, sp, m1 or m2"; exit 1 ;;
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
  chain)
    [ "$M" = sp ] || { log "chain is for M=sp only"; exit 1; }
    echo "all sp" > "$L/QUEUES"; log "QUEUES = all sp (RELEASE held until both queues are DONE)"
    [ "$(sha256sum "$P/pn1_overlay_sp.tar" | cut -c1-64)" = "$PIN_OV" ] || { log "overlay differs from its pin"; exit 1; }
    [ "$(sha256sum "$SRC/../run.sh" | cut -c1-64)" = "$RUNSH_SP" ] || { log "run.sh differs from the Sp pin"; exit 1; }
    T=$(mktemp -d -p "$P")
    for t in $TASKS; do s=${t##*_s}; mkdir -p "$T/$t"; cp "$SRC/../run.sh" "$T/$t/"; printf "TASK=%s\nARM=Sp\nSEED=%s\n" "$t" "$s" > "$T/$t/task.env"; done
    RS "$P/pn1_overlay_sp.tar" "root@$HOST:$B/root/packs/PN1/"
    RS "$T/" "root@$HOST:$B/tasks/"; rm -rf "$T"
    RS "$SRC/remote_sp.sh" "root@$HOST:$B/bin/"
    R "sha256sum $B/root/packs/PN1/pn1_overlay_sp.tar $B/bin/remote_sp.sh $B/tasks/PN1_Sp_s40*/run.sh | cut -c1-16; cat $B/tasks/PN1_Sp_s40*/task.env | paste -sd' '" | tee -a "$L/fs_drive.log"
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && CUDA_VISIBLE_DEVICES=0 nohup setsid bash $B/bin/remote_sp.sh $PIN2 $PIN_SP '$TASKS' > $B/logs/queue_fs_driver_sp.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_FS_STARTED_sp && echo SP_CHAINED" || true)
    echo "$msg" | grep -q SP_CHAINED || { log "Sp chain start not confirmed"; exit 1; }
    log "Sp chained: $TASKS (pack build, then waits for the fit lock)"
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
    keep() {  # OWNER_BRIEF rule (12 Nov): logs are copied back and verified before DONE; sha256 lists kept in the repo
      RS "root@$HOST:$B/logs/" "$OUTD/logs_$M/" || return 1
      RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_fs_$M.log" "$OUTD/logs_$M/" || return 1
      excl=""
      if [ -f "$L/QUEUES" ]; then
        last=$(awk '{print $NF}' "$L/QUEUES")
        if [ "$M" != "$last" ]; then for q in $(cat "$L/QUEUES"); do [ "$q" = "$M" ] && continue
          [ "$q" = sp ] && excl="$excl PN1_Sp_s403.log PN1_Sp_s404.log PN1_Sp_s405.log sp_pack.log queue_fs_driver_sp.log"; done; fi
      fi
      rem=$(R "cd $B/logs && sha256sum * 2>/dev/null | sort -k2; echo KEEP_LISTED" 2>/dev/null) || return 1
      for x in $excl; do rem=$(echo "$rem" | awk -v x="$x" '$2 != x'); done
      echo "$rem" | grep -q KEEP_LISTED || return 1
      loc=$(cd "$OUTD/logs_$M" && sha256sum $(echo "$rem" | grep -v KEEP_LISTED | awk '{print $2}') 2>/dev/null | sort -k2)
      [ "$loc" = "$(echo "$rem" | grep -v KEEP_LISTED)" ] || { log "log copy differs from the remote: retry"; return 1; }
      E=/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/fs_kept
      mkdir -p "$E"
      echo "$loc" > "$E/logs_${M}_sha256.txt"
      (cd "$OUTD" && cat $(for t in $TASKS; do [ -f "$t.tar.sha256" ] && echo "$t.tar.sha256"; done)) > "$E/tars_${M}_sha256.txt"
      log "kept: logs verified ($(echo "$loc" | wc -l) files), tar sha256 list written"
    }
    verify() { n=0; NW=0; bad=""
      for t in $TASKS; do
        NW=$((NW + 1))
        if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256"); then n=$((n + 1))
        else bad="$bad $t"; fi
      done; }
    verify
    log "$M verified $n of $NW (remote $ended)"
    if [ "$n" -eq "$NW" ]; then keep || { log "keep step failed: retry next loop"; exit 0; }; touch "$L/DONE_$M"; log "DONE_$M"
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
      keep || { log "keep step failed: retry next loop"; exit 0; }
      if [ -n "$conf" ]; then
        echo "failed (remote-confirmed: no tar, non-zero rc):$conf" > "$L/FAILED_$M"; touch "$L/DONE_$M"; log "DONE_$M + FAILED_$M ($conf)"
      else touch "$L/DONE_$M"; log "DONE_$M (after re-pull)"; fi
    fi
    if [ -f "$L/DONE_$M" ] && [ -f "$L/QUEUES" ]; then
      alldone=1; for q in $(cat "$L/QUEUES"); do [ -f "$L/DONE_$q" ] || alldone=0; done
      if [ $alldone = 1 ]; then
        cat $(for q in $(cat "$L/QUEUES"); do [ -f "$L/FAILED_$q" ] && echo "$L/FAILED_$q"; done) /dev/null > "$L/FAILED"; [ -s "$L/FAILED" ] || rm -f "$L/FAILED"
        touch "$L/RELEASE"; log "RELEASE written (queues: $(cat "$L/QUEUES"))$( [ -f "$L/FAILED" ] && echo ' + FAILED')"
      else log "DONE_$M; RELEASE held until every queue in QUEUES ($(cat "$L/QUEUES")) is DONE"; fi
    elif [ -f "$L/DONE_$M" ]; then
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

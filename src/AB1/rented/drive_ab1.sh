#!/bin/bash
# AB1 rented fallback (used only if the lead moves SE1 and AB1 to rented machines; AB1 follows SE1's platform), DGX-side
# driver for one lease. Adapted from src/MS1/rented/drive_ms1.sh (no held-out step; FS1 pack + AB1 overlay).
#   bash drive_ab1.sh HOST PORT LEASE Q setup   # Q = a seed list "408 409" (whole seeds per lease, arms A Sb B Sp SbZ SbH SbS
#                                               # AS per seed); uploads the FS1 pack (8.75 GB), the overlay, tasks, remote_ab1.sh
#   bash drive_ab1.sh HOST PORT LEASE Q queue   # start the queue (fits), detached
#   bash drive_ab1.sh HOST PORT LEASE Q pull    # fetch tars (weights + scores), logs; verify sha256; RELEASE when
#                                               # everything is fetched and verified; RELEASE + FAILED on a verified partial
#                                               # result whose failures the remote confirms; no decision on unreadable state
#   bash drive_ab1.sh HOST PORT LEASE Q loop    # pull every 10 min until RELEASE (at most 20 h)
#   bash drive_ab1.sh HOST PORT LEASE Q status
# Floors: no pull when /mnt/t7 has under 20 GB free. A second copy of every verified tar goes to /home/narolski/ab1_results_copy.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; Q=${4:?m1|m2|m3}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${AB1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
HPIN=4e3afaa1e2771d86c75631b116cf7a604c082ca61bd6159089a7418f66240033
RUNSH=${AB1_RUNSH_PIN:?AB1_RUNSH_PIN (run.sh sha256 from prereg section 11)}
QN=$(echo "$Q" | tr ' ' '_'); for s in $Q; do case "$s" in 408|409|410|411|412) ;; *) echo "seed $s" >&2; exit 1 ;; esac; done
TASKS=""; for s in $Q; do for a in ${AB1_ARMS:-A Sb B Sp SbZ SbH SbS AS}; do TASKS="$TASKS AB1_${a}_s$s"; done; done; TASKS=${TASKS# }
P=/mnt/t7/smad_next/AB1; OUTD=$P/results; COPY=/home/narolski/ab1_results_copy; B=/workspace/ab1
mkdir -p "$L" "$OUTD/logs_$QN" "$COPY"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/ab1_drive.log"; }
case "$STEP" in
  setup)
    F=/mnt/t7/smad_next/PN1/pn1_pack_fs.tar
    [ "$(cut -c1-64 "$F.sha256")" = "$PIN" ] || { log "local pack sha file differs from pin"; exit 1; }
    [ "$(cut -c1-64 "$P/ab1_overlay.tar.sha256")" = "$HPIN" ] || { log "local overlay sha file differs from pin"; exit 1; }
    [ "$(sha256sum "$SRC/../run.sh" | cut -c1-64)" = "$RUNSH" ] || { log "run.sh differs from its pin"; exit 1; }
    R "mkdir -p $B/root/packs/BB2 $B/root/packs/AB1 $B/root/results/AB1 $B/tasks $B/bin $B/logs $B/rc $B/tmp && nvidia-smi -L && nproc && df -h /workspace | tail -1" | tee -a "$L/ab1_setup.log"
    T=$(mktemp -d -p "$P")
    for t in $TASKS; do a=${t#AB1_}; a=${a%_s*}; s=${t##*_s}
      mkdir -p "$T/$t"; cp "$SRC/../run.sh" "$T/$t/"; printf "TASK=%s\nARM=%s\nSEED=%s\n" "$t" "$a" "$s" > "$T/$t/task.env"; done
    T0=$SECONDS
    RS "$F" "$F.sha256" "root@$HOST:$B/root/packs/BB2/" && RS "$P/ab1_overlay.tar" "$P/ab1_overlay.tar.sha256" "root@$HOST:$B/root/packs/AB1/"
    log "pack upload $((SECONDS - T0)) s"
    RS "$T/" "root@$HOST:$B/tasks/"; rm -rf "$T"
    RS "$SRC/remote_ab1.sh" "root@$HOST:$B/bin/"
    R "cat $B/tasks/*/task.env | paste -sd' '; sha256sum $B/tasks/*/run.sh | cut -c1-16 | sort | uniq -c" | tee -a "$L/ab1_setup.log"
    R "bash $B/bin/remote_ab1.sh setup $PIN $HPIN" 2>&1 | tee -a "$L/ab1_setup.log"
    grep -q SETUP_OK "$L/ab1_setup.log" && log "SETUP_OK $Q" || { log "SETUP FAILED $Q"; exit 1; }
    ;;
  queue)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && CUDA_VISIBLE_DEVICES=0 nohup setsid bash $B/bin/remote_ab1.sh queue $PIN $HPIN '$TASKS' $QN > $B/logs/queue_driver_$QN.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_STARTED_$QN && echo AB1_QUEUE_STARTED" || true)
    echo "$msg" | grep -q AB1_QUEUE_STARTED || { log "queue start not confirmed"; exit 1; }
    log "queue $Q started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free (< 20 GB floor): not pulling"; exit 1; }
    RS --include='AB1_*.tar' --include='AB1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/AB1/" "$OUTD/" || true
    ended=$(R "[ -f $B/ALL_DONE_$QN ] && echo ENDED || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    [ "$ended" = UNKNOWN ] && { log "remote state unreadable: no decision"; exit 0; }
    verify() { n=0; NW=0; bad=""
      for t in $TASKS; do NW=$((NW + 1))
        if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256"); then n=$((n + 1)); else bad="$bad $t"; fi
      done; }
    verify; log "$Q verified $n of $NW fits (remote $ended)"
    [ "$ended" = ENDED ] || exit 0
    keep() {  # held-out tar, logs, rc and queue log fetched and verified; second copy of every verified tar
      RS "root@$HOST:$B/logs/" "$OUTD/logs_$QN/" || return 1
      RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_$QN.log" "$OUTD/logs_$QN/" || return 1
      # one remote listing taken after ENDED: every log, every rc file and the queue log (all final once the queue has
      # ended); both sides sorted under LC_ALL=C (fix of 13 Nov 06:10: the remote sorted in the C locale, the DGX in
      # en_US, so equal files compared unequal by order only)
      rem=$(R "cd $B/logs && sha256sum * && cd $B && sha256sum rc/* queue_$QN.log; echo KEEP_LISTED" 2>/dev/null) || return 1
      echo "$rem" | grep -q KEEP_LISTED || return 1
      rem=$(echo "$rem" | grep -v KEEP_LISTED | LC_ALL=C sort -k2; echo KEEP_LISTED)
      loc=$(cd "$OUTD/logs_$QN" && sha256sum $(echo "$rem" | grep -v KEEP_LISTED | awk '{print $2}') | LC_ALL=C sort -k2)
      [ "$loc" = "$(echo "$rem" | grep -v KEEP_LISTED)" ] || { log "log copy differs from the remote"; return 1; }
      for f in $(cd "$OUTD" && ls AB1_*.tar 2>/dev/null); do
        case " $TASKS " in *" ${f%.tar} "*) ;; *) continue ;; esac
        cp "$OUTD/$f" "$OUTD/$f.sha256" "$COPY/"; (cd "$COPY" && sha256sum -c --quiet "$f.sha256") || return 1
      done
      E=/home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication/rented_kept; mkdir -p "$E"
      echo "$loc" > "$E/logs_${QN}_sha256.txt"
      (cd "$OUTD" && cat $(for t in $TASKS; do [ -f "$t.tar.sha256" ] && echo "$t.tar.sha256"; done)) > "$E/tars_${QN}_sha256.txt"
      log "kept: logs ($(echo "$loc" | wc -l) files) verified; second copies in $COPY"
    }
    if [ "$n" -lt "$NW" ]; then
      sleep ${AB1_REPULL_WAIT:-60}
      RS --include='AB1_*.tar' --include='AB1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/AB1/" "$OUTD/" || { log "re-pull failed: retry next loop"; exit 0; }
      verify
      conf=""; for t in $bad; do
        st=$(R "if [ -f $B/root/results/AB1/$t.tar ]; then echo PRESENT; elif [ -s $B/rc/$t ] && [ \"\$(cat $B/rc/$t)\" != 0 ]; then echo FAILED; else echo UNKNOWN; fi" 2>/dev/null || echo UNREACHABLE)
        [ "$st" = FAILED ] || { log "$t: remote $st, not confirmed failed: retry next loop"; exit 0; }
        conf="$conf $t"; done
      keep || { log "keep step failed: retry next loop"; exit 0; }
      [ -f "$L/HOLD" ] && { log "HOLD present: RELEASE deferred"; exit 0; }
      echo "failed (remote-confirmed: no tar, non-zero rc):$conf" > "$L/FAILED"; touch "$L/RELEASE"; log "RELEASE + FAILED ($conf)"
    else
      keep || { log "keep step failed: retry next loop"; exit 0; }
      [ -f "$L/HOLD" ] && { log "HOLD present: RELEASE deferred"; exit 0; }
      touch "$L/RELEASE"; log "RELEASE written ($n of $NW fits verified)"
    fi
    ;;
  loop)
    for k in $(seq 1 120); do bash "$0" "$HOST" "$PORT" "$L" "$Q" pull || true; [ -f "$L/RELEASE" ] && break; sleep 600; done
    ;;
  status)
    R "cat $B/queue_*.log 2>/dev/null; ls $B/root/results/AB1/ 2>/dev/null; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
esac

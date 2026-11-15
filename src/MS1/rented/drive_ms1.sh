#!/bin/bash
# MS1 rented fallback (deviation MS1-D1), DGX-side driver for one rented A100 PCIe 40 GB lease (no rental API; SSH key by
# path only). Adapted from src/PN1/rented/drive_fs.sh.
#   bash drive_ms1.sh HOST PORT LEASE Q setup   # Q = m1 (seeds 403, 406) | m2 (404, 407) | m3 (405): uploads the fit pack
#                                               # (14.5 GB), the held-out pack (0.96 GB), task folders, remote_ms1.sh; pip pins
#   bash drive_ms1.sh HOST PORT LEASE Q queue   # start the queue (fits, then the held-out step), detached
#   bash drive_ms1.sh HOST PORT LEASE Q pull    # fetch tars (weights + scores), held-out tar, logs; verify sha256; RELEASE when
#                                               # everything is fetched and verified; RELEASE + FAILED on a verified partial
#                                               # result whose failures the remote confirms; no decision on unreadable state
#   bash drive_ms1.sh HOST PORT LEASE Q loop    # pull every 10 min until RELEASE (at most 20 h)
#   bash drive_ms1.sh HOST PORT LEASE Q status
# Floors: no pull when /mnt/t7 has under 20 GB free. A second copy of every verified tar goes to /home/narolski/ms1_results_copy.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; Q=${4:?m1|m2|m3}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${MS1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d
HPIN=396a7ebeacf1f4b31077e04e0588e0ff84b9287457b8980ea95c9c91fee693a7
RUNSH=098e94cd2821c415803f1b080b5e655e5c164bed040abffa10afe93bf1f669ed
seeds() { case "$Q" in m1) echo "403 406" ;; m2) echo "404 407" ;; m3) echo "405" ;; *) echo "queue must be m1, m2 or m3" >&2; exit 1 ;; esac; }
TASKS=""; for s in $(seeds); do for a in Sb SbM3 SbV; do TASKS="$TASKS MS1_${a}_s$s"; done; done; TASKS=${TASKS# }
P=/mnt/t7/smad_next/MS1; OUTD=$P/results_rented; COPY=/home/narolski/ms1_results_copy; B=/workspace/ms1
mkdir -p "$L" "$OUTD/logs_$Q" "$COPY"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/ms1_drive.log"; }
case "$STEP" in
  setup)
    [ "$(cut -c1-64 "$P/pn1_pack_ms1.tar.sha256")" = "$PIN" ] || { log "local pack sha file differs from pin"; exit 1; }
    [ "$(cut -c1-64 "$P/ms1_heldout_pack.tar.sha256")" = "$HPIN" ] || { log "local held-out sha file differs from pin"; exit 1; }
    [ "$(sha256sum "$SRC/../run.sh" | cut -c1-64)" = "$RUNSH" ] || { log "run.sh differs from its pin"; exit 1; }
    R "mkdir -p $B/root/packs/MS1 $B/root/results/MS1 $B/tasks $B/bin $B/logs $B/rc $B/tmp && nvidia-smi -L && nproc && df -h /workspace | tail -1" | tee -a "$L/ms1_setup.log"
    T=$(mktemp -d -p "$P")
    for t in $TASKS; do a=${t#MS1_}; a=${a%_s*}; s=${t##*_s}
      mkdir -p "$T/$t"; cp "$SRC/../run.sh" "$T/$t/"; printf "TASK=%s\nARM=%s\nSEED=%s\n" "$t" "$a" "$s" > "$T/$t/task.env"; done
    T0=$SECONDS
    RS "$P/pn1_pack_ms1.tar" "$P/pn1_pack_ms1.tar.sha256" "$P/ms1_heldout_pack.tar" "$P/ms1_heldout_pack.tar.sha256" "root@$HOST:$B/root/packs/MS1/"
    log "pack upload $((SECONDS - T0)) s"
    RS "$T/" "root@$HOST:$B/tasks/"; rm -rf "$T"
    RS "$SRC/remote_ms1.sh" "root@$HOST:$B/bin/"
    R "cat $B/tasks/*/task.env | paste -sd' '; sha256sum $B/tasks/*/run.sh | cut -c1-16 | sort | uniq -c" | tee -a "$L/ms1_setup.log"
    R "bash $B/bin/remote_ms1.sh setup $PIN $HPIN" 2>&1 | tee -a "$L/ms1_setup.log"
    grep -q SETUP_OK "$L/ms1_setup.log" && log "SETUP_OK $Q" || { log "SETUP FAILED $Q"; exit 1; }
    ;;
  queue)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && CUDA_VISIBLE_DEVICES=0 nohup setsid bash $B/bin/remote_ms1.sh queue $PIN $HPIN '$TASKS' $Q > $B/logs/queue_driver_$Q.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_STARTED_$Q && echo MS1_QUEUE_STARTED" || true)
    echo "$msg" | grep -q MS1_QUEUE_STARTED || { log "queue start not confirmed"; exit 1; }
    log "queue $Q started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 20 ] || { log "T7 has ${avail} GB free (< 20 GB floor): not pulling"; exit 1; }
    RS --include='MS1_*.tar' --include='MS1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/MS1/" "$OUTD/" || true
    ended=$(R "[ -f $B/ALL_DONE_$Q ] && echo ENDED || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    [ "$ended" = UNKNOWN ] && { log "remote state unreadable: no decision"; exit 0; }
    verify() { n=0; NW=0; bad=""
      for t in $TASKS; do NW=$((NW + 1))
        if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256"); then n=$((n + 1)); else bad="$bad $t"; fi
      done; }
    verify; log "$Q verified $n of $NW fits (remote $ended)"
    [ "$ended" = ENDED ] || exit 0
    keep() {  # held-out tar, logs, rc and queue log fetched and verified; second copy of every verified tar
      RS "root@$HOST:$B/root/results/MS1H/MS1H_$Q.tar" "root@$HOST:$B/root/results/MS1H/MS1H_$Q.tar.sha256" "$OUTD/" || return 1
      (cd "$OUTD" && sha256sum -c --quiet "MS1H_$Q.tar.sha256") || { log "held-out tar not verified"; return 1; }
      RS "root@$HOST:$B/logs/" "$OUTD/logs_$Q/" || return 1
      RS "root@$HOST:$B/rc" "root@$HOST:$B/queue_$Q.log" "$OUTD/logs_$Q/" || return 1
      # one remote listing taken after ENDED: every log, every rc file and the queue log (all final once the queue has
      # ended); both sides sorted under LC_ALL=C (fix of 13 Nov 06:10: the remote sorted in the C locale, the DGX in
      # en_US, so equal files compared unequal by order only)
      rem=$(R "cd $B/logs && sha256sum * && cd $B && sha256sum rc/* queue_$Q.log; echo KEEP_LISTED" 2>/dev/null) || return 1
      echo "$rem" | grep -q KEEP_LISTED || return 1
      rem=$(echo "$rem" | grep -v KEEP_LISTED | LC_ALL=C sort -k2; echo KEEP_LISTED)
      loc=$(cd "$OUTD/logs_$Q" && sha256sum $(echo "$rem" | grep -v KEEP_LISTED | awk '{print $2}') | LC_ALL=C sort -k2)
      [ "$loc" = "$(echo "$rem" | grep -v KEEP_LISTED)" ] || { log "log copy differs from the remote"; return 1; }
      for f in $(cd "$OUTD" && ls MS1_*.tar MS1H_$Q.tar 2>/dev/null); do
        case " $TASKS MS1H_$Q " in *" ${f%.tar} "*) ;; *) continue ;; esac
        cp "$OUTD/$f" "$OUTD/$f.sha256" "$COPY/"; (cd "$COPY" && sha256sum -c --quiet "$f.sha256") || return 1
      done
      E=/home/narolski/smad-next/experiments/MS1_multi-source-training-set/rented_kept; mkdir -p "$E"
      echo "$loc" > "$E/logs_${Q}_sha256.txt"
      (cd "$OUTD" && cat $(for t in $TASKS MS1H_$Q; do [ -f "$t.tar.sha256" ] && echo "$t.tar.sha256"; done)) > "$E/tars_${Q}_sha256.txt"
      log "kept: held-out tar, logs ($(echo "$loc" | wc -l) files) verified; second copies in $COPY"
    }
    if [ "$n" -lt "$NW" ]; then
      sleep ${MS1_REPULL_WAIT:-60}
      RS --include='MS1_*.tar' --include='MS1_*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/MS1/" "$OUTD/" || { log "re-pull failed: retry next loop"; exit 0; }
      verify
      conf=""; for t in $bad; do
        st=$(R "if [ -f $B/root/results/MS1/$t.tar ]; then echo PRESENT; elif [ -s $B/rc/$t ] && [ \"\$(cat $B/rc/$t)\" != 0 ]; then echo FAILED; else echo UNKNOWN; fi" 2>/dev/null || echo UNREACHABLE)
        [ "$st" = FAILED ] || { log "$t: remote $st, not confirmed failed: retry next loop"; exit 0; }
        conf="$conf $t"; done
      keep || { log "keep step failed: retry next loop"; exit 0; }
      [ -f "$L/HOLD" ] && { log "HOLD present: RELEASE deferred"; exit 0; }
      echo "failed (remote-confirmed: no tar, non-zero rc):$conf" > "$L/FAILED"; touch "$L/RELEASE"; log "RELEASE + FAILED ($conf)"
    else
      keep || { log "keep step failed: retry next loop"; exit 0; }
      [ -f "$L/HOLD" ] && { log "HOLD present: RELEASE deferred"; exit 0; }
      touch "$L/RELEASE"; log "RELEASE written ($n of $NW fits + held-out tar verified)"
    fi
    ;;
  loop)
    for k in $(seq 1 120); do bash "$0" "$HOST" "$PORT" "$L" "$Q" pull || true; [ -f "$L/RELEASE" ] && break; sleep 600; done
    ;;
  status)
    R "cat $B/queue_*.log 2>/dev/null; ls $B/root/results/MS1/ $B/root/results/MS1H/ 2>/dev/null; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
esac

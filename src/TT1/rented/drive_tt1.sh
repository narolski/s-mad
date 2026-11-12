#!/bin/bash
# TT1 deviation TT1-D1: DGX-side driver for one rented A100 lease (no rental API; SSH key by path, never printed).
#   bash drive_tt1.sh HOST PORT LEASE start [test]  # upload pack + nets (rsync --partial) and bin; start remote_tt1.sh
#   bash drive_tt1.sh HOST PORT LEASE pull          # fetch result tar + logs, verify, second local copy; RELEASE rules
#   bash drive_tt1.sh HOST PORT LEASE loop          # pull every 3 min (at most 2 h)
# RELEASE rules: RELEASE only after the result tar (sha256) and every log file (remote sha256 listing) are verified
# locally AND copied a second time to /mnt/t7/smad_next/TT1/results/ (verified); rc 0 -> RELEASE; rc GATE_FAILED or
# FATAL* (verified) -> RELEASE + FAILED; unreadable or missing remote state -> no decision.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease folder}; STEP=${4:?step}; MODE=${5:-full}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
O=/mnt/t7/smad_next/TT1; B=/workspace/tt1
PSHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
NSHA=92bd1841bd9307659c4666bfc344974592613e310f2ee4187dc3fc6884205303
OUTD=$L/results; KEEP=$O/results
mkdir -p "$L" "$OUTD" "$KEEP"
SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${SO[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/tt1_drive.log"; }
case "$STEP" in
  start)
    [ "$(cut -c1-64 "$O/tt1_pack.tar.sha256")" = "$PSHA" ] && [ "$(cut -c1-64 "$O/tt1_nets_s401402.tar.sha256")" = "$NSHA" ] \
      || { log "local sha files differ from the pins"; exit 1; }
    R "mkdir -p $B/packs $B/bin $B/logs $B/rc $B/results && nvidia-smi -L && df -h /workspace | tail -1" | tee -a "$L/tt1_drive.log"
    BIN=$L/bin; rm -rf "$BIN"; mkdir -p "$BIN"
    cp "$SRC/remote_tt1.sh" "$SRC/../gate_check_a100.py" "$SRC/../diag_stack.py" "$BIN/"
    (cd "$BIN" && sha256sum remote_tt1.sh gate_check_a100.py diag_stack.py > SHA256SUMS)
    RS "$BIN/" "root@$HOST:$B/bin/"
    RS "$O/tt1_nets_s401402.tar" "$O/tt1_nets_s401402.tar.sha256" "$O/tt1_hn2.tar" "$O/tt1_hn2.tar.sha256" "root@$HOST:$B/packs/"
    RS "$O/tt1_pack.tar" "$O/tt1_pack.tar.sha256" "root@$HOST:$B/packs/"
    log "uploaded"
    msg=$(timeout 30 ssh "${SO[@]}" "root@$HOST" "cd $B && rm -f $B/DONE && nohup setsid bash $B/bin/remote_tt1.sh $PSHA $NSHA $MODE > $B/logs/remote.log 2>&1 < /dev/null & sleep 2; echo TT1_STARTED" || true)
    echo "$msg" | grep -q TT1_STARTED || { log "TT1_STARTED not seen"; exit 1; }
    log "remote_tt1.sh ($MODE) started"
    ;;
  pull)
    T=TT1_A100_s401402_$MODE
    if ! R "test -f $B/DONE" 2>/dev/null; then
      log "not done (or remote unreadable): $(R "tail -1 $B/work/res/$T/calls.log" 2>/dev/null || echo unreadable)"; exit 0
    fi
    RS --include="$T.tar*" --include="logs.sha256" --exclude='*' "root@$HOST:$B/results/" "$OUTD/" || { log "fetch failed"; exit 0; }
    RS "root@$HOST:$B/logs/" "$OUTD/logs/" || { log "log fetch failed"; exit 0; }
    (cd "$OUTD" && sha256sum -c --quiet "$T.tar.sha256") || { log "result tar sha256 mismatch"; exit 0; }
    (cd "$OUTD/logs" && sha256sum -c --quiet ../logs.sha256) || { log "log sha256 mismatch"; exit 0; }
    cp "$OUTD/$T.tar" "$OUTD/$T.tar.sha256" "$KEEP/"
    (cd "$KEEP" && sha256sum -c --quiet "$T.tar.sha256") || { log "second copy mismatch"; exit 0; }
    mkdir -p "$KEEP/logs_$T"; cp -r "$OUTD/logs/." "$KEEP/logs_$T/"; cp "$OUTD/logs.sha256" "$KEEP/logs_$T/"
    (cd "$KEEP/logs_$T" && sha256sum -c --quiet logs.sha256) || { log "second log copy mismatch"; exit 0; }
    rc=$(tar -xOf "$OUTD/$T.tar" "$T/rc" 2>/dev/null || echo "rc unreadable")
    if [ "$MODE" = test ]; then log "test result verified (rc $rc); no RELEASE in test mode"; exit 0; fi
    case "$rc" in
      0) touch "$L/RELEASE"; log "verified $T rc 0; two copies; RELEASE" ;;
      GATE_FAILED|FATAL*) echo "$rc" > "$L/FAILED"; touch "$L/RELEASE"; log "verified $T rc $rc; two copies; RELEASE + FAILED" ;;
      *) log "rc '$rc': no decision" ;;
    esac
    ;;
  loop)
    for k in $(seq 1 40); do bash "$0" "$HOST" "$PORT" "$L" pull "$MODE" || true; [ -f "$L/RELEASE" ] && break; sleep ${TT1_LOOP_SLEEP:-180}; done
    ;;
esac

#!/bin/bash
# TT1 extension block TT1-X (prereg_x_block.md), DGX-side driver. Never writes RELEASE into the lease folder: it keeps
# LEASE/tt1 and writes TT1X_DONE_<TAG> (+ TT1X_FAILED_<TAG>) there after two verified copies of result tar and logs.
#   TAG=sp TASKS="PN1_Sp_s403 ..." LOCAL_TARS=/dir GPU_UUID=... DEADLINE_EPOCH=... GATE_PACK=/host/path/pack.tar \
#     GATE_PACK_SHA=... [GATE_TOP=pn1 GATE_MANIFEST=pn1_eval.csv REMOTE_P=/workspace/pn1] \
#   bash drive_tt1_x.sh HOST PORT LEASE start|pull|loop
set -euo pipefail
HOST=${1:?}; PORT=${2:?}; L0=${3:?}; STEP=${4:?}
: "${TAG:?}" "${TASKS:?}" "${LOCAL_TARS:?}" "${GPU_UUID:?}" "${DEADLINE_EPOCH:?}" "${GATE_PACK:?}" "${GATE_PACK_SHA:?}"
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
L=$L0/tt1; mkdir -p "$L/results_$TAG"
O=/mnt/t7/smad_next/TT1; B=/workspace/tt1; RP=${REMOTE_P:-/workspace/pn1}
PSHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
LEASE=$(basename "$L0"); T=TT1_${LEASE}_${TAG}
SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L0/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=180 -e "ssh ${SO[*]}" "$@"; }
log() { echo "$(date +%T) [$TAG] $*" | tee -a "$L/tt1_x_drive.log"; }
case "$STEP" in
  start)
    BIN=$L/bin_$TAG; rm -rf "$BIN"; mkdir -p "$BIN"; : > "$BIN/nets_pins.txt"
    for t in $TASKS; do
      [ -f "$LOCAL_TARS/$t.tar" ] && (cd "$LOCAL_TARS" && sha256sum -c --quiet "$t.tar.sha256") || { log "local copy of $t missing or unverified"; exit 1; }
      cut -c1-64 "$LOCAL_TARS/$t.tar.sha256" | sed "s|$|  $t.tar|" >> "$BIN/nets_pins.txt"
    done
    cp "$SRC/remote_tt1_x.sh" "$SRC/../rescore_tf32.py" "$SRC/../gate_check_fs.py" "$BIN/"
    (cd "$BIN" && sha256sum remote_tt1_x.sh rescore_tf32.py gate_check_fs.py nets_pins.txt > SHA256SUMS)
    RS "$BIN/" "root@$HOST:$B/bin_$TAG/"
    ENV="TT1_FS_P=$RP TT1_GPU_UUID=$GPU_UUID TT1_DEADLINE_EPOCH=$DEADLINE_EPOCH TT1_GATE_TOP=${GATE_TOP:-pn1} TT1_GATE_MANIFEST=${GATE_MANIFEST:-pn1_eval.csv}"
    msg=$(timeout 30 ssh "${SO[@]}" "root@$HOST" "cd $B && rm -f $B/DONE_$TAG && $ENV nohup setsid bash $B/bin_$TAG/remote_tt1_x.sh $PSHA $GATE_PACK_SHA $LEASE $TAG $GATE_PACK > $B/logs/remote_$TAG.log 2>&1 < /dev/null & sleep 2; echo TT1X_STARTED" || true)
    echo "$msg" | grep -q TT1X_STARTED || { log "TT1X_STARTED not seen"; exit 1; }
    log "started (waits for the host fit lock)"
    ;;
  pull)
    if ! R "test -f $B/DONE_$TAG" 2>/dev/null; then log "not done (or unreadable): $(R "tail -1 $B/work_$TAG/res/$T/calls.log" 2>/dev/null || echo unreadable)"; exit 0; fi
    D=$L/results_$TAG
    RS --include="$T.tar*" --include="logs_$TAG.sha256" --exclude='*' "root@$HOST:$B/results/" "$D/" || { log "fetch failed"; exit 0; }
    RS "root@$HOST:$B/logs/" "$D/logs/" || { log "log fetch failed"; exit 0; }
    (cd "$D" && sha256sum -c --quiet "$T.tar.sha256") || { log "tar sha256 mismatch"; exit 0; }
    (cd "$D/logs" && sha256sum -c --quiet ../logs_$TAG.sha256) || { log "log sha256 mismatch"; exit 0; }
    cp "$D/$T.tar" "$D/$T.tar.sha256" "$O/results/"
    (cd "$O/results" && sha256sum -c --quiet "$T.tar.sha256") || { log "second copy mismatch"; exit 0; }
    mkdir -p "$O/results/logs_$T" && cp -r "$D/logs/." "$O/results/logs_$T/"
    rc=$(tar -xOf "$D/$T.tar" "$T/rc" 2>/dev/null || echo unreadable)
    case "$rc" in
      0) touch "$L/TT1X_DONE_$TAG"; log "verified $T rc 0; two copies; TT1X_DONE_$TAG" ;;
      FATAL*) echo "$rc" > "$L/TT1X_FAILED_$TAG"; touch "$L/TT1X_DONE_$TAG"; log "verified $T rc $rc; TT1X_DONE + FAILED" ;;
      *) log "rc '$rc': no decision" ;;
    esac
    ;;
  loop)
    for k in $(seq 1 80); do bash "$0" "$HOST" "$PORT" "$L0" pull || true; [ -f "$L/TT1X_DONE_$TAG" ] && break; sleep 180; done
    ;;
esac

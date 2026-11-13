#!/bin/bash
# TT1 FS1 block, DGX-side driver for the fresh-seed host pn1fs (lease owned by the PN1/FS1 driver; this script never
# writes RELEASE into that lease folder: it keeps its own folder LEASE/tt1 and writes TT1_DONE / TT1_FAILED there).
#   bash drive_tt1_fs.sh HOST PORT LEASE stage   # rsync --partial --bwlimit of tt1_pack.tar to /workspace/tt1/packs (resumable)
#   bash drive_tt1_fs.sh HOST PORT LEASE start   # bin + nets_pins (16 FS1 tasks, from the verified local copies) ; start
#   bash drive_tt1_fs.sh HOST PORT LEASE pull    # fetch result tar + logs, verify, second local copy; TT1_DONE / TT1_FAILED
#   bash drive_tt1_fs.sh HOST PORT LEASE loop    # pull every 3 min (at most 3 h)
set -euo pipefail
HOST=${1:?}; PORT=${2:?}; L0=${3:?}; STEP=${4:?}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
L=$L0/tt1; mkdir -p "$L/results"
O=/mnt/t7/smad_next/TT1; FSR=/mnt/t7/smad_next/PN1/results_fs; B=/workspace/tt1
PSHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
FSHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_A_s407 PN1_B_s407 PN1_Sb_s407 PN1_A_s401"
SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L0/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=180 -e "ssh ${SO[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/tt1_fs_drive.log"; }
T=TT1_A100_pn1fs_fs
case "$STEP" in
  stage)
    R "mkdir -p $B/packs $B/bin $B/logs $B/results && df -h /workspace | tail -1" | tee -a "$L/tt1_fs_drive.log"
    RS --bwlimit=${TT1_BWLIMIT:-1000} "$O/tt1_pack.tar" "$O/tt1_pack.tar.sha256" "root@$HOST:$B/packs/"
    R "cd $B/packs && sha256sum -c tt1_pack.tar.sha256" | tee -a "$L/tt1_fs_drive.log"
    log "staged"
    ;;
  start)
    BIN=$L/bin; rm -rf "$BIN"; mkdir -p "$BIN"
    : > "$BIN/nets_pins.txt"
    for t in $TASKS; do
      [ -f "$FSR/$t.tar" ] && (cd "$FSR" && sha256sum -c --quiet "$t.tar.sha256") || { log "local FS1 copy of $t missing or unverified"; exit 1; }
      cut -c1-64 "$FSR/$t.tar.sha256" | sed "s|$|  $t.tar|" >> "$BIN/nets_pins.txt"
    done
    cp "$SRC/remote_tt1_fs.sh" "$SRC/../rescore_tf32.py" "$SRC/../gate_check_fs.py" "$BIN/"
    (cd "$BIN" && sha256sum remote_tt1_fs.sh rescore_tf32.py gate_check_fs.py nets_pins.txt > SHA256SUMS)
    RS "$BIN/" "root@$HOST:$B/bin/"
    msg=$(timeout 30 ssh "${SO[@]}" "root@$HOST" "cd $B && rm -f $B/DONE_FS && nohup setsid bash $B/bin/remote_tt1_fs.sh $PSHA $FSHA pn1fs > $B/logs/remote_fs.log 2>&1 < /dev/null & sleep 2; echo TT1FS_STARTED" || true)
    echo "$msg" | grep -q TT1FS_STARTED || { log "TT1FS_STARTED not seen"; exit 1; }
    log "started (waits for the FS1 queue lock on the host)"
    ;;
  pull)
    if ! R "test -f $B/DONE_FS" 2>/dev/null; then log "not done (or unreadable): $(R "tail -1 $B/workfs/res/$T/calls.log" 2>/dev/null || echo unreadable)"; exit 0; fi
    RS --include="$T.tar*" --include="logs_fs.sha256" --exclude='*' "root@$HOST:$B/results/" "$L/results/" || { log "fetch failed"; exit 0; }
    RS "root@$HOST:$B/logs/" "$L/results/logs/" || { log "log fetch failed"; exit 0; }
    (cd "$L/results" && sha256sum -c --quiet "$T.tar.sha256") || { log "tar sha256 mismatch"; exit 0; }
    (cd "$L/results/logs" && sha256sum -c --quiet ../logs_fs.sha256) || { log "log sha256 mismatch"; exit 0; }
    cp "$L/results/$T.tar" "$L/results/$T.tar.sha256" "$O/results/"
    (cd "$O/results" && sha256sum -c --quiet "$T.tar.sha256") || { log "second copy mismatch"; exit 0; }
    mkdir -p "$O/results/logs_$T" && cp -r "$L/results/logs/." "$O/results/logs_$T/"
    rc=$(tar -xOf "$L/results/$T.tar" "$T/rc" 2>/dev/null || echo unreadable)
    case "$rc" in
      0) touch "$L/TT1_DONE"; log "verified $T rc 0; two copies; TT1_DONE (the FS1 driver may release the host)" ;;
      FATAL*) echo "$rc" > "$L/TT1_FAILED"; touch "$L/TT1_DONE"; log "verified $T rc $rc; TT1_DONE + TT1_FAILED" ;;
      *) log "rc '$rc': no decision" ;;
    esac
    ;;
  loop)
    for k in $(seq 1 60); do bash "$0" "$HOST" "$PORT" "$L0" pull || true; [ -f "$L/TT1_DONE" ] && break; sleep 180; done
    ;;
esac

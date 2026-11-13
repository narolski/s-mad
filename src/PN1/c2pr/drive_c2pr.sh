#!/bin/bash
# Amendment C2P-R (draft), DGX-side driver for pn1fs (lease owned by the FS1 driver; this script never writes RELEASE:
# it keeps its own folder LEASE/c2pr and writes C2PR_DONE / C2PR_FAILED there; queue name for the lead's hold list: c2pr).
#   bash drive_c2pr.sh HOST PORT LEASE stage   # upload c2pr_pack.tar (561 MB, resumable), check sha256 on the host
#   bash drive_c2pr.sh HOST PORT LEASE start   # bin (remote_c2pr.sh, rescore.py, rescore_tf32.py, SHA256SUMS, nets_pins.txt); start
#   bash drive_c2pr.sh HOST PORT LEASE pull    # fetch C2P_fs.tar + logs, verify; 45 of 45 npz; second copy; C2PR_DONE
#   bash drive_c2pr.sh HOST PORT LEASE loop    # pull every 3 min (at most 3 h)
set -euo pipefail
HOST=${1:?}; PORT=${2:?}; L0=${3:?}; STEP=${4:?}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
L=$L0/c2pr; mkdir -p "$L/results"
O=/mnt/t7/smad_next/PN1/c2pr; FSR=/mnt/t7/smad_next/PN1/results_fs; COPY=/home/narolski/ms1_results_copy; B=${C2PR_RB:-/workspace/c2pr}
FSHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
CSHA=48e042a89ced7ca1c5a22601796c5830d55e161bfcdfb481e51349032380bf18
TASKS="PN1_A_s403 PN1_B_s403 PN1_Sb_s403 PN1_A_s404 PN1_B_s404 PN1_Sb_s404 PN1_A_s405 PN1_B_s405 PN1_Sb_s405 PN1_A_s406 PN1_B_s406 PN1_Sb_s406 PN1_A_s407 PN1_B_s407 PN1_Sb_s407"
SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L0/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=180 -e "ssh ${SO[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/c2pr_drive.log"; }
case "$STEP" in
  stage)
    [ "$(cut -c1-64 "$O/c2pr_pack.tar.sha256")" = "$CSHA" ] || { log "local pack sha differs from pin"; exit 1; }
    R "mkdir -p $B/packs $B/bin $B/logs $B/results && df -h /workspace | tail -1" | tee -a "$L/c2pr_drive.log"
    RS "$O/c2pr_pack.tar" "$O/c2pr_pack.tar.sha256" "root@$HOST:$B/packs/"
    R "cd $B/packs && sha256sum -c c2pr_pack.tar.sha256" | tee -a "$L/c2pr_drive.log"
    log "staged"
    ;;
  start)
    BIN=$L/bin; rm -rf "$BIN"; mkdir -p "$BIN"
    cp "$SRC/remote_c2pr.sh" /home/narolski/smad-next/src/PN1/rescore.py /home/narolski/smad-next/src/TT1/rescore_tf32.py "$BIN/"
    (cd "$FSR" && for t in $TASKS; do sha256sum -c --quiet "$t.tar.sha256" || exit 1; cut -c1-64 "$t.tar.sha256" | sed "s/\$/  $t.tar/"; done) > "$BIN/nets_pins.txt" \
      || { log "local FS1 tar not verified"; exit 1; }
    (cd "$BIN" && sha256sum remote_c2pr.sh rescore.py rescore_tf32.py nets_pins.txt > SHA256SUMS)
    RS "$BIN/" "root@$HOST:$B/bin/"
    msg=$(timeout 30 ssh "${SO[@]}" "root@$HOST" "cd $B && rm -f $B/DONE && nohup setsid bash $B/bin/remote_c2pr.sh $FSHA $CSHA > $B/logs/remote.log 2>&1 < /dev/null & sleep 2; echo C2PR_STARTED" || true)
    echo "$msg" | grep -q C2PR_STARTED || { log "C2PR_STARTED not seen"; exit 1; }
    log "started (waits for the FS1 queue lock on the host)"
    ;;
  pull)
    if ! R "test -f $B/DONE" 2>/dev/null; then log "not done (or unreadable): $(R "tail -1 $B/logs/calls.log" 2>/dev/null || echo unreadable)"; exit 0; fi
    RS --checksum --include="C2P_fs.tar*" --include="logs.sha256" --exclude='*' "root@$HOST:$B/results/" "$L/results/" || { log "fetch failed"; exit 0; }
    RS --checksum "root@$HOST:$B/logs/" "$L/results/logs/" || { log "log fetch failed"; exit 0; }
    (cd "$L/results" && sha256sum -c --quiet C2P_fs.tar.sha256) || { log "tar sha256 mismatch"; exit 0; }
    (cd "$L/results/logs" && sha256sum -c --quiet ../logs.sha256) || { log "log sha256 mismatch"; exit 0; }
    rc=$(tar -xOf "$L/results/C2P_fs.tar" out/rc 2>/dev/null || echo unreadable)
    n=$(tar -tf "$L/results/C2P_fs.tar" | grep -c '\.npz$' || true)
    cp "$L/results/C2P_fs.tar" "$L/results/C2P_fs.tar.sha256" "$O/" && cp "$L/results/C2P_fs.tar" "$L/results/C2P_fs.tar.sha256" "$COPY/"
    (cd "$O" && sha256sum -c --quiet C2P_fs.tar.sha256) && (cd "$COPY" && sha256sum -c --quiet C2P_fs.tar.sha256) || { log "copies not verified"; exit 0; }
    if [ "$rc" = 0 ] && [ "$n" -eq 45 ]; then touch "$L/C2PR_DONE"; log "verified C2P_fs.tar rc 0, 45 of 45 npz; two copies; C2PR_DONE"
    elif [ "${rc#FATAL}" != "$rc" ]; then echo "$rc ($n of 45 npz)" > "$L/C2PR_FAILED"; touch "$L/C2PR_DONE"; log "verified C2P_fs.tar rc '$rc' ($n of 45); C2PR_DONE + C2PR_FAILED"
    else log "rc '$rc', $n npz: no decision"; fi
    ;;
  loop)
    for k in $(seq 1 60); do bash "$0" "$HOST" "$PORT" "$L0" pull || true; [ -f "$L/C2PR_DONE" ] && break; sleep 180; done
    ;;
esac

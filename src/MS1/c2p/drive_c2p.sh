#!/bin/bash
# DRAFT, not run (contrast 2-prime). DGX side, one MS1 lease whose queue has ended and whose lease folder holds HOLD.
#   bash drive_c2p.sh HOST PORT LEASE Q upload   # the 15 FS1 result tars (about 65 MB) + sha256 list + remote_c2p.sh
#   bash drive_c2p.sh HOST PORT LEASE Q start    # detached remote run under the host lock
#   bash drive_c2p.sh HOST PORT LEASE Q pull     # fetch C2P_<Q>.tar, verify, second copy; then remove LEASE/HOLD so the
#                                                # MS1 pull loop writes RELEASE in its next round
set -euo pipefail
HOST=${1:?}; PORT=${2:?}; L=${3:?}; Q=${4:?}; STEP=${5:?}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${MS1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=c11b16bc7b76236bae80778f9e36cb67bb50de910f73a9dd200a706fc267fe7d
FS=/mnt/t7/smad_next/PN1/results_fs; OUTD=/mnt/t7/smad_next/MS1/c2p; COPY=/home/narolski/ms1_results_copy; B=/workspace/ms1
mkdir -p "$OUTD" "$COPY"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/c2p_drive.log"; }
T15=""; for a in A B Sb; do for s in 403 404 405 406 407; do T15="$T15 PN1_${a}_s$s"; done; done
case "$STEP" in
  upload)
    [ -f "$L/HOLD" ] || { log "no HOLD in the lease folder: refusing (the machine could be released mid-step)"; exit 1; }
    (cd "$FS" && sha256sum -c --quiet $(for t in $T15; do echo "$t.tar.sha256"; done)) || { log "local FS1 tars not verified"; exit 1; }
    (cd "$FS" && cat $(for t in $T15; do echo "$t.tar.sha256"; done)) > "$OUTD/fs1_tars.sha256"
    R "mkdir -p $B/fs1"
    RS $(for t in $T15; do echo "$FS/$t.tar"; done) "$OUTD/fs1_tars.sha256" "root@$HOST:$B/fs1/"
    RS "$SRC/remote_c2p.sh" "root@$HOST:$B/bin/"
    R "cd $B/fs1 && sha256sum -c --quiet fs1_tars.sha256 && echo C2P_UPLOAD_OK" | tee -a "$L/c2p_drive.log"
    ;;
  start)
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_c2p.sh $PIN $Q > $B/logs/c2p_driver_$Q.log 2>&1 < /dev/null & sleep 2; echo C2P_STARTED" || true)
    echo "$msg" | grep -q C2P_STARTED && log "c2p started" || { log "c2p start not confirmed"; exit 1; }
    ;;
  pull)
    st=$(R "[ -f $B/C2P_DONE_$Q ] && echo DONE || echo RUNNING" 2>/dev/null || echo UNKNOWN)
    [ "$st" = DONE ] || { log "remote $st"; exit 0; }
    RS "root@$HOST:$B/root/results/C2P_$Q.tar" "root@$HOST:$B/root/results/C2P_$Q.tar.sha256" "root@$HOST:$B/logs/c2p_$Q.log" "$OUTD/"
    (cd "$OUTD" && sha256sum -c --quiet "C2P_$Q.tar.sha256") || { log "C2P tar not verified"; exit 0; }
    n=$(tar tf "$OUTD/C2P_$Q.tar" | grep -c '\.npz$'); [ "$n" -eq 45 ] || log "C2P tar holds $n of 45 npz (failures in c2p_$Q.log)"
    cp "$OUTD/C2P_$Q.tar" "$OUTD/C2P_$Q.tar.sha256" "$COPY/" && (cd "$COPY" && sha256sum -c --quiet "C2P_$Q.tar.sha256")
    rm -f "$L/HOLD"; log "C2P kept ($n npz); HOLD removed: the MS1 loop may now write RELEASE"
    ;;
esac

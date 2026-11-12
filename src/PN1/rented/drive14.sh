#!/bin/bash
# PN1 amendment 14, DGX-side driver for one rented lease (no rental API; SSH key by path only, never printed).
#   bash drive14.sh HOST PORT LEASE start   # upload pn1_a14.tar, rescore.py, remote_a14.sh; start detached
#   bash drive14.sh HOST PORT LEASE pull    # copy PN1_A14.tar back, verify; RELEASE when verified
# Pull loop: for k in $(seq 1 30); do bash drive14.sh HOST PORT LEASE pull; [ -f LEASE/RELEASE ] && break; sleep 300; done
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease folder}; STEP=${4:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=bda5fd3d5043ad72e08e9c7aeee88ba42181dd2daf68af5a9674406a8a73ef72
P=/mnt/t7/smad_next/PN1; OUTD=$P/results_a14; B=/workspace/pn1
mkdir -p "$L" "$OUTD"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/pn1_a14_drive.log"; }
case "$STEP" in
  start)
    [ "$(cut -c1-64 "$P/pn1_a14.tar.sha256")" = "$PIN" ] || { log "local pack sha file differs from pin"; exit 1; }
    R "mkdir -p $B/root/packs/PN1 $B/root/results/PN1 $B/bin $B/logs $B/rc && nvidia-smi -L && df -h /workspace | tail -1" | tee -a "$L/pn1_a14_drive.log"
    RS "$P/pn1_a14.tar" "$P/pn1_a14.tar.sha256" "root@$HOST:$B/root/packs/PN1/"
    RS "$SRC/../rescore.py" "$SRC/remote_a14.sh" "root@$HOST:$B/bin/"
    timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_a14.sh $PIN > $B/logs/a14_driver.log 2>&1 < /dev/null & sleep 2; echo A14_STARTED" || true
    log "a14 uploaded and started"
    ;;
  pull)
    RS --include='PN1_A14.tar*' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs/" || true
    if [ -f "$OUTD/PN1_A14.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet PN1_A14.tar.sha256); then
      log "verified PN1_A14"; touch "$L/RELEASE"; log "RELEASE written"
    else
      log "not yet"; R "cat $B/rc/PN1_A14 2>/dev/null; tail -1 $B/logs/PN1_A14.log 2>/dev/null" || true
    fi
    ;;
esac

#!/bin/bash
# PN1 amendment 14, DGX-side driver for one rented lease (no rental API; SSH key by path only, never printed).
#   bash drive14.sh HOST PORT LEASE start full|reduced   # upload pack, rescore.py, remote_a14.sh; start detached
#   bash drive14.sh HOST PORT LEASE pull                  # copy PN1_A14.tar back, verify; RELEASE (+ FAILED) when verified
#   bash drive14.sh HOST PORT LEASE loop                  # pull every 5 min until RELEASE (at most 2.5 h)
# Guard values registered with amendment 14 (the lead's guard): cap 1.5 USD, deadline lease start + 2.5 h.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease folder}; STEP=${4:?step}; VAR=${5:-}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
P=/mnt/t7/smad_next/PN1; OUTD=$P/results_a14; B=/workspace/pn1
mkdir -p "$L" "$OUTD"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
log() { echo "$(date +%T) $*" | tee -a "$L/pn1_a14_drive.log"; }
case "$STEP" in
  start)
    case "$VAR" in
      full) PK=pn1_a14.tar; PIN=bda5fd3d5043ad72e08e9c7aeee88ba42181dd2daf68af5a9674406a8a73ef72 ;;
      reduced) PK=pn1_a14r.tar; PIN=efa700a9dc2e85d6a605722990511adcf6920ec3f1e9ef86519cf7edf3aac216 ;;
      *) log "variant must be full or reduced"; exit 1 ;;
    esac
    [ "$(cut -c1-64 "$P/$PK.sha256")" = "$PIN" ] || { log "local pack sha file differs from pin"; exit 1; }
    R "mkdir -p $B/root/packs/PN1 $B/root/results/PN1 $B/bin $B/logs $B/rc && nvidia-smi -L && df -h /workspace | tail -1" | tee -a "$L/pn1_a14_drive.log"
    RS "$P/$PK" "$P/$PK.sha256" "root@$HOST:$B/root/packs/PN1/"
    RS "$SRC/../rescore.py" "$SRC/remote_a14.sh" "root@$HOST:$B/bin/"
    msg=$(timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_a14.sh $PIN $VAR > $B/logs/a14_driver.log 2>&1 < /dev/null & sleep 2; echo A14_STARTED" || true)
    echo "$msg" | grep -q A14_STARTED || { log "A14_STARTED not seen: remote start failed"; exit 1; }
    log "a14 ($VAR) uploaded and started"
    ;;
  pull)
    RS --include='PN1_A14.tar*' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs/" || true
    if [ -f "$OUTD/PN1_A14.tar" ] && [ -f "$OUTD/PN1_A14.tar.sha256" ] && (cd "$OUTD" && sha256sum -c --quiet PN1_A14.tar.sha256); then
      rc=$(tar -xOf "$OUTD/PN1_A14.tar" PN1_A14/rc 2>/dev/null || echo "rc missing")
      if [ "$rc" = "0" ]; then log "verified PN1_A14 (rc 0)"
      else echo "$rc" > "$L/FAILED"; log "verified PN1_A14 with failures: $(echo $rc | tr '\n' ';')"; fi
      touch "$L/RELEASE"; log "RELEASE written"
    else
      log "not yet"; R "tail -2 $B/work/a14/res/PN1_A14/calls.log 2>/dev/null" || true
    fi
    ;;
  loop)
    for k in $(seq 1 30); do bash "$0" "$HOST" "$PORT" "$L" pull || true; [ -f "$L/RELEASE" ] && break; sleep 300; done
    ;;
esac

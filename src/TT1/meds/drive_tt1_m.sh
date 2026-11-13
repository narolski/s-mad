#!/bin/bash
# TT1 MEDS extension driver for se1d (lease held by the lead for the SE1 owner; this driver never writes RELEASE).
#   bash drive_tt1_m.sh stage   # rsync --partial, one stream, into /workspace/tt1m/packs (no GPU use)
#   bash drive_tt1_m.sh start   # only if /mnt/t7/smad_next/vast/se1d/SE1_DONE_411 exists: bin upload + remote start
#   bash drive_tt1_m.sh pull    # fetch + verify result tar and logs, second copy in /mnt/t7/smad_next/TT1/results; TT1M_DONE
#   bash drive_tt1_m.sh loop
set -euo pipefail
STEP=${1:?}
HOST=185.130.165.20; PORT=26693; L0=/mnt/t7/smad_next/vast/se1d; L=$L0/tt1m; mkdir -p "$L/results"
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
O=/mnt/t7/smad_next/TT1; B=/workspace/tt1m; T=TT1M_se1d; SRC=$(cd "$(dirname "$0")" && pwd)
PSHA=2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554
MSHA=3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61
NSHA=b5c4dd6ec16b6cc104093a8a828627e4b00d19814270fb81580d9918ed5d5030
SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L0/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=180 -e "ssh ${SO[*]}" "$@"; }
log() { echo "$(date +%T) [tt1m] $*" | tee -a "$L/tt1m_drive.log"; }
case "$STEP" in
  stage)
    R "mkdir -p $B/packs $B/bin $B/logs $B/results && df -h /workspace | tail -1" | tee -a "$L/tt1m_drive.log"
    RS "$O/meds/tt1m_nets.tar" "$O/meds/tt1m_nets.tar.sha256" "$O/meds/tt1m_meds.tar" "$O/meds/tt1m_meds.tar.sha256" "root@$HOST:$B/packs/"
    RS "$O/tt1_pack.tar" "$O/tt1_pack.tar.sha256" "root@$HOST:$B/packs/"
    R "cd $B/packs && sha256sum -c tt1_pack.tar.sha256 tt1m_meds.tar.sha256 tt1m_nets.tar.sha256" | tee -a "$L/tt1m_drive.log"
    log "staged"
    ;;
  start)
    [ -f "$L0/SE1_DONE_411" ] || { log "SE1_DONE_411 missing: not starting"; exit 1; }
    R "pgrep -f remote_tt1_m.sh >/dev/null" && { log "a TT1-M job is already running on the host: not starting a second"; exit 1; }
    busy=$(R "nvidia-smi --query-compute-apps=pid --format=csv,noheader" 2>/dev/null | grep -v -i "welcome\|fun" || true)
    [ -z "$busy" ] || { log "GPU busy (another owner's process): not starting"; exit 1; }
    BIN=$L/bin; rm -rf "$BIN"; mkdir -p "$BIN"; cp "$SRC/remote_tt1_m.sh" "$SRC/gate_check_m.py" "$BIN/"
    (cd "$BIN" && sha256sum remote_tt1_m.sh gate_check_m.py > SHA256SUMS)
    RS "$BIN/" "root@$HOST:$B/bin/"
    msg=$(timeout 30 ssh "${SO[@]}" "root@$HOST" "cd $B && rm -f $B/DONE_M && nohup setsid bash $B/bin/remote_tt1_m.sh $PSHA $MSHA $NSHA > $B/logs/remote_m.log 2>&1 < /dev/null & sleep 2; echo TT1M_STARTED" || true)
    echo "$msg" | grep -q TT1M_STARTED || { log "TT1M_STARTED not seen"; exit 1; }
    log "started"
    ;;
  pull)
    if ! R "test -f $B/DONE_M" 2>/dev/null; then log "not done (or unreadable): $(R "tail -1 $B/work/res/$T/calls.log" 2>/dev/null || echo unreadable)"; exit 0; fi
    D=$L/results
    RS --include="$T.tar*" --include="logs_m.sha256" --exclude='*' "root@$HOST:$B/results/" "$D/" || { log "fetch failed"; exit 0; }
    RS "root@$HOST:$B/logs/" "$D/logs/" || { log "log fetch failed"; exit 0; }
    (cd "$D" && sha256sum -c --quiet "$T.tar.sha256") || { log "tar sha256 mismatch"; exit 0; }
    (cd "$D/logs" && sha256sum -c --quiet ../logs_m.sha256) || { log "log sha256 mismatch"; exit 0; }
    cp "$D/$T.tar" "$D/$T.tar.sha256" "$O/results/"; (cd "$O/results" && sha256sum -c --quiet "$T.tar.sha256") || { log "second copy mismatch"; exit 0; }
    mkdir -p "$O/results/logs_$T" && cp -r "$D/logs/." "$O/results/logs_$T/"
    rc=$(tar -xOf "$D/$T.tar" "$T/rc" 2>/dev/null || echo unreadable)
    case "$rc" in
      0) touch "$L/TT1M_DONE"; log "verified rc 0; two copies; TT1M_DONE" ;;
      FATAL*) echo "$rc" > "$L/TT1M_FAILED"; touch "$L/TT1M_DONE"; log "verified rc $rc; TT1M_DONE + FAILED" ;;
      *) log "rc '$rc': no decision" ;;
    esac
    ;;
  loop) for k in $(seq 1 60); do bash "$0" pull || true; [ -f "$L/TT1M_DONE" ] && break; sleep 120; done ;;
esac

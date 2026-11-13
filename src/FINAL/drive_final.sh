#!/bin/bash
# Sealed MAD22 read (FINAL) driver. The lead rents one fresh A100-PCIE-40GB and writes the lease folder
# /mnt/t7/smad_next/vast/<LEASE>/lease.json (ssh_host, ssh_port, as every lease). This driver never rents, never
# releases, and never opens a score.
#   bash drive_final.sh stage   LEASE  upload pack + bin (rsync --partial), verify sha256 on the host (no GPU use)
#   bash drive_final.sh dryrun  LEASE  the GATE DRY RUN (development rows only; remote FINAL_DRYRUN=1), once per lease
#   bash drive_final.sh pulldry LEASE  fetch + verify the dry-run tar; DRYRUN_PASSED if rc 0 (all five byte-identical)
#   bash drive_final.sh start   LEASE  THE READ, once: needs DRYRUN_PASSED on this lease; refuses if the local start
#                                      lock exists (any lease) or the host has STARTED; creates the lock atomically
#   bash drive_final.sh pull    LEASE  fetch result tar + logs, verify sha256, second copy; prints rc and gate line only
#   bash drive_final.sh loop    LEASE  pull every 2 min until FINAL_DONE (at most 2 h); loopdry likewise for the dry run
# Test mode (FINAL_TEST=1): the "host" is this machine (bash -c), lock and outputs under FINAL_TEST_ROOT; never used for
# the read.
set -euo pipefail
STEP=${1:?}; LEASE=${2:?}
SRC=$(cd "$(dirname "$0")" && pwd)
CFG=${FINAL_CONFIG:-$SRC/final_config.json}
RID=$(python3 -c "import json; print(json.load(open('$CFG'))['read_id'])")
O=${FINAL_TEST_ROOT:-/mnt/t7/smad_next/FINAL}
L0=${FINAL_LEASE_DIR:-/mnt/t7/smad_next/vast/$LEASE}; L=$L0/final; mkdir -p "$L/results"
LOCK=$O/START_LOCK_$RID                      # one start of the read for this read_id, whatever the lease
PACK=$O/${RID}_pack.tar
PSHA=$(cut -c1-64 "$PACK.sha256")
CSHA=$(sha256sum < "$CFG" | cut -c1-64)
B=${FINAL_B:-/workspace/final}
log() { echo "$(date +%FT%T) [final] $*" | tee -a "$L/final_drive.log"; }
if [ "${FINAL_TEST:-0}" = 1 ]; then
  R() { bash -c "$*"; }
  RS() { rsync -a "$@"; }
  HOSTP=""
else
  KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
  HOST=$(python3 -c "import json; print(json.load(open('$L0/lease.json'))['ssh_host'])")
  PORT=$(python3 -c "import json; print(json.load(open('$L0/lease.json'))['ssh_port'])")
  SO=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L0/known_hosts" -i "$KEY" -p "$PORT")
  R() { ssh "${SO[@]}" "root@$HOST" "$@"; }
  RS() { rsync -a --partial --timeout=180 -e "ssh ${SO[*]}" "$@"; }
  HOSTP="root@$HOST:"
fi
remote_start() {   # $1 = extra env for the remote (FINAL_DRYRUN=1 or empty); prints FINAL_STARTED on success
  local ENVX=$1
  local RCMD="cd $B || exit 1; $ENVX nohup setsid bash $B/bin/remote_final.sh $PSHA $CSHA $LEASE > $B/logs/remote${ENVX:+_dryrun}.log 2>&1 < /dev/null & sleep 2; echo FINAL_STARTED"
  if [ "${FINAL_TEST:-0}" = 1 ]; then
    FINAL_TEST=1 FINAL_SKIP_VENV=${FINAL_SKIP_VENV:-0} FINAL_PY=${FINAL_PY:-python} FINAL_B=$B timeout 30 bash -c "$RCMD" || true
  else
    timeout 30 ssh "${SO[@]}" "root@$HOST" "$RCMD" || true
  fi
}
host_pins() { R "cd $B/packs && sha256sum -c --quiet ${RID}_pack.tar.sha256 && cd $B/bin && sha256sum -c --quiet SHA256SUMS"; }
fetch() {          # $1 = tar stem, $2 = logs sha file, $3 = DONE file name; echoes rc
  local T=$1 LS=$2 DF=$3 D=$L/results
  R "test -f $B/$DF" 2>/dev/null || { echo "NOTDONE"; return 0; }
  RS --include="$T.tar*" --include="$LS" --exclude='*' "${HOSTP}$B/results/" "$D/" || { echo "FETCHFAIL"; return 0; }
  RS "${HOSTP}$B/logs/" "$D/logs/" || { echo "FETCHFAIL"; return 0; }
  (cd "$D" && sha256sum -c --quiet "$T.tar.sha256") || { echo "SHAFAIL"; return 0; }
  (cd "$D/logs" && sha256sum -c --quiet "../$LS") || { echo "LOGSHAFAIL"; return 0; }
  mkdir -p "$O/results"; cp "$D/$T.tar" "$D/$T.tar.sha256" "$O/results/"
  (cd "$O/results" && sha256sum -c --quiet "$T.tar.sha256") || { echo "COPYFAIL"; return 0; }
  mkdir -p "$O/results/logs_$T" && cp -r "$D/logs/." "$O/results/logs_$T/"
  tar -xOf "$D/$T.tar" "$T/rc" 2>/dev/null || echo unreadable
}
case "$STEP" in
  stage)
    [ -e "$LOCK" ] && { log "start lock exists ($LOCK): the read has been started once; not staging"; exit 1; }
    (cd "$O" && sha256sum -c --quiet "${RID}_pack.tar.sha256") || { log "local pack sha256 mismatch"; exit 1; }
    BIN=$L/bin; rm -rf "$BIN"; mkdir -p "$BIN"
    cp "$SRC/remote_final.sh" "$SRC/gate_check_final.py" "$BIN/" && cp "$CFG" "$BIN/final_config.json"
    (cd "$BIN" && sha256sum remote_final.sh gate_check_final.py final_config.json > SHA256SUMS)
    R "mkdir -p $B/packs $B/bin $B/logs $B/results && df -h $B | tail -1" | tee -a "$L/final_drive.log"
    t0=$(date +%s)
    RS "$PACK" "$PACK.sha256" "${HOSTP}$B/packs/"
    RS "$BIN/" "${HOSTP}$B/bin/"
    log "upload $(( $(date +%s) - t0 )) s"
    R "cd $B/packs && sha256sum -c ${RID}_pack.tar.sha256 && cd $B/bin && sha256sum -c SHA256SUMS" | tee -a "$L/final_drive.log"
    log "staged"
    ;;
  dryrun)
    host_pins || { log "host pins not verified: no dry run"; exit 1; }
    mkdir "$L/DRYRUN_LOCK" 2>/dev/null || { log "the dry run was started once for this lease"; exit 1; }
    R "test -e $B/STARTED_DRYRUN" && { log "the dry run was started once on this host"; exit 1; }
    R "test -e $B/STARTED" && { log "the read was started on this host: no dry run"; exit 1; }
    remote_start "FINAL_DRYRUN=1" | grep -q FINAL_STARTED || { log "dry run: FINAL_STARTED not seen"; exit 1; }
    log "dry run started on $LEASE (development rows only)"
    ;;
  pulldry)
    rc=$(fetch "${RID}_${LEASE}_dryrun" logs_dryrun.sha256 DONE_DRYRUN)
    case "$rc" in
      NOTDONE) log "dry run not done: $(R "tail -1 $B/work/res/${RID}_${LEASE}_dryrun/calls.log" 2>/dev/null | cut -c1-200 || echo unreadable)" ;;
      0) touch "$L/DRYRUN_PASSED"; log "dry run verified rc 0: gate passed on this lease; DRYRUN_PASSED; $(tar -xOf "$L/results/${RID}_${LEASE}_dryrun.tar" "${RID}_${LEASE}_dryrun/gate.txt" | head -1)" ;;
      *) echo "$rc" > "$L/DRYRUN_FAILED"; log "dry run rc '$rc': the read is NOT started on this lease; report to the lead" ;;
    esac
    ;;
  start)
    [ -f "$L/DRYRUN_PASSED" ] || { log "no DRYRUN_PASSED for this lease: not starting the read"; exit 1; }
    host_pins || { log "host pins not verified: not starting"; exit 1; }
    R "test -e $B/STARTED" && { log "host has STARTED: not starting a second time"; exit 1; }
    busy=$(R "nvidia-smi --query-compute-apps=pid --format=csv,noheader" 2>/dev/null || true)
    [ "${FINAL_TEST:-0}" = 1 ] || [ -z "$busy" ] || { log "GPU busy: not starting"; exit 1; }
    # the one-start lock: mkdir is atomic; no script removes it
    mkdir "$LOCK" 2>/dev/null || { log "start lock $LOCK exists: the read was started once; a second start is impossible"; exit 1; }
    echo "$(date +%FT%T) lease $LEASE pack $PSHA config $CSHA" > "$LOCK/started"
    remote_start "" | grep -q FINAL_STARTED || { log "FINAL_STARTED not seen (lock kept; report to the lead, do not retry)"; exit 1; }
    log "started the read on $LEASE"
    ;;
  pull)
    T=${RID}_${LEASE}
    rc=$(fetch "$T" logs_final.sha256 DONE)
    case "$rc" in
      NOTDONE) log "not done: $(R "tail -1 $B/work/res/$T/calls.log" 2>/dev/null | cut -c1-200 || echo unreadable)" ;;
      0) touch "$L/FINAL_DONE"; log "verified rc 0; two copies ($L/results, $O/results); gate: $(tar -xOf "$L/results/$T.tar" "$T/gate.txt" | head -1); FINAL_DONE" ;;
      FATAL*) echo "$rc" > "$L/FINAL_FAILED"; touch "$L/FINAL_DONE"; log "verified rc '$rc'; FINAL_DONE + FAILED (report to the lead; no re-run without his word)" ;;
      *) log "rc '$rc': no decision" ;;
    esac
    ;;
  loop) for k in $(seq 1 60); do bash "$0" pull "$LEASE" || true; [ -f "$L/FINAL_DONE" ] && break; sleep 120; done ;;
  loopdry) for k in $(seq 1 60); do bash "$0" pulldry "$LEASE" || true; { [ -f "$L/DRYRUN_PASSED" ] || [ -f "$L/DRYRUN_FAILED" ]; } && break; sleep 60; done ;;
  *) echo "unknown step"; exit 2 ;;
esac

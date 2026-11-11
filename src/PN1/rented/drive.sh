#!/bin/bash
# PN1 rented A100, DGX-side driver (no rental API here; the SSH key is used by path only and never printed or copied).
#   bash drive.sh HOST PORT LEASE setup    # upload packs (pinned pack + reference tar), tasks, scripts; pip pins; versions
#   bash drive.sh HOST PORT LEASE smoke    # 200-step smoke fit on arm Bn (unchanged run.sh); speed, peak memory, rc
#   bash drive.sh HOST PORT LEASE queue    # start the remote queue (eight fits, then the reference row), detached
#   bash drive.sh HOST PORT LEASE pull     # copy finished tars + logs back, verify sha256; RELEASE when all 9 verified
#   bash drive.sh HOST PORT LEASE status
# LEASE = the lead's lease folder (known_hosts and logs go there; RELEASE is written there).
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease folder}; STEP=${4:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN=5c6427907d92514ed284881fcf859f92a4294da74e03ada46226fdd7b0dd2676
P=/mnt/t7/smad_next/PN1
OUTD=$P/results_rented
mkdir -p "$L"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
B=/workspace/pn1
QT=${PN1_TASKS:?PN1_TASKS}; DO_REF=${PN1_DO_REF:-0}   # amendment 7
TASKS="PN1_A_s401 PN1_B_s401 PN1_Bn_s401 PN1_C_s401 PN1_A_s402 PN1_B_s402 PN1_Bn_s402 PN1_C_s402"
log() { echo "$(date +%T) $*" | tee -a "$L/pn1_drive.log"; }
case "$STEP" in
  setup)
    [ "$(cut -c1-64 "$P/pn1_pack.tar.sha256")" = "$PIN" ] || { log "local pack sha file differs from pin"; exit 1; }
    [ -f "$P/refnets.tar" ] || { log "refnets.tar missing locally (python3 -I build_refnets.py)"; exit 1; }
    R "mkdir -p $B/root/packs/PN1 $B/root/results/PN1 $B/tasks $B/bin $B/logs $B/tmp && nvidia-smi -L && nproc && df -h /workspace | tail -1" | tee -a "$L/pn1_setup.log"
    T0=$SECONDS
    RS "$P/pn1_pack.tar" "$P/pn1_pack.tar.sha256" "$P/refnets.tar" "$P/refnets.tar.sha256" "root@$HOST:$B/root/packs/PN1/"
    log "pack and reference tar upload $((SECONDS - T0)) s"
    RS "$SRC/remote_setup.sh" "$SRC/remote_smoke.sh" "$SRC/remote_queue.sh" "$SRC/score_ref_local.sh" "root@$HOST:$B/bin/"
    for t in $TASKS; do RS "$P/athena_tasks/$t" "root@$HOST:$B/tasks/"; done
    R "sha256sum $B/tasks/*/run.sh | cut -c1-16 | sort | uniq -c; cat $B/tasks/PN1_C_s402/task.env"
    R "bash $B/bin/remote_setup.sh $PIN" 2>&1 | tee -a "$L/pn1_setup.log"
    grep -q SETUP_OK "$L/pn1_setup.log" && log "SETUP_OK"
    ;;
  smoke)
    R "bash $B/bin/remote_smoke.sh" 2>&1 | tee "$L/pn1_smoke.txt"
    RS "root@$HOST:$B/smoke/smoke_run.log" "root@$HOST:$B/smoke/gpumem.csv" "$L/" || true
    grep -q "SMOKE_RC=0" "$L/pn1_smoke.txt" && log "SMOKE passed" || { log "SMOKE failed"; exit 1; }
    ;;
  queue)
    R "cd $B && nohup setsid bash $B/bin/remote_queue.sh \"$QT\" $DO_REF > $B/logs/queue_driver.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_STARTED"
    log "queue started"
    ;;
  pull)
    df -h /mnt/t7 | tail -1 | tee -a "$L/pn1_drive.log"
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 2 ] || { log "T7 has under 2 GB free: not pulling"; exit 1; }
    mkdir -p "$OUTD/logs"
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/root/results/PN1/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs/" || true
    RS "root@$HOST:$B/queue.log" "root@$HOST:$B/rc" "$OUTD/logs/" 2>/dev/null || true
    n=0
    WANT="$QT"; [ "$DO_REF" = 1 ] && WANT="$WANT PN1_REF_smdd_m3"
    Q2=$(R "ls -d $B/tasks/PN1_Sb_s* $B/tasks/PN1_Bv_s* 2>/dev/null | xargs -n1 basename 2>/dev/null" 2>/dev/null | grep PN1_ || true)
    WANT="$WANT $Q2"; NW=$(echo $WANT | wc -w)   # amendment 10: a second queue, if armed, must finish before RELEASE
    for t in $WANT; do
      if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ]; then
        (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256") && { n=$((n + 1)); echo "verified $t"; } || log "HASH MISMATCH $t"
      fi
    done
    log "verified $n of $NW"
    if [ "$n" -eq "$NW" ]; then touch "$L/RELEASE"; log "RELEASE written"; fi
    ;;
  status)
    R "cat $B/queue.log 2>/dev/null; ls $B/root/results/PN1/; tail -2 $B/logs/*.log 2>/dev/null | tail -12; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
  *) echo "step $STEP"; exit 1 ;;
esac

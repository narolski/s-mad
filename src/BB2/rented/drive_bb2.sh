#!/bin/bash
# BB2 rented variant, DGX-side driver for one lease (no rental API; SSH key by path only, never printed).
#   bash drive_bb2.sh HOST PORT LEASE Q upload   # pack 8.75 GB + overlay 1.2 GB + scripts -> /workspace/bb2/root/packs/BB2
#   bash drive_bb2.sh HOST PORT LEASE Q setup    # remote pins, pip pins, versions -> LEASE/setup.log
#   bash drive_bb2.sh HOST PORT LEASE Q smoke    # detached; read LEASE/smoke.txt with `status` (memory and batch rules)
#   bash drive_bb2.sh HOST PORT LEASE Q queue BS ACCUM   # start queue Q's fits detached (BS/ACCUM from the rule)
#   bash drive_bb2.sh HOST PORT LEASE Q pull     # fetch tars + logs, verify sha256 against remote; RELEASE when kept
#   bash drive_bb2.sh HOST PORT LEASE Q status
# Q (seeds whole on one machine): all = 403, 404, 405 | s403 | s404 | s405 | s403s405 | ...
# Keep rule (OWNER_BRIEF 12 Nov): RELEASE only when every task of Q has its tar locally with a sha256 equal to the
# remote one (trained weights last_trainable.pt are inside), and every remote log file is copied and hash-verified.
# A failed task counts as done only when the remote confirms it (rc file non-zero after its rerun, no tar). An
# unreachable host never leads to a decision.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease}; Q=${4:?queue}; STEP=${5:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${BB2_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
STAGE=/mnt/t7/smad_next/BB2/wcss_stage           # pack, overlay, run.sh, featcheck + .sha256 (same files as WCSS)
OUTD=/mnt/t7/smad_next/BB2/results; B=/workspace/bb2
TASKS=""
for s in $(echo "$Q" | sed 's/all/s403s404s405/; s/s/ /g'); do TASKS="$TASKS BB2_A_s$s BB2_B_s$s BB2_Sb_s$s"; done
mkdir -p "$L" "$OUTD/logs_$Q"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
case "$STEP" in
  upload)
    R "mkdir -p $B/root/packs/BB2"
    RS -L "$STAGE/pn1_pack_fs.tar" "$STAGE/pn1_pack_fs.tar.sha256" "$STAGE/bb2_overlay.tar" "$STAGE/bb2_overlay.tar.sha256" \
      "$STAGE/run.sh" "$STAGE/run.sh.sha256" "$STAGE/featcheck.py" "$STAGE/featref_cpu.npz" "$SRC/remote_bb2.sh" \
      "root@$HOST:$B/root/packs/BB2/" 2>&1 | tee -a "$L/upload.log"
    echo "UPLOAD_OK $(date -Is)" | tee -a "$L/upload.log" ;;
  setup) R "bash $B/root/packs/BB2/remote_bb2.sh setup" 2>&1 | tee "$L/setup.log" ;;
  smoke) R "cd /workspace && nohup setsid bash $B/root/packs/BB2/remote_bb2.sh smoke > /workspace/bb2_smoke.out 2>&1 < /dev/null &"; echo started ;;
  queue)
    BS=${6:?bs}; AC=${7:?accum}
    case "$BS/$AC" in 256/1|128/2) ;; *) echo "refuse batch $BS/$AC"; exit 1 ;; esac
    echo "$TASKS" > "$L/TASKS"
    R "cd /workspace && nohup setsid bash $B/root/packs/BB2/remote_bb2.sh queue $BS $AC '$TASKS' > /workspace/bb2_queue.out 2>&1 < /dev/null &"
    echo "queue $Q started $(date -Is): $TASKS bs $BS accum $AC" | tee -a "$L/queue_local.log" ;;
  status)
    R "cat $B/logs/smoke.txt 2>/dev/null; cat $B/queue.log 2>/dev/null; ls $B/root/results/BB2 2>/dev/null; ls $B/ALL_DONE 2>/dev/null; nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader" ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' '); [ "$avail" -ge 20 ] || { echo "T7 under 20 GB free: no pull"; exit 1; }
    RS "root@$HOST:$B/root/results/BB2/" "$OUTD/" || { echo "unreachable: no decision"; exit 1; }
    RS "root@$HOST:$B/logs/" "$OUTD/logs_$Q/" && RS "root@$HOST:$B/rc/" "$OUTD/logs_$Q/rc/" && RS "root@$HOST:$B/rerun/" "$OUTD/logs_$Q/rerun/" || { echo "unreachable: no decision"; exit 1; }
    RS "root@$HOST:$B/queue.log" "$OUTD/logs_$Q/" 2>/dev/null || true
    ok=1; done_n=0
    for T in $TASKS; do
      if [ -f "$OUTD/$T.tar" ] && [ -f "$OUTD/$T.tar.sha256" ]; then
        l=$(sha256sum "$OUTD/$T.tar" | cut -c1-64); r=$(R "sha256sum $B/root/results/BB2/$T.tar | cut -c1-64") || { echo "unreachable"; exit 1; }
        [ "$l" = "$r" ] && [ "$l" = "$(cut -c1-64 "$OUTD/$T.tar.sha256")" ] && { done_n=$((done_n+1)); continue; }
        echo "$T hash mismatch"; ok=0
      elif [ -f "$OUTD/logs_$Q/rc/$T" ] && [ "$(cat "$OUTD/logs_$Q/rc/$T")" != 0 ] && R "test -f $B/ALL_DONE"; then
        echo "$T failed (remote confirmed)"; touch "$L/FAILED"; done_n=$((done_n+1))
      else ok=0; fi
    done
    (R "cd $B/logs && sha256sum *") > "$L/remote_logs.sha256" || { echo "unreachable"; exit 1; }
    (cd "$OUTD/logs_$Q" && sha256sum -c --quiet "$L/remote_logs.sha256") || ok=0
    sha256sum "$OUTD"/BB2_*.tar > "$L/kept_tars.sha256" 2>/dev/null || true
    echo "$(date +%T) verified $done_n of $(echo $TASKS | wc -w)"
    if [ $ok = 1 ] && [ $done_n = $(echo $TASKS | wc -w) ] && R "test -f $B/ALL_DONE"; then touch "$L/RELEASE"; echo RELEASE; fi ;;
  *) echo "step upload|setup|smoke|queue|status|pull"; exit 1 ;;
esac

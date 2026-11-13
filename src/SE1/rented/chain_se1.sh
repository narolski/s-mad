#!/bin/bash
# SE1 rented A100 route: one lease = one whole seed (arms A, Sb, SE). Runs on the DGX, detached, one per lease:
#   bash chain_se1.sh HOST PORT NAME SEED
# Steps: (packs + setup are started separately by drive_se1.sh) -> check -> smoke with the platform reproduction check
# (waits for its end; the queue starts only if the smoke log has "smoke rc 0") -> the seed's 3 fits -> pull every 10 min
# until ALL_DONE and the 3 fit tars + smoke/platform tars are verified in two copies (/mnt/t7/smad_next/SE1/results and
# /home/narolski/se1_results_copy) and the logs are fetched -> RELEASE in the lease folder. Never RELEASE on unreadable state.
set -u
HOST=$1; PORT=$2; NAME=$3; SEED=$4
D=$(cd "$(dirname "$0")" && pwd); LEASE=/mnt/t7/smad_next/vast/$NAME; P=/mnt/t7/smad_next/SE1; S=$P/rented_$NAME
DR() { bash "$D/drive_se1.sh" "$HOST" "$PORT" "$NAME" none "$@"; }
log() { echo "$(date +%T) chain $*" | tee -a "$S/drive.log"; }
O=(-o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile=$LEASE/known_hosts -i /home/narolski/.config/smad-next/vast_ssh_key -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@" 2>/dev/null; }
mkdir -p "$S"
until grep -q SE1_SETUP_OK "$S/setup.log" 2>/dev/null; do sleep 30; done
DR check | grep -q SE1_CHECK_OK || { log "check failed"; exit 1; }
R "test -f /workspace/se1/SMOKE_DONE" || DR smoke || { log "smoke launch failed"; exit 1; }
until R "test -f /workspace/se1/SMOKE_DONE"; do sleep 60; done
R "grep -q 'smoke rc 0' /workspace/se1/queue.log" || { log "SMOKE FAILED on $NAME: no fits"; exit 1; }
log "smoke passed"
DR pull
R "test -f /workspace/se1/QUEUE_STARTED_$SEED" || DR queue "$SEED" || { log "queue launch failed"; exit 1; }
log "queue $SEED started"
for k in $(seq 1 60); do
  sleep 600
  DR pull || continue
  st=$(R "[ -f /workspace/se1/ALL_DONE_$SEED ] && echo ENDED || echo RUNNING") || st=UNKNOWN
  [ "$st" = ENDED ] || continue
  DR pull || continue
  ok=1
  for a in A Sb SE; do t=SE1_${a}_s$SEED
    if [ -f "$P/results/$t.tar" ] && (cd "$P/results" && sha256sum -c --quiet "$t.tar.sha256") && (cd /home/narolski/se1_results_copy && sha256sum -c --quiet "$t.tar.sha256"); then :;
    else rc=$(R "cat /workspace/se1/rc/$t 2>/dev/null"); log "$t not verified in two copies (remote rc '$rc')"; ok=0; fi
  done
  pc=$(ls "$P/smoke_$NAME"/SE1_platformcheck_*.tar 2>/dev/null | head -1)
  [ -n "$pc" ] && (cd "$(dirname "$pc")" && sha256sum -c --quiet "$(basename "$pc").sha256") && cp -n "$pc" "$pc.sha256" /home/narolski/se1_results_copy/ || { log "platform tar missing"; ok=0; }
  if [ $ok = 1 ]; then
    if [ "${SE1_NO_RELEASE:-0}" = 1 ]; then log "seed $SEED fetched and verified in two copies; NO RELEASE (lease held by the lead): tell the lead"; exit 0; fi
    touch "$LEASE/RELEASE"; log "RELEASE written: seed $SEED fetched and verified in two copies"; exit 0; fi
  failed=1; for a in A Sb SE; do t=SE1_${a}_s$SEED; [ -f "$P/results/$t.tar" ] && continue
    r=$(R "cat /workspace/se1/rc/$t 2>/dev/null"); [ -n "$r" ] && [ "$r" != 0 ] || failed=0; done
  if [ $failed = 1 ]; then
    if [ "${SE1_NO_RELEASE:-0}" = 1 ]; then log "remote-confirmed failures; NO RELEASE (lease held by the lead): tell the lead"; exit 0; fi
    echo "remote-confirmed failures, see logs" > "$LEASE/FAILED"; touch "$LEASE/RELEASE"; log "RELEASE + FAILED"; exit 0; fi
done
log "loop ended without RELEASE"

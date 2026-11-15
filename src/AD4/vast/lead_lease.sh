#!/bin/bash
# Lead-side driver for one rented single-GPU machine of the morph-free networks experiment (AD4).
#   lead_lease.sh NAME CAP_USD CREDIT_BASELINE "TASK TASK ..." OFFER_ID [OFFER_ID ...]
# Rents the first available offer, starts the watchdog, waits for SSH (direct port first, then proxy; a host that is
# not reachable 10 minutes after creation is destroyed and the next offer is tried), uploads the pack and the listed
# tasks, runs a 200-step smoke test (speed, peak memory), and starts the queue only if the smoke test passed.
set -u
NAME=$1; CAP=$2; BASE=$3; TASKS="$4"; shift 4
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
SRC=/home/narolski/smad-next/src/AD4
KEY=/home/narolski/.config/smad-next/vast_ssh_key
LD=/mnt/t7/smad_next/AD4/vast/$NAME
mkdir -p "$LD"
log(){ echo "$(date +%T) [$NAME] $*" | tee -a "$LD/driver.log"; }
for OFFER in "$@"; do
  IID=$(cd "$SRC" && $P -I - "$OFFER" "$NAME" "$CAP" "$BASE" "$LD" <<'PY'
import sys, json, time
sys.path.insert(0, '.')
import vast_api as V
offer, name, cap, base, ld = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
t = time.time()
try:
    r = V.create(int(offer), 'smad-next-AD4-' + name, 120)
except SystemExit as e:
    print('NONE'); sys.exit(0)
iid = r.get('new_contract')
cfg = dict(label='smad-next-AD4-' + name, offer_id=int(offer), image=V.IMAGE, disk_gb=120, cap_usd=cap, credit_start=base,
           created_epoch=t, deadline_epoch=t + 9 * 3600, instance_id=iid, dph=1.0, hold=True,
           authority='author 11 Nov: approved run on Vast from the main session; A100 class cards; total cap 10 USD')
open(ld + '/lease.json', 'w').write(json.dumps(cfg, indent=1))
print(iid)
PY
)
  [ "$IID" = "NONE" ] || [ -z "$IID" ] && { log "offer $OFFER not available"; continue; }
  log "rented offer $OFFER as instance $IID"
  ( cd "$SRC/vast" && setsid nohup $P -I watchdog.py --config "$LD/lease.json" > "$LD/watchdog.out" 2>&1 < /dev/null & )
  HOST=""; PORT=""; T0=$(date +%s)
  while [ $(( $(date +%s) - T0 )) -lt 780 ]; do
    INFO=$(cd "$SRC" && $P -I - "$IID" <<'PY'
import sys, json
sys.path.insert(0, '.')
import vast_api as V
i = V.call("GET", f"/instances/{int(sys.argv[1])}/", params={"owner": "me"}).get("instances") or {}
p = (i.get("ports") or {}).get("22/tcp") or [{}]
print(i.get("actual_status"), i.get("ssh_host"), i.get("ssh_port"), i.get("public_ipaddr"), p[0].get("HostPort"), i.get("dph_total"), i.get("gpu_name"), i.get("gpu_ram"))
PY
)
    set -- $INFO; ST=${1:-}; PH=${2:-}; PP=${3:-}; DH=${4:-}; DP=${5:-}; DPH=${6:-}; GN=${7:-}; GR=${9:-${8:-}}
    if [ "$ST" = "running" ]; then
      for cand in "$DH $DP" "$PH $PP"; do
        set -- $cand; h=${1:-None}; p=${2:-None}
        [ "$h" = "None" ] || [ "$p" = "None" ] && continue
        if ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$LD/known_hosts" -i "$KEY" -p "$p" "root@$h" 'echo SSH_OK' 2>/dev/null | grep -q SSH_OK; then HOST=$h; PORT=$p; break; fi
      done
      [ -n "$HOST" ] && break
    fi
    sleep 12
  done
  if [ -z "$HOST" ]; then
    log "instance $IID not reachable within 13 minutes (status $ST); destroying"
    ( cd "$SRC" && $P -I vast_api.py destroy "$IID" >/dev/null )
    pkill -f "[w]atchdog.py --config $LD/lease.json"; mkdir -p "$LD/unreachable_$IID"; mv "$LD"/lease.json "$LD"/watchdog.* "$LD"/LIVE_BUDGET.json "$LD/unreachable_$IID/" 2>/dev/null
    continue
  fi
  $P - "$LD/lease.json" "$HOST" "$PORT" "$DPH" <<'PY'
import json, sys
p = sys.argv[1]; c = json.load(open(p)); c.update(ssh_host=sys.argv[2], ssh_port=int(sys.argv[3]), dph=float(sys.argv[4]))
open(p, 'w').write(json.dumps(c, indent=1))
PY
  log "reachable at $HOST:$PORT, $GN, price $DPH USD per hour"
  if ! AD4_LEASE_DIR="$LD" AD4_TASKS="$TASKS" bash "$SRC/vast/launch_remote.sh" "$HOST" "$PORT" setup >> "$LD/driver.log" 2>&1; then
    log "SETUP FAILED; see driver.log; instance left to the watchdog (destroy by hand if needed)"; exit 3
  fi
  log "setup done; smoke test (200 steps, 8 scored images)"
  R() { ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$LD/known_hosts" -i "$KEY" -p "$PORT" "root@$HOST" "$@"; }
  R 'B=/workspace/ad4; set -u; mkdir -p $B/smokeroot/smad-next/packs/AD4 $B/smokeroot/smad-next/results $B/smoke/t200 $B/smoke/tasks/t200
     ln -sf $B/root/smad-next/packs/AD4/ad4_pack.tar $B/smokeroot/smad-next/packs/AD4/ad4_pack.tar
     T=$(ls $B/tasks | sort | head -1); cp $B/tasks/$T/run.sh $B/smoke/tasks/t200/; sed "s/^TASK=.*/TASK=${T}_smoke_t200/" $B/tasks/$T/task.env > $B/smoke/tasks/t200/task.env
     ( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $B/smoke/gpumem.csv; sleep 5; done ) & S=$!
     ( cd $B/smoke/t200 && CUDA_VISIBLE_DEVICES=0 TASK_DIR=$B/smoke/tasks/t200 TASK_WORK=$B/smoke/t200 AD4_LOCAL=1 AD4_PY=python AD4_ROOT=$B/smokeroot AD4_WORKERS=7 AD4_STEPS=200 AD4_LIMIT=8 TMPDIR=/tmp bash $B/smoke/tasks/t200/run.sh > $B/smoke/t200.log 2>&1 ); rc=$?
     kill $S; echo "SMOKE_RC=$rc"; grep -E "step +[0-9]+/|AD4_TASK_DONE|AD4 FAIL|AD4 env|out of memory|OutOfMemory" $B/smoke/t200.log | tail -6
     awk -F", " "{if (\$2+0>m) m=\$2+0} END {print \"PEAK_MIB \" m}" $B/smoke/gpumem.csv; rm -rf $B/smoke/t200/ad4 $B/smokeroot/smad-next/results' > "$LD/smoke.txt" 2>&1
  cat "$LD/smoke.txt" | tee -a "$LD/driver.log"
  if grep -q "SMOKE_RC=0" "$LD/smoke.txt"; then
    AD4_LEASE_DIR="$LD" bash "$SRC/vast/launch_remote.sh" "$HOST" "$PORT" queue 1 >> "$LD/driver.log" 2>&1 && log "QUEUE STARTED with tasks: $TASKS"
    exit 0
  fi
  log "SMOKE FAILED; destroying instance $IID"
  ( cd "$SRC" && $P -I vast_api.py destroy "$IID" >/dev/null ); exit 4
done
log "no offer could be used"; exit 5

#!/bin/bash
# Lead-side: rents ONE machine that an experiment owner then operates over SSH. Run from the main session only,
# and only with the author's approval for that rental.
#   rent_owner_machine.sh NAME CAP_USD HOURS DISK_GB "AUTHORITY TEXT" OFFER_ID [OFFER_ID ...]
# Rents the first available offer, writes /mnt/t7/smad_next/vast/NAME/lease.json, starts guard.py (destroys at the
# cap, at the deadline, or when the owner writes the file RELEASE), waits up to 13 minutes for SSH (else destroys
# and tries the next offer) and prints "READY <host> <port>".
# NOT YET RUN (11 Nov 2026): written while the rental itself awaited the author's confirmation.
set -u
NAME=$1; CAP=$2; HOURS=$3; DISK=$4; AUTH=$5; shift 5
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
SRC=/home/narolski/smad-next/src
KEY=/home/narolski/.config/smad-next/vast_ssh_key
LD=/mnt/t7/smad_next/vast/$NAME
mkdir -p "$LD"
log(){ echo "$(date +%T) [$NAME] $*" | tee -a "$LD/driver.log"; }
for OFFER in "$@"; do
  IID=$(cd "$SRC/AD4" && $P -I - "$OFFER" "$NAME" "$CAP" "$HOURS" "$DISK" "$LD" "$AUTH" <<'PY'
import sys, json, time
sys.path.insert(0, '.')
import vast_api as V
offer, name, cap, hours, disk, ld, auth = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7]
t = time.time()
try:
    r = V.create(int(offer), 'smad-next-' + name, disk)
except SystemExit:
    print('NONE'); sys.exit(0)
iid = r.get('new_contract')
cfg = dict(label='smad-next-' + name, offer_id=int(offer), image=V.IMAGE, disk_gb=disk, cap_usd=cap, created_epoch=t,
           deadline_epoch=t + hours * 3600, instance_id=iid, dph=1.0, authority=auth)
open(ld + '/lease.json', 'w').write(json.dumps(cfg, indent=1))
print(iid)
PY
)
  [ "$IID" = "NONE" ] || [ -z "$IID" ] && { log "offer $OFFER not available"; continue; }
  log "rented offer $OFFER as instance $IID"
  ( cd "$SRC/vast" && setsid nohup $P -I guard.py --config "$LD/lease.json" > "$LD/guard.out" 2>&1 < /dev/null & )
  HOST=""; PORT=""; T0=$(date +%s)
  while [ $(( $(date +%s) - T0 )) -lt 780 ]; do
    INFO=$(cd "$SRC/AD4" && $P -I - "$IID" <<'PY'
import sys
sys.path.insert(0, '.')
import vast_api as V
i = V.call("GET", f"/instances/{int(sys.argv[1])}/", params={"owner": "me"}).get("instances") or {}
p = (i.get("ports") or {}).get("22/tcp") or [{}]
print(i.get("actual_status"), i.get("ssh_host"), i.get("ssh_port"), i.get("public_ipaddr"), p[0].get("HostPort"), i.get("dph_total"), str(i.get("gpu_name")).replace(" ", "_"), i.get("gpu_ram"))
PY
)
    set -- $INFO; ST=${1:-}; PH=${2:-}; PP=${3:-}; DH=${4:-}; DP=${5:-}; DPH=${6:-}; GN=${7:-}
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
    log "instance $IID not reachable within 13 minutes (status ${ST:-unknown}); destroying"
    ( cd "$SRC/AD4" && $P -I vast_api.py destroy "$IID" >/dev/null )
    mkdir -p "$LD/unreachable_$IID"; mv "$LD"/lease.json "$LD"/guard.* "$LD"/LIVE.json "$LD/unreachable_$IID/" 2>/dev/null
    continue
  fi
  $P - "$LD/lease.json" "$HOST" "$PORT" "$DPH" "$GN" <<'PY'
import json, sys
p = sys.argv[1]; c = json.load(open(p)); c.update(ssh_host=sys.argv[2], ssh_port=int(sys.argv[3]), dph=float(sys.argv[4]), gpu=sys.argv[5])
open(p, 'w').write(json.dumps(c, indent=1))
PY
  R() { ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$LD/known_hosts" -i "$KEY" -p "$PORT" "root@$HOST" "$@"; }
  log "reachable at $HOST:$PORT, $GN, price $DPH USD per hour"
  R 'nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; nproc; free -g | sed -n 2p; df -h /workspace 2>/dev/null | tail -1; python -c "import torch,sys;print(sys.version.split()[0],torch.__version__,torch.version.cuda)"' 2>&1 | tee -a "$LD/driver.log"
  echo "READY $HOST $PORT"
  exit 0
done
log "no offer could be rented"; exit 1

#!/bin/bash
# PN1 amendment 10: upload pack 2, the new run.sh and two task folders to one rented machine and start its second
# queue (it waits until the first queue has ended). Usage: bash upload_pack2.sh HOST PORT LEASE SEED   (SEED 401 or 402)
set -euo pipefail
HOST=$1; PORT=$2; L=$3; SEED=$4
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
PIN2=266ce5c352f1a04220d2025092ef92f973f0c8ecdc5872671a228819b189fce6
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
P=/mnt/t7/smad_next/PN1; B=/workspace/pn1; S=/home/narolski/smad-next/src/PN1
T=$(mktemp -d -p "$P"); for a in Sb Bv; do mkdir -p "$T/PN1_${a}_s$SEED"; cp "$S/run.sh" "$T/PN1_${a}_s$SEED/"; printf "TASK=PN1_${a}_s$SEED\nARM=$a\nSEED=$SEED\n" > "$T/PN1_${a}_s$SEED/task.env"; done
RS "$P/pn1_pack2.tar" "$P/pn1_pack2.tar.sha256" "root@$HOST:$B/root/packs/PN1/"
RS "$T/" "root@$HOST:$B/tasks/"; RS "$S/rented/remote_queue2.sh" "root@$HOST:$B/bin/"; rm -rf "$T"
timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_queue2.sh $PIN2 'PN1_Sb_s$SEED PN1_Bv_s$SEED' > $B/logs/queue2_driver.log 2>&1 < /dev/null & sleep 2; echo QUEUE2_ARMED" || true
echo "$(date +%T) pack2 uploaded, queue 2 armed (seed $SEED)" | tee -a "$L/pn1_drive.log"

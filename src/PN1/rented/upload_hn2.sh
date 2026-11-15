#!/bin/bash
# PN1 amendment 13: upload the HN2 FFHQ pack and remote_hn2.sh to one rented machine, create the task folder (so
# drive.sh pull waits for PN1_HN2_s<SEED> before RELEASE) and start the fourth queue (it waits for ALL_DONE3).
# Usage: bash upload_hn2.sh HOST PORT LEASE SEED   (SEED 401 or 402)
set -euo pipefail
HOST=$1; PORT=$2; L=$3; SEED=$4
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
P=/mnt/t7/smad_next/PN1; B=/workspace/pn1; S=/home/narolski/smad-next/src/PN1
timeout 30 ssh "${O[@]}" "root@$HOST" "mkdir -p $B/tasks/PN1_HN2_s$SEED && echo TASK=PN1_HN2_s$SEED > $B/tasks/PN1_HN2_s$SEED/task.env"
RS "$P/pn1_hn2.tar" "$P/pn1_hn2.tar.sha256" "root@$HOST:$B/root/packs/PN1/"
RS "$S/rented/remote_hn2.sh" "root@$HOST:$B/bin/"
timeout 30 ssh "${O[@]}" "root@$HOST" "cd $B && nohup setsid bash $B/bin/remote_hn2.sh $SEED > $B/logs/hn2_driver.log 2>&1 < /dev/null & sleep 2; echo HN2_ARMED" || true
echo "$(date +%T) hn2 pack uploaded, queue 4 armed (seed $SEED)" | tee -a "$L/pn1_drive.log"

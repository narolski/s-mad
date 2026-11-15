#!/bin/bash
#   start.sh HOST PORT LEASE   starts remote_run.sh detached (setsid nohup) and returns; progress: logs/progress.txt
set -euo pipefail
H=$1; P=$2; LD=$3; K=/home/narolski/.config/smad-next/vast_ssh_key
ssh -o BatchMode=yes -o UserKnownHostsFile=$LD/known_hosts -i $K -p $P root@$H \
  'mkdir -p /root/ad5/logs; cd /root/ad5 && setsid nohup bash packs/remote_run.sh > logs/remote_run.out 2>&1 < /dev/null & echo started'

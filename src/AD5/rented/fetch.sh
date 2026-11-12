#!/bin/bash
#   fetch.sh HOST PORT LEASE   copies finished result tars + logs back to /mnt/t7/smad_next/AD5/results/rented/ and
# checks every sha256 (keep rule: weights stay as the one verified copy here until the lead says otherwise). When all
# five seeds are OK it writes LEASE/RELEASE, which tells the lead's guard to destroy the machine.
set -uo pipefail
H=$1; P=$2; LD=$3; K=/home/narolski/.config/smad-next/vast_ssh_key; O=/mnt/t7/smad_next/AD5/results/rented
mkdir -p $O; df -h /mnt/t7 | tail -1
rsync -a --partial -e "ssh -o BatchMode=yes -o UserKnownHostsFile=$LD/known_hosts -i $K -p $P" root@$H:/root/ad5/results/ root@$H:/root/ad5/logs $O/
cd $O; n=0; for s in madation_B_s*.tar.sha256; do [ -f "$s" ] || continue; sha256sum -c "$s" && n=$((n+1)); done
echo "verified $n of 5"; [ $n = 5 ] && { touch $LD/RELEASE; echo RELEASE written; }

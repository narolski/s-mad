#!/bin/bash
# MS1 (MS1-D2): for one lease, wait for the setup run to finish; if SETUP_OK, start the queue and the pull loop.
# usage: bash after_setup.sh Q [LEASE]   (default lease folder /mnt/t7/smad_next/vast/ms1<Q>, READY line in rent.out)
set -u
Q=$1; L=${2:-/mnt/t7/smad_next/vast/ms1$Q}; D=$(cd "$(dirname "$0")" && pwd)
read -r _ H P < <(grep READY "$L/rent.out" | tail -1)
while pgrep -f "drive_ms1.sh $H $P $L $Q setup" > /dev/null; do sleep 30; done
grep -q "SETUP_OK $Q" "$L/ms1_drive.log" || { echo "$(date +%T) setup not OK; nothing started" >> "$L/ms1_drive.log"; exit 1; }
bash "$D/drive_ms1.sh" "$H" "$P" "$L" "$Q" queue || exit 1
nohup setsid bash "$D/drive_ms1.sh" "$H" "$P" "$L" "$Q" loop > "$L/ms1_loop.out" 2>&1 < /dev/null &
echo "$(date +%T) loop started" >> "$L/ms1_drive.log"

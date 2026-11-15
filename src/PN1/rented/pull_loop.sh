#!/bin/bash
# PN1 rented: pull every 10 minutes until all nine tars are back and verified (drive.sh writes RELEASE), then stop.
set -u
HOST=$1; PORT=$2; L=$3
D=$(cd "$(dirname "$0")" && pwd)
for k in $(seq 1 120); do
  bash "$D/drive.sh" "$HOST" "$PORT" "$L" pull >> "$L/pn1_pull.log" 2>&1
  [ -f "$L/RELEASE" ] && { echo "RELEASE $(date +%T)" >> "$L/pn1_pull.log"; break; }
  sleep 600
done

#!/bin/bash
# PN1 amendment 10 queue (rented): waits for the first queue (ALL_DONE), then runs the given tasks one after another
# with pack 2 through run.sh (arm list Sb, Bv), one result tar per task. Args: PIN2 TASKS
set -u
B=/workspace/pn1; PIN2=$1; TASKS=$2
until [ -f "$B/ALL_DONE" ]; do sleep 60; done
cd "$B/root/packs/PN1"; [ "$(cut -c1-64 pn1_pack2.tar.sha256)" = "$PIN2" ] && sha256sum -c pn1_pack2.tar.sha256 >> "$B/queue2.log" 2>&1 || { echo "pack2 check failed" >> "$B/queue2.log"; exit 1; }
for T in $TASKS; do
  for try in 1 2; do
    W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
    ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$B/root/packs/PN1/pn1_pack2.tar" \
      PN1_LOCAL=1 PN1_PY=python PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
    rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$W"
    echo "$(date +%T) $T try $try rc $rc" >> "$B/queue2.log"
    [ $rc -eq 0 ] && break
    grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && break
  done
done
date > "$B/ALL_DONE2"

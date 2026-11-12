#!/bin/bash
# PN1 arm Sp (registration 1b8fe48), rented FS1 host. A separate file, so the running FS1 queue's remote_fs.sh is never
# touched. One call does both steps, detached:
#   bash remote_sp.sh PINFS PINSP "T1 T2 T3"
# 1. build pn1_pack_sp.tar = copy of pn1_pack_fs.tar (checked against PINFS) + `tar -A pn1_overlay_sp.tar`; check
#    against PINSP (log logs/sp_pack.log); on a mismatch write rc FAIL for every task and stop (no fit runs).
# 2. take the host-wide fit lock (fs_queue.lock; held by the FS1 queue until its 16 fits end), then run the tasks one
#    after another through their run.sh with the Sp pack, exactly as remote_fs.sh's queue (re-run once on an
#    infrastructure failure, never on a non-finite loss); markers QUEUE_FS_STARTED_sp, queue_fs_sp.log, ALL_DONE_FS_sp.
set -u
B=/workspace/pn1; PINFS=${1:?}; PINSP=${2:?}; TASKS=${3:?}; Q=sp
P=$B/root/packs/PN1; LG=$B/logs/sp_pack.log
date > "$B/QUEUE_FS_STARTED_$Q"
{
  echo "$(date +%T) building the Sp pack"
  [ "$(sha256sum < "$P/pn1_pack_fs.tar" | cut -d' ' -f1)" = "$PINFS" ] || { echo "FS1 pack differs from its pin"; exit 2; }
  cp "$P/pn1_pack_fs.tar" "$P/pn1_pack_sp.tar.part" && tar -Af "$P/pn1_pack_sp.tar.part" "$P/pn1_overlay_sp.tar" || exit 3
  h=$(sha256sum < "$P/pn1_pack_sp.tar.part" | cut -d' ' -f1)
  [ "$h" = "$PINSP" ] || { echo "Sp pack $h differs from the pin $PINSP"; exit 4; }
  mv "$P/pn1_pack_sp.tar.part" "$P/pn1_pack_sp.tar"; echo "$PINSP  pn1_pack_sp.tar" > "$P/pn1_pack_sp.tar.sha256"
  echo "$(date +%T) Sp pack OK $PINSP"
} >> "$LG" 2>&1
if [ ! -f "$P/pn1_pack_sp.tar" ]; then
  for T in $TASKS; do echo "FAIL sp_pack" > "$B/rc/$T"; done
  echo "$(date +%T) Sp pack failed: no fit run" >> "$B/queue_fs_$Q.log"; date > "$B/ALL_DONE_FS_$Q"; exit 1
fi
exec 9> "$B/fs_queue.lock"; flock 9          # waits until the FS1 queue has ended
echo "$(date +%T) queue $Q has the lock" >> "$B/queue_fs_$Q.log"
for T in $TASKS; do
  for try in 1 2; do
    W=$B/work/$T; rm -rf "$W"; mkdir -p "$W"
    ( cd "$W" && TMPDIR=$B/tmp TASK_DIR="$B/tasks/$T" TASK_WORK="$W" PN1_ROOT="$B/root" PN1_PACK="$P/pn1_pack_sp.tar" \
      PN1_LOCAL=1 PN1_PY=python PN1_WORKERS=7 bash "$B/tasks/$T/run.sh" ) >> "$B/logs/$T.log" 2>&1
    rc=$?; echo "$rc" > "$B/rc/$T"; rm -rf "$W"
    echo "$(date +%T) $T try $try rc $rc" >> "$B/queue_fs_$Q.log"
    [ $rc -eq 0 ] && break
    grep -qiE "loss +nan|loss +inf|non-finite" "$B/logs/$T.log" && { echo "$(date +%T) $T non-finite: not re-run" >> "$B/queue_fs_$Q.log"; break; }
  done
done
date > "$B/ALL_DONE_FS_$Q"

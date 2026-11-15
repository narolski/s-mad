#!/bin/bash
# SM1 sm1dg reorder driver (13 Nov 01:45; lead's order): A18 starts on the GPU now; the A16 pack keeps uploading in the
# background; A16 scores on the machine only after A18 (remote_a18_then_a16.sh, one GPU user at a time). RELEASE only
# when BOTH are back and verified (3 A18 tars, 6 A16 tars, logs); FAILED + RELEASE on a verified partial result or at
# the deadline (09:30 local, lease deadline 10:00).
#   nohup setsid bash drive_v3.sh HOST PORT LEASE > LEASE/sm1_v3.log 2>&1 &
set -uo pipefail
HOST=${1:?}; PORT=${2:?}; L=${3:?}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=/home/narolski/.config/smad-next/vast_ssh_key
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh -n "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=300 -e "ssh ${O[*]}" "$@"; }
B=/workspace/sm1r; OUTD=/mnt/t7/smad_next/SM1/results_rented; OH=$OUTD/hn2; O16=$OUTD/dev16
H2=/mnt/t7/smad_next/SM1/hn2; D16=/mnt/t7/smad_next/SM1/dev_a16; GP=/mnt/t7/smad_next/SM1/gpupack
log() { echo "$(date +%T) $*" | tee -a "$L/sm1_drive.log"; }
DEADLINE=$(date -d '09:30' +%s); [ "$DEADLINE" -lt "$(date +%s)" ] && DEADLINE=$((DEADLINE + 86400))
# --- A18 now (ad4_pack is already unpacked on the machine)
R "[ -f $B/done/ad4_pack ]" || { log "ad4_pack not unpacked on the machine: stop"; exit 1; }
R "mkdir -p $B/bin $B/logs $B/manifests/hn2 $B/manifests/dev16 $B/data/x $B/results"
RS "$SRC/fit_hn2.sh" "$SRC/remote_hn2.sh" "$SRC/remote_dev16.sh" "$SRC/remote_a18_then_a16.sh" "$SRC/unpack_one.sh" "$SRC/../sm1_lora_audit.py" "root@$HOST:$B/bin/"
RS "$H2/sm1_hn2_manifests.tar" "$H2/sm1_hn2_manifests.tar.sha256" "root@$HOST:$B/manifests/hn2/"
R "cd $B/manifests/hn2 && sha256sum -c sm1_hn2_manifests.tar.sha256 && tar -xf sm1_hn2_manifests.tar && rm sm1_hn2_manifests.tar"
RS "$H2/sm1_hn2_files.tar" "$H2/sm1_hn2_files.tar.sha256" "root@$HOST:$B/in/"
R "cd $B/in && sha256sum -c sm1_hn2_files.tar.sha256 && tar -C $B/data/x -xf sm1_hn2_files.tar && rm sm1_hn2_files.tar && cd $B/data/x && sha256sum -c --quiet $B/manifests/hn2/hn2_files.sha256 && echo DG1_FILES_OK"
R "cd $B; (nohup setsid bash $B/bin/remote_a18_then_a16.sh > $B/logs/orchestrator_driver.log 2>&1 < /dev/null &) > /dev/null 2>&1; sleep 2; echo started"
log "A18 started on the GPU (orchestrator: A18, then A16 when staged)"
# --- A16 staging in the background of this driver (the old upload of sm1gpu_img_test.tar may still be running)
(
  while pgrep -f "rsync .*$PORT.*sm1gpu_img_test" > /dev/null; do sleep 60; done
  RS "$GP/sm1gpu_img_test.tar" "$GP/sm1gpu_img_test.tar.sha256" "root@$HOST:$B/in/" && \
  R "bash $B/bin/unpack_one.sh sm1gpu_img_test" && \
  for t in SM1B_a_s401 SM1B_a_s402 SM1B_e_s401 SM1B_e_s402 SM1B_f_s401 SM1B_f_s402; do RS "$OUTD/$t.tar" "$OUTD/$t.tar.sha256" "root@$HOST:$B/results/"; done && \
  R "cd $B/results && sha256sum -c --quiet SM1B_*.sha256 && date > $B/ALL_DONE" && \
  RS "$D16/sm1_dev16_eval.csv" "$D16/sm1_dev16_eval.csv.sha256" "$D16/dev16_files.sha256" "root@$HOST:$B/manifests/dev16/" && \
  RS "$D16/sm1_dev16_files.tar" "$D16/sm1_dev16_files.tar.sha256" "root@$HOST:$B/in/" && \
  R "cd $B/in && sha256sum -c sm1_dev16_files.tar.sha256 && tar -C $B/data/x -xf sm1_dev16_files.tar && rm sm1_dev16_files.tar && date > $B/A16_READY" && \
  log "A16 inputs staged (A16_READY)" || log "A16 staging failed"
) &
# --- watch, pull, release
while :; do
  sleep 600
  mkdir -p "$OH/machine_logs" "$O16"
  RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_hn2/" "$OH/" 2>/dev/null
  RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_dev16/" "$O16/" 2>/dev/null
  RS "root@$HOST:$B/logs/" "$OH/machine_logs/" 2>/dev/null
  done_both=0; R "[ -f $B/BOTH_DONE ]" && done_both=1
  if [ "$(date +%s)" -ge "$DEADLINE" ] && [ $done_both = 0 ]; then
    R "touch $B/A16_ABANDON"; log "deadline reached before BOTH_DONE"; late=1
  else late=0; fi
  if [ $done_both = 1 ] || [ $late = 1 ]; then
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_hn2/" "$OH/" 2>/dev/null
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_dev16/" "$O16/" 2>/dev/null
    RS "root@$HOST:$B/logs/" "root@$HOST:$B/queue_hn2.log" "$OH/machine_logs/" 2>/dev/null
    nh=$(cd "$OH" && ls HN2_RS_s40?.tar 2>/dev/null | while read t; do sha256sum -c --quiet "$t.sha256" && echo ok; done | grep -c ok)
    n16=$(cd "$O16" && ls SM1E_*.tar 2>/dev/null | while read t; do sha256sum -c --quiet "$t.sha256" && echo ok; done | grep -c ok)
    log "verified: A18 $nh of 3, A16 $n16 of 6"
    if [ "$nh" -eq 3 ] && [ "$n16" -eq 6 ]; then touch "$L/RELEASE"; log "RELEASE written (both complete, logs back)";
    else touch "$L/FAILED" "$L/RELEASE"; log "FAILED + RELEASE written (verified partial: A18 $nh / 3, A16 $n16 / 6; logs back)"; fi
    break
  fi
done

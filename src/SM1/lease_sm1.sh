#!/bin/bash
# SM1 driver for the rented CPU machine "leaseB" (lead's offer, 11 Nov 17:32): CPU builds only, never the GPU, only
# under /workspace/sm1, all at nice 19, at most 96 processes. Connection as src/AD4/vast/launch_remote.sh (key used
# locally only, never copied or printed). One attempt per step; never loop on a failed connection.
#   bash lease_sm1.sh up TASK        upload pack + task dir (rsync; sha256 checked inside run.sh)
#   bash lease_sm1.sh run8 TASK      run the task on 8 pairs per list (engine check vs DGX references)
#   bash lease_sm1.sh run TASK       full run, detached; log /workspace/sm1/logs/task_TASK.log
#   bash lease_sm1.sh status TASK    tail of the log, df, load
#   bash lease_sm1.sh fetch TASK     copy the result tar + sha256 back to /mnt/t7/smad_next/SM1/lease/ and check
#   bash lease_sm1.sh clean TASK     remove the task's work dir and tars on the lease (after a verified fetch)
set -euo pipefail
STEP=${1:?}; T=${2:?task c|b}
HOST=89.221.67.144; PORT=17736
KEY=/home/narolski/.config/smad-next/vast_ssh_key
KH=/mnt/t7/smad_next/AD4/vast/leaseB/known_hosts
O=(-o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile="$KH" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@" 2>&1 | grep -v "Welcome to vast.ai\|Have fun\|double check your ssh key"; }
RS() { rsync -a --partial --timeout=300 -e "ssh ${O[*]}" "$@"; }
B=/workspace/sm1
LOC=/mnt/t7/smad_next/SM1
LOG=$LOC/lease/lease_log.txt
mkdir -p "$LOC/lease"
echo "$(date -Is) $STEP $T" >> "$LOG"
PT=${PACKT:-$T}   # A12 item 11: PACKT=b reuses pack b already on the lease (overlay task d5)
ENV="SM1_PACK=$B/packs/sm1_${PT}_pack.tar SM1_RESULTS=$B/results SM1_PY=$B/venv/bin/python TMPDIR=$B/tmp/$T"
case "$STEP" in
  up)
    T0=$SECONDS
    [ "$PT" = "$T" ] && RS "$LOC/wcss/packs/SM1/sm1_${T}_pack.tar" "root@$HOST:$B/packs/"
    RS "$LOC/wcss/staging/SM1/cpu/SM1_cpu_${T}/" "root@$HOST:$B/task_${T}/"
    echo "upload $((SECONDS - T0)) s" | tee -a "$LOG"
    R "df -h /workspace | tail -1; free -g | sed -n 2p; ls -la $B/packs $B/task_${T}"
    ;;
  run8)
    R "mkdir -p $B/tmp/$T; cd $B && env $ENV SM1_LIMIT=8 SLURM_CPUS_PER_TASK=4 nice -n 19 bash $B/task_${T}/run.sh > $B/logs/task_${T}_limit8.log 2>&1; echo rc=\$?; tail -4 $B/logs/task_${T}_limit8.log; cat $B/tmp/$T/sm1_${T}/out/logs/compare_ref.json | head -5; grep -h max_abs $B/tmp/$T/sm1_${T}/out/logs/verify_cli_*.json | head -4" | tee -a "$LOG"
    ;;
  run)
    R "mkdir -p $B/tmp/$T; cd $B && nohup setsid env $ENV SLURM_CPUS_PER_TASK=${NCPU:-96} nice -n 19 bash $B/task_${T}/run.sh > $B/logs/task_${T}.log 2>&1 < /dev/null & sleep 2; echo started; head -3 $B/logs/task_${T}.log" | tee -a "$LOG"
    ;;
  status)
    R "tail -5 $B/logs/task_${T}.log; ls $B/results; df -h /workspace | tail -1; uptime"
    ;;
  fetch)
    T0=$SECONDS
    RS "root@$HOST:$B/results/sm1_${T}_out.tar" "root@$HOST:$B/results/sm1_${T}_out.tar.sha256" "root@$HOST:$B/logs/task_${T}.log" "$LOC/lease/"
    echo "fetch $((SECONDS - T0)) s" | tee -a "$LOG"
    [ "$(sha256sum "$LOC/lease/sm1_${T}_out.tar" | cut -c1-64)" = "$(cut -c1-64 "$LOC/lease/sm1_${T}_out.tar.sha256")" ] && echo "FETCH_SHA_OK $T" | tee -a "$LOG"
    ;;
  clean)
    R "rm -rf $B/tmp/$T $B/results/sm1_${T}_out.tar $B/results/sm1_${T}_out_limit8.tar; df -h /workspace | tail -1" | tee -a "$LOG"
    ;;
  *) echo "step $STEP"; exit 1 ;;
esac

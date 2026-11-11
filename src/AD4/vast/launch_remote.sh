#!/bin/bash
# DGX-side driver for the AD4 ViT-B/16 Vast lease (no Vast API calls here; SSH key used locally only, never copied).
#   bash launch_remote.sh HOST PORT setup   # upload pack + scripts + the ten task dirs, check pack sha256, pip pins
#   bash launch_remote.sh HOST PORT smoke   # GPU0: AD4_m3mf_s401 3 steps, 8 scored images; GPU1: same task 200 steps
#                                           # (it/s); peak GPU memory from nvidia-smi samples -> smoke/ here
#   bash launch_remote.sh HOST PORT queue NGPU   # start the remote queue (one worker per GPU), detached
# Everything is logged under /mnt/t7/smad_next/AD4/vast/.
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; STEP=${3:?setup|smoke|queue}
L=${AD4_LEASE_DIR:-/mnt/t7/smad_next/AD4/vast}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=/home/narolski/.config/smad-next/vast_ssh_key
mkdir -p "$L"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 -e "ssh ${O[*]}" "$@"; }
B=/workspace/ad4
TASKS="${AD4_TASKS:-AD4_m3mf_s401 AD4_m3mf_s402 AD4_m3mf_s403 AD4_m3mf_s404 AD4_m3mf_s405 AD4_m3perm_s401 AD4_m3perm_s402 AD4_m3perm_s403 AD4_m3perm_s404 AD4_m3perm_s405}"
case "$STEP" in
  setup)
    R "mkdir -p $B/root/smad-next/packs/AD4 $B/root/smad-next/results/AD4 $B/tasks $B/bin && nvidia-smi -L && df -h /workspace | tail -1"
    T0=$SECONDS
    RS /mnt/t7/smad_next/AD4/ad4_pack.tar /mnt/t7/smad_next/AD4/ad4_pack.tar.sha256 "root@$HOST:$B/root/smad-next/packs/AD4/"
    echo "pack upload $((SECONDS - T0)) s" | tee -a "$L/launch.log"
    RS "$SRC/remote_setup.sh" "$SRC/remote_queue.sh" "root@$HOST:$B/bin/"
    for t in $TASKS; do RS "/mnt/t7/smad_next/AD4/staging/AD4/$t" "root@$HOST:$B/tasks/"; done
    R "bash $B/bin/remote_setup.sh" 2>&1 | tee -a "$L/setup.log"
    grep -q SETUP_OK "$L/setup.log"
    ;;
  smoke)
    R "set -e; mkdir -p $B/smokeroot/smad-next/packs/AD4 $B/smokeroot/smad-next/results $B/smoke/t3 $B/smoke/t200 $B/smoke/tasks;
       ln -sf $B/root/smad-next/packs/AD4/ad4_pack.tar $B/smokeroot/smad-next/packs/AD4/ad4_pack.tar;
       for v in t3 t200; do mkdir -p $B/smoke/tasks/\$v; cp $B/tasks/AD4_m3mf_s401/run.sh $B/smoke/tasks/\$v/;
         sed 's/^TASK=.*/TASK=AD4_m3mf_s401_smoke_'\$v'/' $B/tasks/AD4_m3mf_s401/task.env > $B/smoke/tasks/\$v/task.env; done;
       ( while :; do nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits >> $B/smoke/gpumem.csv; sleep 5; done ) & S=\$!;
       ( cd $B/smoke/t3 && CUDA_VISIBLE_DEVICES=0 TASK_DIR=$B/smoke/tasks/t3 TASK_WORK=$B/smoke/t3 AD4_LOCAL=1 AD4_PY=python AD4_ROOT=$B/smokeroot AD4_WORKERS=7 AD4_STEPS=3 AD4_LIMIT=8 TMPDIR=/tmp bash $B/smoke/tasks/t3/run.sh > $B/smoke/t3.log 2>&1; echo rc=\$? >> $B/smoke/t3.log ) & P1=\$!;
       ( cd $B/smoke/t200 && CUDA_VISIBLE_DEVICES=1 TASK_DIR=$B/smoke/tasks/t200 TASK_WORK=$B/smoke/t200 AD4_LOCAL=1 AD4_PY=python AD4_ROOT=$B/smokeroot AD4_WORKERS=7 AD4_STEPS=200 AD4_LIMIT=8 TMPDIR=/tmp bash $B/smoke/tasks/t200/run.sh > $B/smoke/t200.log 2>&1; echo rc=\$? >> $B/smoke/t200.log ) & P2=\$!;
       wait \$P1 \$P2 || true; kill \$S; rm -rf $B/smoke/t3/ad4 $B/smoke/t200/ad4"
    mkdir -p "$L/smoke"
    RS "root@$HOST:$B/smoke/t3.log" "root@$HOST:$B/smoke/t200.log" "root@$HOST:$B/smoke/gpumem.csv" "$L/smoke/"
    RS "root@$HOST:$B/smokeroot/smad-next/results/" "$L/smoke/results/"
    grep -E "rc=|AD4_TASK_DONE|FAIL|step +[0-9]+/" "$L/smoke/t3.log" "$L/smoke/t200.log" | cut -c1-200
    awk -F', ' '{if ($2 > m[$1]) m[$1] = $2} END {for (g in m) print "peak MiB gpu " g ": " m[g]}' "$L/smoke/gpumem.csv"
    ;;
  queue)
    N=${4:?number of GPUs}
    R "rm -rf $B/smoke/t3 $B/smoke/t200; cd $B && nohup setsid bash $B/bin/remote_queue.sh $N > $B/queue.log 2>&1 < /dev/null & sleep 3; cat $B/QUEUE_STARTED"
    ;;
  *) echo "step $STEP"; exit 1 ;;
esac
echo "launch_remote $STEP done"

#!/bin/bash
# PR1 GD job driver (DGX side) for the rented A100 pn1fs. Writes only under /workspace/pr1 on the host and
# /mnt/t7/smad_next/PR1 here. Never writes RELEASE or DONE_* files (the lead touches DONE_pr1).
#   bash drive_gd.sh upload | test | start | status | pull
set -u
STEP=${1:?step}
L=/mnt/t7/smad_next/vast/pn1fs; HOST=149.248.21.7; PORT=30078
KEY=${PN1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=120 --bwlimit=30000 -e "ssh ${O[*]}" "$@"; }
S=/home/narolski/smad-next/src/PR1; D=/mnt/t7/smad_next/PR1; B=/workspace/pr1
GSHA=$(cut -c1-64 "$D/pr1_gd.tar.sha256"); GSHA8=$(cut -c1-64 "$D/pr1_gd_limit8.tar.sha256")
FSHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004
case "$STEP" in
  upload)
    R "mkdir -p $B/bin $B/packs $B/logs $B/results"
    (cd "$S" && sha256sum remote_gd.sh gate_gd.py rescore.py rescore_tf32.py nets_pins.txt > "$D/bin_SHA256SUMS")
    RS "$S/remote_gd.sh" "$S/gate_gd.py" "$S/rescore.py" "$S/rescore_tf32.py" "$S/nets_pins.txt" "root@$HOST:$B/bin/"
    RS "$D/bin_SHA256SUMS" "root@$HOST:$B/bin/SHA256SUMS"
    RS "$D/pr1_gd_limit8.tar" "$D/pr1_gd.tar" "root@$HOST:$B/packs/"
    R "cd $B/bin && sha256sum -c --quiet SHA256SUMS && cd $B/packs && echo '$GSHA  pr1_gd.tar' | sha256sum -c --quiet && echo '$GSHA8  pr1_gd_limit8.tar' | sha256sum -c --quiet && echo UPLOAD_OK" ;;
  start)
    R "test ! -e $B/results/PR1_GD_pn1fs.tar && test ! -e $B/PR1_DONE" || { echo "result or PR1_DONE exists; refusing (F1)"; exit 1; }
    R "cd $B && CUDA_VISIBLE_DEVICES=0 nohup setsid bash $B/bin/remote_gd.sh $GSHA $FSHA > $B/logs/run.log 2>&1 < /dev/null & sleep 3; tail -2 $B/logs/run.log" ;;
  status)
    R "tail -3 $B/logs/run.log; ls $B/PR1_DONE 2>/dev/null; ls /workspace/tt1/DONE_FS /workspace/tt1/DONE_sp /workspace/tt1/NO_SP 2>/dev/null" ;;
  pull)
    R "test -f $B/PR1_DONE" || { echo "not done"; exit 1; }
    mkdir -p "$D/results" "$D/results_copy2"
    RS "root@$HOST:$B/results/PR1_GD_pn1fs.tar" "root@$HOST:$B/results/PR1_GD_pn1fs.tar.sha256" "$D/results/"
    (cd "$D/results" && sha256sum -c PR1_GD_pn1fs.tar.sha256) || exit 1
    cp "$D/results/PR1_GD_pn1fs.tar" "$D/results/PR1_GD_pn1fs.tar.sha256" "$D/results_copy2/"
    (cd "$D/results_copy2" && sha256sum -c PR1_GD_pn1fs.tar.sha256) && echo "PR1 kept: two verified copies" ;;
esac

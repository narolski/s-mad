#!/bin/bash
# SM1 rented A100 (amendment A13), DGX-side driver. No rental API here; the SSH key is used by path only, never printed
# or copied. One command does everything (the lead starts it from the main session after renting):
#   nohup setsid bash drive.sh HOST PORT LEASE all > LEASE/sm1_all.log 2>&1 &
# Steps (each also callable alone):
#   setup   machine check, pinned pip packages, then per pack: free-disk check, upload tar + .sha256, hash check on
#           the machine, unpack, delete the tar (unpack_one.sh); scripts
#   smoke   200-step fit on arm a seed 401 (fit_local.sh), speed, peak GPU memory, rc -> LEASE/sm1_smoke.txt
#   cancel  after a passed smoke: cancel the Athena ViT-B/16 jobs 3545957 (array) and 3546034 (array) (A13)
#   queue   the 12 fits, one at a time, detached on the machine
#   pull    copy finished tars back to /mnt/t7/smad_next/SM1/results_rented/, verify sha256; RELEASE when 12 of 12
#   pullloop  pull every 10 minutes until RELEASE or the end of the queue (12 Nov fix)
#   status
# LEASE = the lead's lease folder (known_hosts, logs, RELEASE).
set -euo pipefail
HOST=${1:?host}; PORT=${2:?port}; L=${3:?lease folder}; STEP=${4:?step}
SRC=$(cd "$(dirname "$0")" && pwd)
KEY=${SM1_SSH_KEY:-/home/narolski/.config/smad-next/vast_ssh_key}
GP=/mnt/t7/smad_next/SM1/gpupack; AD4=/mnt/t7/smad_next/AD4
OUTD=/mnt/t7/smad_next/SM1/results_rented
mkdir -p "$L"
O=(-o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$L/known_hosts" -i "$KEY" -p "$PORT")
R() { ssh -n "${O[@]}" "root@$HOST" "$@"; }
RS() { rsync -a --partial --timeout=300 -e "ssh ${O[*]}" "$@"; }
B=/workspace/sm1r
TASKS="SM1B_a_s401 SM1B_c_s401 SM1B_e_s401 SM1B_f_s401 SM1B_a_s402 SM1B_c_s402 SM1B_e_s402 SM1B_f_s402 SM1B_b_s401 SM1B_bp_s401 SM1B_b_s402 SM1B_bp_s402"
# pinned sha256 of every pack (= the files on Athena packs/AD4 and packs/SM1, which the Athena fits use)
PACKS="ad4_pack:1ad170be30af949c55536f5dd6fff8c8c62b60f39b3faaa8bc134cb68967bfde
sm1lora_manifests_v2:5b1c41c19d29d2bdc9fe822ef550c985fc0cfc39d044a107f4c8faddfe59af4f
sm1lora_manifests_b:4441de74600d39a1bcb5062d3984cf601065368d69ddb66a262b66e3ff58270f
sm1lora_manifests_audit:4b58943acaa44b306d9950a86791d38a815e9b338926e0abbde5f8865cace1fe
sm1gpu_img_test:59cb6455eafc3bf93c2a40fd069aef4bc5832f275d1260451cebeed2fb29f758
sm1gpu_img_armsc:3df239359a5f43d6dcfbe906edbb9706d258666b79089862028448f495d6db22
sm1gpu_img_armsb:1d028856ba6e867e59a21a5638fe8fe38796e63cbfc03b46d13f69fe69573a38
sm1gpu_img_base:5c79a7b8f7b54062b0edcfbc77e0813b7305cb79e88642546535070992def51d
sm1gpu_img_armf:1267573e2ac1aa3b5e7c94275c2c231a319013f4fc3c02f1911c17e6b69ee7c1
sm1gpu_img_audit:344a6c32407e74cff10651da2135370024ab9e66d1eb32c799f87639b6456126
sm1gpu_img_arme:aeb57d6bc5aaa872474f9f62e0af8e08c1aa80684db288206fa86f4e7f3d090b
sm1gpu_img_jpegeval:ea7f7477d0ed21347cb51f611d849a5acf53004225e2b003e39cbd275886fd17"
log() { echo "$(date +%T) $*" | tee -a "$L/sm1_drive.log"; }
loc() { [ "$1" = ad4_pack ] && echo "$AD4/$1.tar" || echo "$GP/$1.tar"; }
case "$STEP" in
  setup)
    R "mkdir -p $B/in $B/bin $B/logs $B/results && nvidia-smi -L && nproc && df -h /workspace /dev/shm" | tee -a "$L/sm1_setup.log"
    RS "$SRC/remote_setup.sh" "$SRC/unpack_one.sh" "$SRC/fit_local.sh" "$SRC/remote_smoke.sh" "$SRC/remote_queue.sh" \
       "$SRC/../sm1_lora_audit.py" "root@$HOST:$B/bin/"
    R "bash $B/bin/remote_setup.sh" 2>&1 | tee -a "$L/sm1_setup.log"
    grep -q SETUP_OK "$L/sm1_setup.log" || { log "remote_setup failed"; exit 1; }
    T0=$SECONDS
    while IFS=: read -r -u 3 n pin; do
      f=$(loc "$n")
      [ "$(cut -c1-64 "$f.sha256")" = "$pin" ] || { log "local $n.tar.sha256 differs from the pin"; exit 1; }
      if R "[ -f $B/done/$n ]"; then log "skip $n (already unpacked)"; continue; fi
      need=$(( $(stat -c %s "$f") / 1000000000 + 5 ))
      avail=$(R "df --output=avail -B1G /workspace | tail -1" | tr -d ' ')
      [ "$avail" -ge "$need" ] || { log "disk: $avail GB free, $n needs $need GB"; exit 1; }
      t=$SECONDS
      RS "$f" "$f.sha256" "root@$HOST:$B/in/"
      R "bash $B/bin/unpack_one.sh $n" 2>&1 | tee -a "$L/sm1_setup.log" | tail -1
      R "[ -f $B/done/$n ]" || { log "unpack of $n failed"; exit 1; }
      log "pack $n uploaded + checked + unpacked in $((SECONDS - t)) s"
    done 3<<< "$PACKS"
    log "SETUP_DONE all packs in $((SECONDS - T0)) s"
    R "df -h /workspace | tail -1; ls $B/done" | tee -a "$L/sm1_setup.log"
    ;;
  smoke)
    R "bash $B/bin/remote_smoke.sh" 2>&1 | tee "$L/sm1_smoke.txt"
    RS "root@$HOST:$B/smoke/smoke_run.log" "root@$HOST:$B/smoke/gpumem.csv" "$L/" || true
    grep -q "SMOKE_RC=0" "$L/sm1_smoke.txt" && log "SMOKE passed" || { log "SMOKE failed"; exit 1; }
    ;;
  cancel)
    grep -q "SMOKE_RC=0" "$L/sm1_smoke.txt" || { log "no passed smoke: Athena jobs not cancelled"; exit 1; }
    flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes -o ConnectTimeout=20 plgpnarolski@athena.cyfronet.pl \
      'scancel 3545957 3546034; sleep 5; sacct -j 3545957,3546034 -X -n -o JobID,State | sort -u' 2>&1 | tee -a "$L/sm1_drive.log"
    log "Athena ViT-B/16 jobs 3545957 and 3546034 cancelled (A13)"
    ;;
  queue)
    # fixed 12 Nov: the whole "cd && nohup ... &" list was backgrounded in a subshell that kept the ssh session's
    # stdout open, so this ssh never returned and "all" never reached its pull loop
    R "cd $B; (nohup setsid bash $B/bin/remote_queue.sh \"$TASKS\" > $B/logs/queue_driver.log 2>&1 < /dev/null &) > /dev/null 2>&1; sleep 3; cat $B/QUEUE_STARTED"
    log "queue started: $TASKS"
    ;;
  pull)
    avail=$(df --output=avail -B1G /mnt/t7 | tail -1 | tr -d ' ')
    [ "$avail" -ge 1 ] || { log "T7 has under 1 GB free: not pulling"; exit 1; }
    mkdir -p "$OUTD/logs"
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results/" "$OUTD/" || true
    RS "root@$HOST:$B/logs/" "$OUTD/logs/" || true
    RS "root@$HOST:$B/queue.log" "$OUTD/logs/" 2>/dev/null || true
    n=0
    for t in $TASKS; do
      if [ -f "$OUTD/$t.tar" ] && [ -f "$OUTD/$t.tar.sha256" ]; then
        (cd "$OUTD" && sha256sum -c --quiet "$t.tar.sha256") && { n=$((n + 1)); echo "verified $t"; } || log "HASH MISMATCH $t"
      fi
    done
    log "verified $n of 12"
    if [ "$n" -eq 12 ]; then
      if [ -f "$L/DEV_PLANNED" ] && [ ! -f "$L/DEV_DONE" ]; then log "12 of 12, RELEASE held for the dev step (A15)";
      else touch "$L/RELEASE"; log "RELEASE written"; fi
    fi
    if R "[ -f $B/ALL_DONE ]" && [ "$n" -lt 12 ]; then log "queue finished with $n of 12 (see queue.log): RELEASE not written"; R "cat $B/queue.log" | tee -a "$L/sm1_drive.log"; fi
    ;;
  status)
    R "cat $B/queue.log 2>/dev/null; ls $B/results/; for f in $B/logs/SM1B_*.log; do echo \$f; grep -E 'it/s' \$f | tail -1 | cut -c1-160; done 2>/dev/null; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader; df -h /workspace | tail -1"
    ;;
  pullloop)                                                    # pull every 10 min until RELEASE (or queue end)
    for k in $(seq 1 120); do
      bash "$0" "$HOST" "$PORT" "$L" pull >> "$L/sm1_pull.log" 2>&1 || true
      [ -f "$L/RELEASE" ] && { log "ALL_DONE: 12 of 12 verified, RELEASE written"; break; }
      if R "[ -f $B/ALL_DONE ]" 2>/dev/null; then
        bash "$0" "$HOST" "$PORT" "$L" pull >> "$L/sm1_pull.log" 2>&1 || true
        [ -f "$L/RELEASE" ] && { log "ALL_DONE: 12 of 12 verified, RELEASE written"; break; }
        log "queue ended without 12 of 12; machine kept for inspection"; break
      fi
      sleep 600
    done
    ;;
  dev16fresh)                                                  # A16 (DRAFT): DG1 rungs on a fresh lease, development data only
    touch "$L/DEV_PLANNED"
    DV=/mnt/t7/smad_next/SM1/dev_a16; O16=$OUTD/dev16
    R "mkdir -p $B/in $B/bin $B/logs $B/results $B/manifests/dev16 && nvidia-smi -L && df -h /workspace" | tee -a "$L/sm1_setup.log"
    RS "$SRC/remote_setup.sh" "$SRC/unpack_one.sh" "$SRC/remote_dev16.sh" "$SRC/../sm1_lora_audit.py" "root@$HOST:$B/bin/"
    R "bash $B/bin/remote_setup.sh" 2>&1 | tee -a "$L/sm1_setup.log" | tail -2
    while IFS=: read -r -u 3 n pin; do
      case "$n" in ad4_pack|sm1gpu_img_test|sm1lora_manifests_v2) ;; *) continue ;; esac
      f=$(loc "$n"); [ "$(cut -c1-64 "$f.sha256")" = "$pin" ] || { log "pin $n"; exit 1; }
      R "[ -f $B/done/$n ]" || { RS "$f" "$f.sha256" "root@$HOST:$B/in/"; R "bash $B/bin/unpack_one.sh $n" | tail -1; }
    done 3<<< "$PACKS"
    for t in SM1B_a_s401 SM1B_a_s402 SM1B_e_s401 SM1B_e_s402 SM1B_f_s401 SM1B_f_s402; do
      RS "$OUTD/$t.tar" "$OUTD/$t.tar.sha256" "root@$HOST:$B/results/"
    done
    R "cd $B/results && sha256sum -c *.sha256 && date > $B/ALL_DONE"
    RS "$DV/sm1_dev16_eval.csv" "$DV/sm1_dev16_eval.csv.sha256" "$DV/dev16_files.sha256" "root@$HOST:$B/manifests/dev16/"
    (cd / && tar -cf - -T "$DV/filelist_dev16.txt" 2>/dev/null) | ssh "${O[@]}" "root@$HOST" "tar -xf - -C $B/data/x"
    R "cd $B; (nohup setsid bash $B/bin/remote_dev16.sh > $B/logs/dev16.log 2>&1 < /dev/null &) > /dev/null 2>&1; sleep 2; echo started"
    for k in $(seq 1 60); do R "[ -f $B/results_dev16/SM1E_ALL_DONE ]" && break; sleep 120; done
    mkdir -p "$O16"
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_dev16/" "$O16/"
    RS "root@$HOST:$B/logs/" "$O16/machine_logs/" || true
    nd=$(cd "$O16" && sha256sum -c --quiet SM1E_*.sha256 2>/dev/null && ls SM1E_*.tar | wc -l)
    log "dev16 results verified: ${nd:-0} of 6"
    if [ "${nd:-0}" -eq 6 ]; then touch "$L/DEV_DONE"
      if [ -n "${SM1_NO_RELEASE:-}" ]; then log "dev16 6 of 6, logs copied; RELEASE not written (SM1_NO_RELEASE: lease reused)";
      else touch "$L/RELEASE"; log "RELEASE written (dev16 6 of 6, logs copied)"; fi
    fi
    ;;
  hn2fresh)                                                    # H-n2 (DRAFT A18): train on DG1 shards 0-5, test 6-7
    DV=/mnt/t7/smad_next/SM1/hn2; OH=$OUTD/hn2
    R "mkdir -p $B/in $B/bin $B/logs $B/manifests/hn2 $B/data/x && nvidia-smi -L && df -h /workspace" | tee -a "$L/sm1_setup.log"
    RS "$SRC/remote_setup.sh" "$SRC/unpack_one.sh" "$SRC/fit_hn2.sh" "$SRC/remote_hn2.sh" "root@$HOST:$B/bin/"
    R "bash $B/bin/remote_setup.sh" 2>&1 | tee -a "$L/sm1_setup.log" | tail -2
    f=$(loc ad4_pack); [ "$(cut -c1-64 "$f.sha256")" = "$(echo "$PACKS" | grep ^ad4_pack | cut -d: -f2)" ] || { log "pin ad4_pack"; exit 1; }
    R "[ -f $B/done/ad4_pack ]" || { RS "$f" "$f.sha256" "root@$HOST:$B/in/"; R "bash $B/bin/unpack_one.sh ad4_pack" | tail -1; }
    RS "$DV/sm1_hn2_manifests.tar" "$DV/sm1_hn2_manifests.tar.sha256" "root@$HOST:$B/manifests/hn2/"
    R "cd $B/manifests/hn2 && sha256sum -c sm1_hn2_manifests.tar.sha256 && tar -xf sm1_hn2_manifests.tar && rm sm1_hn2_manifests.tar"
    (cd / && tar -cf - -T "$DV/filelist_hn2.txt" 2>/dev/null) | ssh "${O[@]}" "root@$HOST" "tar -xf - -C $B/data/x"
    R "cd $B/data/x && sha256sum -c --quiet $B/manifests/hn2/hn2_files.sha256 && echo DG1_FILES_OK"
    R "cd $B; (nohup setsid bash $B/bin/remote_hn2.sh > $B/logs/hn2_queue_driver.log 2>&1 < /dev/null &) > /dev/null 2>&1; sleep 2; echo started"
    log "hn2 queue started (smoke, then 4 fits)"
    mkdir -p "$OH"
    for k in $(seq 1 120); do
      sleep 600
      RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_hn2/" "$OH/" 2>/dev/null || true
      RS "root@$HOST:$B/logs/" "$OH/machine_logs/" 2>/dev/null || true
      R "[ -f $B/results_hn2_FAILED ]" && { log "hn2 smoke failed: machine kept, see machine_logs"; exit 1; }
      if R "[ -f $B/results_hn2/HN2_ALL_DONE ]"; then
        RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_hn2/" "$OH/"
        RS "root@$HOST:$B/logs/" "root@$HOST:$B/queue_hn2.log" "$OH/machine_logs/" || true
        nh=$(cd "$OH" && sha256sum -c --quiet HN2_*.sha256 2>/dev/null && ls HN2_*_s40?.tar | wc -l)
        log "hn2 verified ${nh:-0} of 4"
        [ "${nh:-0}" -eq 4 ] && { touch "$L/RELEASE"; log "RELEASE written (4 of 4 fits and logs back)"; }
        break
      fi
    done
    ;;
  devfresh)                                                    # A15 on another host: minimal packs + the 6 fit tars, then dev
    R "mkdir -p $B/in $B/bin $B/logs $B/results && nvidia-smi -L && nproc && df -h /workspace" | tee -a "$L/sm1_setup.log"
    RS "$SRC/remote_setup.sh" "$SRC/unpack_one.sh" "$SRC/remote_dev.sh" "$SRC/../sm1_lora_audit.py" "root@$HOST:$B/bin/"
    R "bash $B/bin/remote_setup.sh" 2>&1 | tee -a "$L/sm1_setup.log" | tail -2
    while IFS=: read -r -u 3 n pin; do
      case "$n" in ad4_pack|sm1gpu_img_test|sm1lora_manifests_v2) ;; *) continue ;; esac
      f=$(loc "$n"); [ "$(cut -c1-64 "$f.sha256")" = "$pin" ] || { log "pin $n"; exit 1; }
      R "[ -f $B/done/$n ]" || { RS "$f" "$f.sha256" "root@$HOST:$B/in/"; R "bash $B/bin/unpack_one.sh $n" | tail -1; }
    done 3<<< "$PACKS"
    for t in SM1B_a_s401 SM1B_a_s402 SM1B_e_s401 SM1B_e_s402 SM1B_f_s401 SM1B_f_s402; do
      RS "$OUTD/$t.tar" "$OUTD/$t.tar.sha256" "root@$HOST:$B/results/"
    done
    R "cd $B/results && sha256sum -c *.sha256 && date > $B/ALL_DONE"
    bash "$0" "$HOST" "$PORT" "$L" dev
    ;;
  dev)                                                         # A15 draft: development-data scoring (after the queue)
    touch "$L/DEV_PLANNED"                                      # holds RELEASE until DEV_DONE
    DV=/mnt/t7/smad_next/SM1/dev_a14
    R "mkdir -p $B/manifests/dev"
    RS "$DV/sm1_dev_eval.csv" "$DV/sm1_dev_eval.csv.sha256" "$DV/dev_files.sha256" "root@$HOST:$B/manifests/dev/"
    RS "$SRC/remote_dev.sh" "$SRC/../sm1_lora_audit.py" "root@$HOST:$B/bin/"   # fixed: the scorer with --check-npz
    R "rm -f $B/results_dev/SM1D_ALL_DONE"
    (cd / && tar -cf - -T "$DV/filelist_dev.txt" 2>/dev/null) | ssh "${O[@]}" "root@$HOST" "tar -xf - -C $B/data/x"
    log "dev files streamed ($(wc -l < "$DV/filelist_dev.txt") files)"
    R "cd $B; (nohup setsid bash $B/bin/remote_dev.sh > $B/logs/dev.log 2>&1 < /dev/null &) > /dev/null 2>&1; sleep 2; echo dev started"
    log "dev started detached on the machine (waits for the queue's ALL_DONE)"
    for k in $(seq 1 60); do R "[ -f $B/results_dev/SM1D_ALL_DONE ]" && break; sleep 300; done
    mkdir -p "$OUTD/dev"
    RS --include='*.tar' --include='*.tar.sha256' --exclude='*' "root@$HOST:$B/results_dev/" "$OUTD/dev/"
    RS "root@$HOST:$B/logs/dev.log" "$OUTD/dev/" || true
    (cd "$OUTD/dev" && sha256sum -c *.sha256) | tee -a "$L/sm1_drive.log"
    nd=$(cd "$OUTD/dev" && sha256sum -c --quiet *.sha256 2>/dev/null && ls SM1D_*.tar | wc -l)
    log "dev results verified: ${nd:-0} of 6"; [ "${nd:-0}" -eq 6 ] && touch "$L/DEV_DONE"
    [ -f "$L/DEV_DONE" ] && bash "$0" "$HOST" "$PORT" "$L" pull
    ;;
  all)
    bash "$0" "$HOST" "$PORT" "$L" setup
    bash "$0" "$HOST" "$PORT" "$L" smoke
    bash "$0" "$HOST" "$PORT" "$L" cancel
    bash "$0" "$HOST" "$PORT" "$L" queue
    for k in $(seq 1 120); do                                # pull every 10 minutes, at most 20 h
      sleep 600
      bash "$0" "$HOST" "$PORT" "$L" pull >> "$L/sm1_pull.log" 2>&1 || true
      [ -f "$L/RELEASE" ] && { log "ALL_DONE: 12 of 12 verified, RELEASE written"; break; }
      if R "[ -f $B/ALL_DONE ]" 2>/dev/null; then bash "$0" "$HOST" "$PORT" "$L" pull >> "$L/sm1_pull.log" 2>&1 || true; [ -f "$L/RELEASE" ] || { log "queue ended without 12 of 12; machine kept for inspection"; break; }; fi
    done
    ;;
  *) echo "step $STEP"; exit 1 ;;
esac

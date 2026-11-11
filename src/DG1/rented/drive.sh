#!/bin/bash
# Diffusion-autoencoder generation (DG1), amendment 3: drive ONE rented Docker machine from the DGX (lead's session).
#   bash /home/narolski/smad-next/src/DG1/rented/drive.sh HOST PORT LEASE_FOLDER
# 1 upload the base pack (2.88 GB), the add-on pack and remote_run.sh (rsync, resumable), sha check on the machine;
# 2 setup (pinned environment); 3 the registered 8-image equivalence gate (eq.csv) against the stored DGX A43 files,
#   read on the DGX with dg1_validity.py equiv (every image's mean |difference| <= 2 grey levels) -- stop if it fails;
# 4 add-on shards 2..7: a shard whose Athena task (3545907_K) is already running or finished is left to Athena;
#   otherwise it runs on the machine, its image tar is copied back to /mnt/t7/smad_next/DG1/rented_results/, sha-verified,
#   unpacked to /mnt/t7/smad_next/DG1/gen/addon_sK/ with PLATFORM.txt, and the Athena task is cancelled. Codes tars
#   are copied back only while /mnt/t7 keeps > 55 GB free. 5 RELEASE written into the lease folder (also on a failure
#   exit, so the guard stops the rental; the reason is in LEASE_FOLDER/dg1_drive.log).
set -uo pipefail
H=$1; PT=$2; L=$3
KEY=/home/narolski/.config/smad-next/vast_ssh_key
SSH="ssh -i $KEY -p $PT -o BatchMode=yes -o UserKnownHostsFile=$L/known_hosts -o StrictHostKeyChecking=yes -o ServerAliveInterval=30"
D=/mnt/t7/smad_next/DG1; S=/home/narolski/smad-next/src/DG1; E=/home/narolski/smad-next/experiments/DG1_diffusion-generation-athena
OUT=$D/rented_results; P=/home/narolski/mambamorph-code/.venv-spark/bin/python
ATH="flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes -o ConnectTimeout=20 plgpnarolski@athena.cyfronet.pl"
mkdir -p "$OUT"
exec > >(tee -a "$L/dg1_drive.log") 2>&1
r() { $SSH root@$H "$@"; }
log() { echo "$(date +%H:%M:%S) $*"; }
getlogs() { mkdir -p "$L/remote_logs"; rsync -a -e "$SSH" "root@$H:/root/dg1/*.log" "root@$H:/root/dg1/out_*/*.log" "$L/remote_logs/" 2>/dev/null; log "remote logs copied to $L/remote_logs/ ($(ls "$L/remote_logs" 2>/dev/null | tr '\n' ' '))"; }
finish() { [ "${2:-0}" = 0 ] || getlogs; touch "$L/RELEASE"; log "RELEASE written ($1)"; echo "DRIVE_END $1"; exit "${2:-0}"; }
hold() { getlogs; log "NO RELEASE: machine kept up for a fix ($1); the guard still stops it at the cap"; echo "DRIVE_HOLD $1"; exit "${2:-1}"; }
log "start host $H port $PT lease $L"
r 'hostname; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader; df -h /root | tail -1' || finish "no ssh" 1
r 'mkdir -p /root/dg1/packs /root/dg1/results'
for f in dg1_pack.tar dg1_pack.tar.sha256 dg1_addon_pack.tar dg1_addon_pack.tar.sha256; do
  ok=0; for k in 1 2 3 4 5; do rsync -a --partial -e "$SSH" "$D/packs/$f" root@$H:/root/dg1/packs/ && { ok=1; break; }; log "retry $f $k"; sleep 15; done
  [ $ok = 1 ] || finish "upload of $f failed" 2
done
rsync -a -e "$SSH" "$S/rented/remote_run.sh" root@$H:/root/dg1/ || finish "upload of remote_run.sh failed" 2
log "uploaded"
r 'bash /root/dg1/remote_run.sh setup > /root/dg1/setup.log 2>&1; tail -4 /root/dg1/setup.log; grep -q SETUP_OK /root/dg1/setup.log' || hold "setup failed (see $L/remote_logs/setup.log)" 3
rsync -a -e "$SSH" root@$H:/root/dg1/versions.txt "$OUT/versions_rented.txt"

remote_task() {   # $1 = remote_run.sh arguments, $2 = tag; waits for the end, fetches the image tar, verifies
  local args=$1 tag=$2
  r "cd /root/dg1 && nohup bash -c 'bash remote_run.sh $args; echo EXIT_CODE \$?' > /root/dg1/run_$tag.log 2>&1 &"
  until r "grep -q '^EXIT_CODE' /root/dg1/run_$tag.log"; do sleep 60; done
  r "tail -4 /root/dg1/run_$tag.log"
  rsync -a -e "$SSH" root@$H:/root/dg1/results/DG1_$tag.tar root@$H:/root/dg1/results/DG1_$tag.tar.sha256 root@$H:/root/dg1/run_$tag.log "$OUT/" || return 1
  ( cd "$OUT" && sha256sum -c "DG1_$tag.tar.sha256" ) || return 1
  r "grep -q '^EXIT_CODE 0' /root/dg1/run_$tag.log" || return 2
}

# ---- equivalence gate (registered reading)
remote_task eq eq_rented || finish "equivalence images failed" 4
rm -rf "$D/gen/eq_rented"; mkdir -p "$D/gen/eq_rented" && tar -C "$D/gen/eq_rented" -xf "$OUT/DG1_eq_rented.tar"
$P -I "$S/dg1_validity.py" equiv --gen "$D/gen/eq_rented/out_eq_rented/eq" --ref /mnt/t7/smad_heldout/a43/gen \
  --out "$E/equivalence_rented.json" 2>&1 | grep -v -i "warn\|x = x\|tform\|provider\|model ignore\|find model\|set det" | tail -14
$P -I -c "import json,sys; d=json.load(open('$E/equivalence_rented.json')); sys.exit(0 if d['equivalent'] else 1)" \
  || finish "EQUIVALENCE GATE FAILED: no rented shard is produced" 5
log "GATE_PASSED"

# ---- add-on shards 2..7, one platform per shard
for K in 2 3 4 5 6 7; do
  # an array element that has not started appears only inside the range line (e.g. 3545907_[2-7] PENDING)
  st=$($ATH "sacct -j 3545907 -X -n -P -o JobID,State 2>/dev/null" | python3 -c "
import sys, re
k = '$K'; st = ''
for ln in sys.stdin:
    jid, _, state = ln.strip().partition('|')
    if jid == '3545907_' + k: st = state; break
    m = re.fullmatch(r'3545907_\\[(.*)\\]', jid)
    if m and not st:
        for part in m.group(1).split('%')[0].split(','):
            a, _, b = part.partition('-')
            if int(a) <= int(k) <= int(b or a): st = state
print(st.split()[0] if st else '')")
  log "shard $K: Athena task state '${st:-unknown}'"
  case "$st" in RUNNING*|COMPLETED*|COMPLETING*) log "shard $K left to Athena"; continue ;; esac
  [ -n "$st" ] || { log "shard $K: Athena state unknown, left to Athena"; continue; }
  if ! remote_task "shard $K" "addon_s$K"; then log "shard $K FAILED on the rented machine; Athena task kept"; continue; fi
  T=$D/gen/addon_s$K
  if [ -e "$T" ]; then log "shard $K: $T exists (Athena copy?), rented tar kept unpacked only in $OUT"; continue; fi
  mkdir -p "$T" && tar -C "$T" -xf "$OUT/DG1_addon_s$K.tar"
  echo "rented $H (lease $L); $(head -2 "$T/out_addon_s$K/host.txt" | tr '\n' ' ')" > "$T/PLATFORM.txt"
  $ATH "scancel 3545907_$K; sacct -j 3545907_$K -X -n -o State | head -1" && log "Athena task 3545907_$K cancelled"
  free=$(df -BG --output=avail /mnt/t7 | tail -1 | tr -dc 0-9)
  if [ "${free:-0}" -gt 35 ]; then
    rsync -a -e "$SSH" root@$H:/root/dg1/results/DG1_addon_s${K}_codes.tar root@$H:/root/dg1/results/DG1_addon_s${K}_codes.tar.sha256 "$OUT/" \
      && ( cd "$OUT" && sha256sum -c "DG1_addon_s${K}_codes.tar.sha256" ) && log "shard $K codes copied"
  else
    log "shard $K codes NOT copied (/mnt/t7 free ${free} GB <= 56)"; r "cat /root/dg1/results/DG1_addon_s${K}_codes.tar.sha256" >> "$OUT/codes_not_copied.sha256"
  fi
  log "shard $K DONE ($(find "$T" -name '*.png' | wc -l) png)"
done
finish "all shards handled" 0

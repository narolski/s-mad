#!/bin/bash
# AG1 on a rented Docker machine, driven from the DGX after the lead's one upload command.
#   drive_v2.sh HOST PORT LEASE_FOLDER   (= drive.sh + mkdir of logs/ and results/ before setup; use for any restart;
#   drive.sh is left byte-identical while the first run, PID 3080694, reads it)
# 1 setup (remote_run.sh setup); 2 first check: AG1_smoke_mip1 on the rented GPU vs Athena's (compare_smoke.py);
# 3 the remaining shards in order (core first, graded mixing and spread last); after each: fetch its tar + sha256 + log
# to /mnt/t7/smad_next/AG1/results/ (one at a time, only with >= MINFREE GB free), check the hash, process it
# (ag1_manifest.py shard, thread caps), add a ledger line, remove the local tar (the rented copy stays until RELEASE),
# then cancel the matching queued Athena task. On any failure: copy remote logs to LEASE/remote_logs and stop; RELEASE
# is written only after every shard is fetched and processed (never on a setup or check failure).
set -uo pipefail
H=$1; PT=$2; L=$3
K=/home/narolski/.config/smad-next/vast_ssh_key
SSH="ssh -i $K -p $PT -o BatchMode=yes -o UserKnownHostsFile=$L/known_hosts -o StrictHostKeyChecking=yes -o ServerAliveInterval=30"
S=/home/narolski/smad-next/src/AG1
B=/mnt/t7/smad_next/AG1; R=$B/results; LEDGER=/home/narolski/smad-next/experiments/AG1/fetched_tars.csv
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
MINFREE=${MINFREE:-30}                  # lead, 12 Nov: the T7 drive had 33 GB free; one tar (<= 1.1 GB) at a time
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
r() { $SSH root@$H "$@"; }
log() { echo "$(date +%F_%T) $*" | tee -a "$L/ag1_drive.log"; }
fail() { log "FAILED: $1"; mkdir -p "$L/remote_logs"; rsync -a -e "$SSH" root@$H:/root/ag1/logs/ "$L/remote_logs/" 2>/dev/null; exit "${2:-1}"; }
# queued Athena task of each shard (cancelled once the rented copy is verified and processed)
declare -A ATH=([AG1_mip1_frgc_01]=3544797_5 [AG1_mip2_frll_00]=3544797_6 [AG1_mip2_frll_01]=3544797_7
  [AG1_mip1_feret_ag3_00]=3544798_0 [AG1_mip1_feret_ag3_01]=3544798_1 [AG1_mip1_frgc_ag3_00]=3544799_2
  [AG1_mip1_frgc_ag3_01]=3544799_3 [AG1_spread_mip1_frll]=3545819_0 [AG1_spread_mip1_feret]=3545819_1
  [AG1_spread_mip1_frgc]=3545819_2 [AG1_spread_mip2_frll]=3545819_3)
ORDER=(AG1_mip1_frgc_01 AG1_mip2_frll_00 AG1_mip2_frll_01 AG1_mip1_feret_ag3_00 AG1_mip1_feret_ag3_01
  AG1_mip1_frgc_ag3_00 AG1_mip1_frgc_ag3_01 AG1_spread_mip1_frll AG1_spread_mip1_feret AG1_spread_mip1_frgc
  AG1_spread_mip2_frll)
mkdir -p "$L" "$R"
run_remote() {  # $1 = remote_run.sh arguments, $2 = tag; nohup + poll so a dropped SSH session does not kill it
  r "cd /root/ag1 && nohup bash -c 'bash upload/remote_run.sh $1; echo EXIT_CODE \$?' > logs/run_$2.out 2>&1 &" || return 1
  until r "grep -q '^EXIT_CODE' /root/ag1/logs/run_$2.out" 2>/dev/null; do sleep 60; done
  r "tail -4 /root/ag1/logs/run_$2.out"
  r "grep -q '^EXIT_CODE 0' /root/ag1/logs/run_$2.out"
}
fetch() {  # $1 = shard name -> verified local tar
  local free; free=$(df --output=avail -BG /mnt/t7 | tail -1 | tr -dc 0-9)
  [ "$free" -ge "$MINFREE" ] || fail "only ${free} GB free on /mnt/t7 (floor $MINFREE)" 9
  rsync -a -e "$SSH" root@$H:/root/ag1/results/$1.tar root@$H:/root/ag1/results/$1.tar.sha256 root@$H:/root/ag1/results/$1.log.csv "$R/" || return 1
  [ "$(sha256sum "$R/$1.tar" | cut -c1-64)" = "$(cut -c1-64 "$R/$1.tar.sha256")" ]
}
log "machine"; r 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; df -h /root | tail -1; ls -la /root/ag1/upload' | tee -a "$L/ag1_drive.log" || fail "no ssh / no upload" 2
r 'mkdir -p /root/ag1/logs /root/ag1/results' || fail "mkdir on the machine" 2      # 12 Nov: upload creates only upload/
log "setup"; r 'cd /root/ag1 && bash upload/remote_run.sh setup > logs/setup.out 2>&1; tail -3 logs/setup.out; grep -q SETUP_OK logs/setup.out' || fail "setup" 3
rsync -a -e "$SSH" root@$H:/root/ag1/logs/versions.txt root@$H:/root/ag1/logs/pip_freeze.txt root@$H:/root/ag1/logs/gpu.txt "$L/" 2>/dev/null
log "first check: smoke shard on the rented GPU"
run_remote "shard AG1_smoke_mip1" smoke || fail "smoke shard" 4
mkdir -p "$L/check"
[ -s "$L/check/rented_AG1_smoke_mip1.tar" ] && mv "$L/check/rented_AG1_smoke_mip1.tar" "$L/check/rented_AG1_smoke_mip1_$(date +%H%M%S).tar"
rsync -a -e "$SSH" root@$H:/root/ag1/results/AG1_smoke_mip1.tar "$L/check/rented_AG1_smoke_mip1.tar" || fail "fetch smoke" 4
[ -s "$L/check/compare.txt" ] && mv "$L/check/compare.txt" "$L/check/compare_$(date +%H%M%S).txt"
$P -I $S/rented/compare_smoke.py "$L/check/rented_AG1_smoke_mip1.tar" "$R/AG1_smoke_mip1.tar" "${RENTED_RULE:-strict}" | tee "$L/check/compare.txt"
grep -q "^PASS" "$L/check/compare.txt" || fail "first check did not pass (see $L/check/compare.txt)" 5
log "CHECK_PASSED"
for n in "${ORDER[@]}"; do
  if [ -s "$B/data/shards/$n.json" ]; then log "$n already processed (Athena or earlier run)"; continue; fi
  case $n in
    AG1_spread_*) g=${n#AG1_spread_}; run_remote "spread ${g%%_*} ${g#*_}" "$n" || fail "$n" 6 ;;
    *) run_remote "shard $n" "$n" || fail "$n" 6 ;;
  esac
  fetch "$n" || fail "fetch / hash $n" 7
  nice -n 10 $P $S/ag1_manifest.py shard "$R/$n.tar" >> "$L/ag1_drive.log" 2>&1 || fail "processing $n" 8
  echo "$n,$(cut -c1-64 "$R/$n.tar.sha256"),$(stat -c %s "$R/$n.tar"),$(date +%FT%T),rented" >> "$LEDGER"
  rm -f "$R/$n.tar"
  log "$n processed; local tar removed (copy on the rented machine until RELEASE)"
  flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl "scancel ${ATH[$n]}" \
    && log "Athena task ${ATH[$n]} cancelled" || log "WARNING: could not cancel Athena ${ATH[$n]} (cancel by hand)"
done
rsync -a -e "$SSH" root@$H:/root/ag1/logs/ "$L/remote_logs/" 2>/dev/null
touch "$L/RELEASE" && log "RELEASE written"
echo DRIVE_DONE

#!/bin/bash
# Own-crop re-score of the audit rows (RS1), amendment 5: drive the rented Docker machine from the DGX.
#   drive.sh HOST PORT LEASE_FOLDER
# 1 upload packs + SMDD script + run script (rsync, resumable), 2 setup, 3 8-image smoke of both variants and compare
# with Athena smoke 3545869 (max |logit difference|), 4 variant 1 then variant 2 in full, each small result tar copied
# back to /mnt/t7/smad_next/RS1/results_rented/ and sha-verified; crops stay on the machine. Writes RELEASE at the end.
set -uo pipefail
H=$1; PT=$2; L=$3
K=/home/narolski/.config/smad-next/vast_ssh_key
SSH="ssh -i $K -p $PT -o BatchMode=yes -o UserKnownHostsFile=$L/known_hosts -o StrictHostKeyChecking=yes -o ServerAliveInterval=30"
A=/mnt/t7/smad_next/RS1/athena; S=/home/narolski/smad-next/src/RS1; OUT=/mnt/t7/smad_next/RS1/results_rented
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
mkdir -p $OUT
r() { $SSH root@$H "$@"; }
log() { echo "$(date +%H:%M:%S) $*"; }
log "disk / gpu"; r 'df -h /root | tail -1; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader' || exit 1
r 'mkdir -p /root/rs1/packs /root/rs1/results'
if r 'test -f /root/rs1/pack/.unpacked'; then
  log "packs already unpacked and hash-checked on the machine; upload skipped"
  rsync -a -e "$SSH" /mnt/t7/thirdparty/smdd_9683229_20261107/image_preprocess.py $S/rented/rs1_run.sh root@$H:/root/rs1/ || exit 1
else
for f in rs1a_pack.tar rs1a_pack.tar.sha256 rs1a_pack_amend.tar rs1a_pack_amend.tar.sha256 rs1a_pack_raw.tar rs1a_pack_raw.tar.sha256; do
    for k in 1 2 3 4 5; do rsync -a --partial -e "$SSH" $A/$f root@$H:/root/rs1/packs/ && break; log "retry $f $k"; sleep 10; done
  done
  rsync -a -e "$SSH" /mnt/t7/thirdparty/smdd_9683229_20261107/image_preprocess.py $S/rented/rs1_run.sh root@$H:/root/rs1/ || exit 1
  log "packs uploaded"; r 'cd /root/rs1/packs && sha256sum -c rs1a_pack.tar.sha256 rs1a_pack_amend.tar.sha256 rs1a_pack_raw.tar.sha256; df -h /root | tail -1' || exit 3
fi
log "setup"; r 'bash /root/rs1/rs1_run.sh setup > /root/rs1/setup.log 2>&1; tail -3 /root/rs1/setup.log' || exit 4
rsync -a -e "$SSH" root@$H:/root/rs1/setup_versions.txt root@$H:/root/rs1/setup_pip_freeze.txt $OUT/
run_variant() {  # $1 = v1|v2, $2 = limit
  r 'df -h /root | tail -1; nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader'
  local tag=$([ "$2" = 0 ] && echo prod || echo smoke)_$1_rented
  r "cd /root/rs1 && nohup bash -c 'RS1_VARIANT=$1 RS1_LIMIT=$2 bash rs1_run.sh run; echo EXIT_CODE \$?' > /root/rs1/run_$tag.log 2>&1 &"
  until r "grep -q '^EXIT_CODE' /root/rs1/run_$tag.log"; do sleep 60; done
  r "tail -5 /root/rs1/run_$tag.log"
  r "grep -q '^EXIT_CODE 0' /root/rs1/run_$tag.log" || return 1
  rsync -a -e "$SSH" root@$H:/root/rs1/results/rs1a_$tag.tar root@$H:/root/rs1/results/rs1a_$tag.tar.sha256 root@$H:/root/rs1/run_$tag.log $OUT/ || return 1
grep -q "^PASS" $OUT/smoke_compare.txt || { if [ "${RS1_GATE_DESCRIPTIVE:-0}" = 1 ]; then log "smoke comparison not passed; continuing because the lead made the comparison descriptive (all rows come from this one machine)"; else log "smoke comparison failed; stopping before production"; exit 6; fi; }
  mkdir -p $OUT/$tag && tar -xf $OUT/rs1a_$tag.tar -C $OUT/$tag && log "fetched $tag"
}
run_variant v1 8 && run_variant v2 8 || { log "smoke failed"; exit 5; }
$P -I $S/rented/compare_smoke.py $OUT/smoke_v1_rented $OUT/smoke_v2_rented $A/smoke_3545869 | tee $OUT/smoke_compare.txt
if [ "${RS1_GATE:-strict}" = descriptive ]; then log "gate descriptive (lead's amendment): comparison recorded, production proceeds"
else grep -q "^PASS" $OUT/smoke_compare.txt || { log "smoke comparison failed; stopping before production"; exit 6; }; fi
log "SMOKE_PASSED"
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl 'scancel 3545972 3545973; squeue -u plgpnarolski -h -o "%i %T" | grep "354597[23]" || echo cancelled' && log "Athena 3545972/3545973 cancelled"
run_variant v1 0 || exit 7
run_variant v2 0 || exit 8
touch $L/RELEASE && log "RELEASE written"
echo DRIVE_DONE

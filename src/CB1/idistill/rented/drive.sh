#!/bin/bash
# CB1 IDistill rented variant: drive from the DGX.  drive.sh HOST PORT LEASE_FOLDER   (not run)
# Runs the WCSS job script unchanged as a plain bash script (CB1_L, TMPDIR, CB1_PIP=online), stage by stage; after each
# stage the result tar + sha256 are fetched to /mnt/t7/smad_next/CB1/results_rented/ and verified; RELEASE only at the end.
set -uo pipefail
H=$1; PT=$2; L=$3; mkdir -p "$L"
K=/home/narolski/.config/smad-next/vast_ssh_key
SSH="ssh -i $K -p $PT -o BatchMode=yes -o UserKnownHostsFile=$L/known_hosts -o StrictHostKeyChecking=yes -o ServerAliveInterval=30"
R=/mnt/t7/smad_next/CB1/results_rented; mkdir -p $R
log() { echo "$(date +%F_%T) $*" | tee -a "$L/drive.log"; }
fail() { log "FAILED: $1"; rsync -a -e "$SSH" root@$H:/root/cb1/logs/ "$L/remote_logs/" 2>/dev/null; exit 1; }
stage() {  # $1 = env assignments, $2 = tag (result tar name)
  $SSH root@$H "mkdir -p /root/cb1/logs && cd /root/cb1 && nohup bash -c 'env CB1_L=/root/cb1/smad-next TMPDIR=/root/cb1/tmp/$2 CB1_PIP=online $1 bash smad-next/jobs_cb1/cb1_idistill.sbatch; echo EXIT_CODE \$?' > logs/$2.out 2>&1 &" || return 1
  until $SSH root@$H "grep -q '^EXIT_CODE' /root/cb1/logs/$2.out" 2>/dev/null; do sleep 120; done
  $SSH root@$H "tail -5 /root/cb1/logs/$2.out; grep -q '^EXIT_CODE 0' /root/cb1/logs/$2.out" || return 1
  rsync -a -e "$SSH" root@$H:/root/cb1/smad-next/results/CB1/$2.tar root@$H:/root/cb1/smad-next/results/CB1/$2.tar.sha256 $R/ || return 1
  ( cd $R && sha256sum -c $2.tar.sha256 ) && cat $R/$2.tar.sha256 >> /home/narolski/smad-next/experiments/CB1_competitor-baselines-corrected-mad22/rented_tars.sha256
  $SSH root@$H "rm -rf /root/cb1/tmp/$2"
}
$SSH root@$H 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader; nproc; df -h /root | tail -1; python3 --version' | tee -a "$L/drive.log" || fail "ssh"
stage "STAGE=ae" idistill_ae || fail "autoencoder stage"
log "AE fetched and verified"
if [ "${DRIVE_PARALLEL:-0}" = 1 ]; then
  for s in 401 402 403; do ( stage "STAGE=cls SEED=$s" idistill_cls_s$s && log "seed $s fetched" || log "seed $s FAILED" ) & done; wait
else
  for s in 401 402 403; do stage "STAGE=cls SEED=$s" idistill_cls_s$s || fail "classifier seed $s"; log "seed $s fetched and verified"; done
fi
for s in 401 402 403; do [ -s $R/idistill_cls_s$s.tar ] || fail "seed $s result missing"; done
rsync -a -e "$SSH" root@$H:/root/cb1/logs/ "$L/remote_logs/" 2>/dev/null
touch "$L/RELEASE" && log "RELEASE written (all result tars on /mnt/t7, hashes verified)"

#!/bin/bash
# Retrains of released methods (AD5), rented variant (MADation ViT-B/16, 5 seeds on ONE GPU type, one card per run).
#   upload.sh HOST PORT LEASE       (LEASE = /mnt/t7/smad_next/vast/<name>, holds known_hosts; key as the lead's tooling)
# Sends the same packs as WCSS (code, cp39 wheels, Athena crop pack, each with .sha256) and the job script to
# /root/ad5/packs on the machine, then checks the hashes there.
set -euo pipefail
H=$1; P=$2; LD=$3; K=/home/narolski/.config/smad-next/vast_ssh_key; D=/mnt/t7/smad_next/AD5/wcss
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$LD/known_hosts -i $K -p $P"
$SSH root@$H 'mkdir -p /root/ad5/packs /root/ad5/results /root/ad5/logs'
rsync -a --partial -e "$SSH" $D/ad5w_code.tar $D/ad5w_code.tar.sha256 $D/ad5w_wheels39.tar $D/ad5w_wheels39.tar.sha256 \
  $D/smdd_train_cropped.tar $D/smdd_train_cropped.tar.sha256 /home/narolski/smad-next/src/AD5/wcss/ad5w_train.sbatch \
  /home/narolski/smad-next/src/AD5/rented/remote_run.sh root@$H:/root/ad5/packs/
$SSH root@$H 'cd /root/ad5/packs && sha256sum -c *.sha256' | tee -a $LD/ad5_upload.log

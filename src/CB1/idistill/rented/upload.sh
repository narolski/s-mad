#!/bin/bash
# CB1 IDistill rented variant: upload.  upload.sh HOST PORT LEASE_FOLDER   (not run; author's budget decision pending)
set -euo pipefail
H=$1; PT=$2; L=$3; mkdir -p "$L"
K=/home/narolski/.config/smad-next/vast_ssh_key
SSH="ssh -i $K -p $PT -o BatchMode=yes -o UserKnownHostsFile=$L/known_hosts -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30"
P=/mnt/t7/smad_next/CB1/packs; A=/mnt/t7/smad_next/AD5/wcss
$SSH root@$H 'mkdir -p /root/cb1/smad-next/packs/CB1 /root/cb1/smad-next/jobs_cb1 /root/cb1/smad-next/results/CB1 /root/cb1/tmp'
rsync -a --partial -e "$SSH" $P/idistill_code.tar $P/idistill_code.tar.sha256 $P/idistill_data.tar $P/idistill_data.tar.sha256 \
  $A/smdd_train_cropped.tar $A/smdd_train_cropped.tar.sha256 root@$H:/root/cb1/smad-next/packs/CB1/
rsync -a -e "$SSH" /home/narolski/smad-next/src/CB1/idistill/cb1_idistill.sbatch root@$H:/root/cb1/smad-next/jobs_cb1/
$SSH root@$H 'cd /root/cb1/smad-next/packs/CB1 && sha256sum -c *.sha256' | tee "$L/upload_check.txt"
echo UPLOAD_OK

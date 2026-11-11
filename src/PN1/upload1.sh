#!/bin/bash
# PN1: upload pack, DINOv3 tar, task folders to Athena (transfer lock), then verify hashes there (command lock).
set -u
A=plgpnarolski@athena.cyfronet.pl; G=/net/pr2/projects/plgrid/plggrestoration/smad-next
cd /mnt/t7/smad_next/PN1
t0=$(date +%s)
flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial pn1_pack.tar pn1_pack.tar.sha256 featx.tar featx.tar.sha256 $A:$G/packs/PN1/ || { echo "UPLOAD FAILED rc $?"; exit 1; }
echo "uploaded packs in $(( $(date +%s) - t0 )) s"
flock -w 1800 /tmp/smadnext-athena.lock rsync -a athena_tasks/ $A:$G/tasks/PN1/ || { echo "TASK UPLOAD FAILED"; exit 1; }
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "cd $G/packs/PN1 && sha256sum -c pn1_pack.tar.sha256 featx.tar.sha256 && cd $G/tasks/PN1 && sha256sum run.sh PN1_Bn_s401/run.sh pn1_smoke.sbatch pn1_array.sbatch"
echo "UPLOAD_DONE $(date +%T)"

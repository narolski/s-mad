#!/bin/bash
# PN1: after upload1, submit the smoke job, then upload the reference-network tar and refresh the task folder.
set -u
A=plgpnarolski@athena.cyfronet.pl; G=/net/pr2/projects/plgrid/plggrestoration/smad-next
until grep -q "UPLOAD_DONE\|FAILED" /mnt/t7/smad_next/PN1/upload1.log; do sleep 20; done
grep -q "UPLOAD_DONE" /mnt/t7/smad_next/PN1/upload1.log || { echo "upload1 failed; no submission"; exit 1; }
grep -q "pn1_pack.tar: OK" /mnt/t7/smad_next/PN1/upload1.log && grep -q "featx.tar: OK" /mnt/t7/smad_next/PN1/upload1.log || { echo "hash check failed on Athena"; exit 1; }
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "cd $G && sbatch tasks/PN1/pn1_smoke.sbatch"
echo "SMOKE_SUBMITTED $(date +%T)"
cd /mnt/t7/smad_next/PN1
flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial refnets.tar refnets.tar.sha256 $A:$G/packs/PN1/ && \
flock -w 1800 /tmp/smadnext-athena.lock rsync -a athena_tasks/ $A:$G/tasks/PN1/ && \
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes $A "cd $G/packs/PN1 && sha256sum -c refnets.tar.sha256 && ls $G/tasks/PN1"
echo "UPLOAD2_DONE $(date +%T)"

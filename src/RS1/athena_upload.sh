#!/bin/bash
# Own-crop re-score of the audit rows (RS1): upload the two packs to Athena in resumable pieces; every connection
# holds the shared lock for at most 4 minutes (rsync --partial --append-verify resumes), then releases it.
set -uo pipefail
A=/mnt/t7/smad_next/RS1/athena; G=/net/pr2/projects/plgrid/plggrestoration/smad-next
for f in rs1a_pack.tar rs1a_pack_amend.tar; do
  for k in $(seq 1 200); do
    flock -w 600 /tmp/smadnext-athena.lock timeout 240 rsync -a --partial --append-verify -e "ssh -o BatchMode=yes -o ConnectTimeout=30" \
      $A/$f plgpnarolski@athena.cyfronet.pl:$G/packs/RS1/ && { echo "$f done try $k $(date +%H:%M)"; break; }
    echo "$f piece $k $(date +%H:%M)"; sleep 5
  done
done
flock -w 600 /tmp/smadnext-athena.lock rsync -a -e "ssh -o BatchMode=yes" $A/rs1a_pack.tar.sha256 $A/rs1a_pack_amend.tar.sha256 plgpnarolski@athena.cyfronet.pl:$G/packs/RS1/
echo UPLOAD_DONE

#!/bin/bash
# upload_crops.sh wcss|athena : stream the exact local regen crops (crop_list.txt) as a tar split in 1 GiB parts
set -euo pipefail
cd /home/narolski/ad6_stage/h5race
case $1 in
  wcss) export LOCK=/tmp/opencode/wcss-client.lock HOST=narolski@ui.wcss.pl D=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/h5race/parts ;;
  athena) export LOCK=/tmp/smadnext-athena-cmd.lock HOST=plgpnarolski@athena.cyfronet.pl D=/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/AD5/h5race/parts ;;
esac
rm -f parts_$1.sha256
tar -cf - -C /mnt/t7/smad_next/RS1/regen_run -T crop_list.txt | tee >(sha256sum | sed 's/-$/crops_regen.tar/' > crops_regen_$1.tar.sha256) | \
  split -b 1G -d -a 2 --filter='tee >(sha256sum | sed "s#-\$#$FILE#" >> parts_'$1'.sha256) | flock -w 600 $LOCK ssh -o BatchMode=yes $HOST "cat > $D/$FILE"' - crops_regen.tar.part_
sleep 2; sort -k2 parts_$1.sha256 -o parts_$1.sha256
flock -w 600 $LOCK scp -q -o BatchMode=yes parts_$1.sha256 $HOST:$D/parts.sha256
flock -w 600 $LOCK ssh -o BatchMode=yes $HOST "cd $D && sha256sum -c parts.sha256 && ls | wc -l"
echo UPLOAD_DONE $1 $(date +%T)

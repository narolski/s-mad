#!/bin/bash
# SM1 amendment A10 after Athena job MODE=f: fetch + check + merge the JPEG-frame and arm-f features, rescore every
# saved head on the extended test bank, train the arm (f) heads (5 seeds, and the bootstrap variant), rerun readers.
set -euo pipefail
J=${1:?athena job id}
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
cd "$O/athena"
T=sm1gpu_feats_f_$J
if [ ! -f "$T.ok" ]; then
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial -e "ssh -o BatchMode=yes -o ConnectTimeout=20" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar.sha256" .
  sha256sum -c "$T.tar.sha256"
  mkdir -p "f_$J" && tar -xf "$T.tar" -C "f_$J" && touch "$T.ok"
fi
cd /tmp
$P $S/merge_feats.py merge "$O/athena/f_$J/feats"
cp "$O/feat_athena/merge_log.json" "$O/feat_athena/merge_log_f.json"
$P $S/heads.py --rescore
$P $S/heads.py --fe-ref
$P $S/heads.py --arms f
$P $S/heads.py --arms f --boot
$P $S/read_p3.py
$P $S/read_p3.py --boot
$P $S/read_p2.py
echo P3F_DONE

#!/bin/bash
# SM1 Part 3 after the Athena feature job: fetch + check + merge, equivalence check, smoke heads and reader (seed 401,
# 500 pairs), then all heads (5 seeds), bootstrap heads, FE reference, readers. Usage: run_p3.sh JOBID
set -euo pipefail
J=${1:?athena job id}
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
cd "$O/athena"
T=sm1gpu_feats_full_$J
if [ ! -f "$T.ok" ]; then
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial -e "ssh -o BatchMode=yes -o ConnectTimeout=20" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar.sha256" .
  sha256sum -c "$T.tar.sha256"
  mkdir -p "full_$J" && tar -xf "$T.tar" -C "full_$J" && touch "$T.ok"
fi
cd /tmp
$P $S/merge_feats.py merge "$O/athena/full_$J/feats"
$P $S/merge_feats.py equiv "$O/feat_athena"
$P $S/pool_cue.py
$P $S/heads.py --smoke --arms a,b,bp,c,cr,d --seeds 401
$P $S/read_p3.py --smoke --arms a,b,bp,c,cr,d --seeds 401 --B 1000
echo P3_SMOKE_DONE
$P $S/heads.py --fe-ref
$P $S/heads.py
$P $S/read_p3.py
$P $S/heads.py --boot
$P $S/read_p3.py --boot
echo P3_DONE

#!/bin/bash
# SM1 A12 items 11 and 13 after Athena job MODE=a12: fetch + check + merge the armd5 and softened-AR1 features, compose
# arm d5, fit its heads (our recipe on the GPU as Part 3; release recipe on the CPU), rerun the readers, score the
# softened copies. Sequential, one process at a time (DGX limit 2), OMP 2, nice 10.
#   bash run_a12f.sh JOBID
set -euo pipefail
J=${1:?athena job id}
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
G=/net/pr2/projects/plgrid/plggrestoration/smad-next
mkdir -p "$O/athena"; cd "$O/athena"
T=sm1gpu_feats_a12_$J
if [ ! -f "$T.ok" ]; then
  flock -w 1800 /tmp/smadnext-athena.lock rsync -a --partial -e "ssh -o BatchMode=yes -o ConnectTimeout=20" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar" "plgpnarolski@athena.cyfronet.pl:$G/results/SM1/$T.tar.sha256" .
  sha256sum -c "$T.tar.sha256"
  mkdir -p "a12_$J" && tar -xf "$T.tar" -C "a12_$J" && touch "$T.ok"
fi
cd /tmp
[ -f "$O/feat_athena/merge_log.json" ] && cp "$O/feat_athena/merge_log.json" "$O/feat_athena/merge_log_before_a12.json"
$P $S/merge_feats.py merge "$O/athena/a12_$J/feats"
cp "$O/feat_athena/merge_log.json" "$O/feat_athena/merge_log_a12.json"
$P -c "
import json, sys
sys.path.insert(0, '$S')
import compose as C, sm1_common as K
for s in K.SEEDS:
    c = C.compose('d5', s)
    json.dump(c, open(K.OUT / 'compose' / f'd5_s{s}.json', 'w'))
    print('d5', s, len(c['genuine']), len(c['morph']))
"
$P $S/heads.py --arms d5
$P $S/heads_fz1.py --arms d5
$P $S/read_p3.py
$P $S/read_p3.py --dir $O/heads_fz1 --name fz1
$P $S/a12_fixed.py
$P $S/a12_partner_ref.py
$P $S/a12_partner_ref.py --heads-dir $O/heads_fz1 --name a12_partner_ref_fz1 --no-releases
$P $S/a12_af0soft.py
echo A12F_DONE

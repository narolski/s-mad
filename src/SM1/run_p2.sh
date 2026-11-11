#!/bin/bash
# SM1 Part 2 scoring chain (after the audit images exist and their crops are made by ar1copy/crop_rgb.py):
# crop list -> released detectors on own MTCNN crops (primary, rel_multi.py) -> whole files (secondary, A6) -> reader.
set -euo pipefail
S=/home/narolski/smad-next/src/SM1; O=/mnt/t7/smad_next/SM1
P="nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I"
cd /tmp
$P -c "
import csv,collections,glob
rows=[r for f in sorted(glob.glob('$O/crops/audit/crops*.csv')) for r in csv.DictReader(open(f))]
print(collections.Counter(r['status'].split(':')[0] for r in rows))
keep=[dict(id=r['id'],path=r['path']) for r in rows if r['status']=='retained' or r['status'].startswith('flag')]
w=csv.DictWriter(open('$O/crops/audit_list.csv','w',newline=''),fieldnames=['id','path']); w.writeheader(); w.writerows(keep)
print('crops kept', len(keep))
"
for G in madation_vitb16,madation_fe_vitb16,mixfacenet_mad_smdd,madation_vitl14,madation_fe_vitl14 madation_fs_vitb16,madation_fs_vitl14; do
  $P $S/rel_multi.py --manifest $O/crops/audit_list.csv --out-dir $O/p2scores --dets $G --bs 32 --workers 6
done
for G in madation_vitb16,madation_fe_vitb16,mixfacenet_mad_smdd,madation_vitl14,madation_fe_vitl14; do
  $P $S/rel_multi.py --manifest $O/flists/audit.csv --out-dir $O/p2scores/whole --dets $G --bs 32 --workers 6
done
$P $S/read_p2.py
echo P2_DONE

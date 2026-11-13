import csv, io, tarfile, numpy as np, sys, json
R='/mnt/t7/smad_next/MS1/results_rented/'
M=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv')))
H=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/heldout_tree/pn1/data/manifests/ms1_heldout.csv')))
ids=set(r['id'] for r in M)
rc=[r['id'] for r in H if r['rung']=='R_cam']
print('rcam stripped in pack:', sum(i[5:] in ids for i in rc), 'of', len(rc))
ex=[i for i in ids if i.startswith('ar1_')][:3]; print('ar1 ids in pack sample', ex)

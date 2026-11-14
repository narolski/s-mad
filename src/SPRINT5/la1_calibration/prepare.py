"""Predeclare 1000 labelled low-resolution persons and pin every actual image."""
import collections
import csv
import hashlib
import json
import pathlib
import random

labels=pathlib.Path('/mnt/t7/Datasety/datasets_processed/data-celeb-aligned/split.csv')
images=labels.parent/'images'
out=pathlib.Path('/mnt/t7/smad_next/SPRINT5_5/lowres_calibration_v1')
assert not out.exists();out.mkdir(parents=True)
by=collections.defaultdict(list)
for r in csv.DictReader(labels.open()):by[r['person_id']].append(r)
rng=random.Random(2026111405)
eligible=sorted(p for p,v in by.items() if len(v)>=2)
selected=rng.sample(eligible,1000);rows=[]
for j,p in enumerate(selected):
    for r in rng.sample(sorted(by[p],key=lambda r:r['image_id']),2):
        path=images/r['image_id'];assert path.is_file()
        rows.append({'image_id':r['image_id'],'person_id':p,'original_split':r['split'],
                     'partition':'calibration' if j<500 else 'validation','path':str(path),
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert len(rows)==2000
with (out/'selected_images.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report={'label_sha256':hashlib.sha256(labels.read_bytes()).hexdigest(),'labels':str(labels),
        'seed':2026111405,'selected_persons':1000,'images':2000,'partition_persons':{'calibration':500,'validation':500},
        'selection_csv_sha256':hashlib.sha256((out/'selected_images.csv').read_bytes()).hexdigest(),
        'scope':'Variable-resolution aligned CelebA source calibration only; no localHQ correspondence or detector training admission'}
(out/'SELECTION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

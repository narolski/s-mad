"""Convert five admitted existing metadata allocations into FS1-format manifests."""
import csv
import hashlib
import json
import pathlib

repo=pathlib.Path('/home/narolski/smad-next')
base=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data')
inp=pathlib.Path('/mnt/t7/smad_next/SPRINT5_4/existing_pair_inventory_v1')
out=repo/'src/SPRINT5/breadth_fit'
truth={r['path']:r for r in csv.DictReader((base/'manifests/train_Sb.csv').open())}
report=[]
for seed in (511,512,513,514,515):
    for arm in ('narrow_more_variants','broad_fewer_variants'):
        p=inp/str(seed)/(arm+'.csv');rows=list(csv.DictReader(p.open()));converted=[]
        for r in rows:
            rel=str(pathlib.Path(r['path']).relative_to(base))
            x=dict(truth[rel]);assert x['label']==r['label'] and x['source']=='smdd'
            assert hashlib.sha256(pathlib.Path(r['path']).read_bytes()).hexdigest()==r['sha256']
            x.update(unit_person_ids=r['unit_person_ids'],contributing_ids=r['contributing_ids'],allocation_unit=r['unit_id'],variant_id=r['variant_id'])
            converted.append(x)
        assert len(converted)==32 and len({r['path'] for r in converted})==32
        target=out/f'train_{arm}_s{seed}.csv'
        with target.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(converted[0]));w.writeheader();w.writerows(converted)
        report.append({'arm':arm,'seed':seed,'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
          'allocation_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':32,'images_hashed':32})
(repo/'experiments/SPRINT5_20261114/breadth/FIT_MANIFESTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'manifests':len(report),'status':'EXACT32SOURCEASSETS_VERIFIED'}))

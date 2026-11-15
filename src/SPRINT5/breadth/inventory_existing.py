"""Inventory existing training pair/orientation assets; no HQ or new images."""
import collections
import csv
import hashlib
import json
import pathlib
import allocate

repo=pathlib.Path('/home/narolski/smad-next')
base=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data')
splitp=repo/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv'
trainp=base/'manifests/train_Sb.csv'
split={r['pid']:r for r in csv.DictReader(splitp.open())}
train=list(csv.DictReader(trainp.open()))
asset={r['id']:r for r in train if r['kind'] in ('lad_S3','lad_S4')}
rows=[];units=collections.Counter();missing=[]
for h,r in sorted(split.items()):
    b=r['partner_B']
    if r['role']!='train' or split[b]['role']!='train' or split[b]['partner_B']!=h or h>=b:continue
    source=r['db'];unit=h+'__'+b;block=[]
    for variant,host in enumerate((h,b)):
        suffix=host.replace(':','_')
        for kind,label in (('S3','0'),('S4','1')):
            key='sp2_'+kind+'_opencv_'+suffix
            if key not in asset:missing.append(key);continue
            a=asset[key];assert int(a['label'])==int(label)
            p=base/a['path'];assert p.is_file()
            block.append(dict(unit_id=unit,unit_person_ids=h+';'+b,contributing_ids=(host if label=='0' else h+';'+b),
                 source=source,variant_id=str(variant),kind=kind,label=label,processing=a['hist'],path=str(p),
                 host=host,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    if len(block)==4:rows.extend(block);units[source]+=1
out=pathlib.Path('/mnt/t7/smad_next/SPRINT5_4/existing_pair_inventory_v1')
assert not out.exists();out.mkdir(parents=True)
with (out/'eligible_variants.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'source_units':dict(units),'images':len(rows),'missing':missing,'unit':'two reciprocal training persons; two host orientations; S4/S3 in each',
         'input_pins':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (splitp,trainp)},
         'limitation':'Eligibility is existing historical training truth, not independent new captures; bounded splice-contrast budget pilot only.'}
receipts=[]
for seed in (511,512,513,514,515):
    arms,s=allocate.allocate(rows,4,1,seed)
    d=out/str(seed);d.mkdir()
    for arm,rs in arms.items():
        with (d/(arm+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    receipts.append({'seed':seed,'allocation':s})
summary['five_allocation_receipts']=receipts
(out/'inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'units':dict(units),'images':len(rows),'allocations':len(receipts),'arm_rows':receipts[0]['allocation']['narrow_more_variants']['rows'],
                 'identities':{k:v['identities'] for k,v in receipts[0]['allocation'].items()}}))

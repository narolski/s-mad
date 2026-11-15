"""Actual source/processing and identity feasibility for genuine-tail training."""
import collections
import csv
import hashlib
import json
import pathlib

repo=pathlib.Path('/home/narolski/smad-next')
base=pathlib.Path('/mnt/t7/smad_next')
trainp=base/'PN1/fs_tree/pn1/data/manifests/train_Sb.csv'
afp=base/'AF0/manifest.csv'
arp=base/'AF0/lists/ar1.csv'
hap=base/'PN1/lists/ar1h.csv'
sp=repo/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv'
af={r['id']:r for r in csv.DictReader(afp.open())}
ar={r['id']:r for r in csv.DictReader(arp.open())}
ha={r['id']:r for r in csv.DictReader(hap.open())}
split={r['pid']:r for r in csv.DictReader(sp.open())}
unique={r['path']:r for r in csv.DictReader(trainp.open())}
rows=[]
for r in unique.values():
    i=r['id'];kind=r['kind'];y=int(r['label'])
    if kind.startswith('af0_'):
        stem=i.removesuffix('_fm61');side=None
        if stem.endswith(('_halfA','_halfB')):stem,side=stem.rsplit('_',1)
        origin=af[stem]
        if y:ids=[origin['pid_A'],origin['pid_B']]
        elif side=='halfB':ids=[origin['pid_B']]
        else:ids=[origin['pid_A']]
    elif kind in ('lad_R0','lad_R2w','lad_R4'):
        origin=ar[i];ids=[origin['p1'],origin['p2']] if y else [origin['p1']]
    elif kind=='lad_half':
        origin=ha[i];ids=[origin['p2'] if i.endswith('_hB') else origin['p1']]
    elif kind in ('lad_S0','lad_S3','lad_S4'):
        _,rung,tool,db,pid=i.split('_');h=db+':'+pid
        ids=[h,split[h]['partner_B']] if y else [h]
    else:raise ValueError(kind)
    row=dict(r,contributing_ids=';'.join(sorted(set(ids))),group=r['db']+'/'+r['hist'],
       camera_genuine=str(kind in ('af0_photo','af0_photo61','lad_R0')))
    rows.append(row)
summary={}
for camera_only in (False,True):
    stats={}
    for g in sorted({r['group'] for r in rows}):
        rs=[r for r in rows if r['group']==g and r['label']=='0' and (not camera_only or r['camera_genuine']=='True')]
        identities={p for r in rs for p in r['contributing_ids'].split(';')}
        stats[g]={'unique_negative_images':len(rs),'negative_texture_identities':len(identities),'q10_effective_tail_identities':len(identities)*.1}
    summary['camera_photo_only' if camera_only else 'all_protocol_negatives']=stats
summary['positive_families']={k:len({r['path'] for r in rows if r['kind']==k and r['label']=='1'}) for k in sorted({r['kind'] for r in rows if r['label']=='1'})}
summary['known_reference']='Existing H100 AB1_Sb_s408.tar is source-pinned reference; do not read training logits without separate narrowed authorization/review. No new baseline reference/anchor computed here.'
summary['next_executable']='Freeze camera-only vs allnegative target, eta quantile initialization and dedicated eta LR; baseline training-only pass for anchors/group references (not a candidate read), then real GPU smoke and fixed warm-start pilot registration.'
summary['input_pins']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (trainp,afp,arp,hap,sp)}
out=base/'SPRINT5_3/metadata_v1';assert not out.exists();out.mkdir(parents=True)
with (out/'training_identity_groups.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

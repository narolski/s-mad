"""Native TRAIN124 nuisance-floor inputs. Measurements only, no learner fit."""
import csv
import hashlib
import json
import pathlib
import sys

import cv2
import numpy as np

repo=pathlib.Path('/home/narolski/smad-next')
src=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/train124_native_floor_v1')
out=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/floor_native_features_v1')
assert not out.exists();out.mkdir(parents=True)
sys.path.insert(0,str(repo/'src/adversary'))
sys.path.insert(0,str(repo/'src/AR1'))
import feats
import floor
import splice

records=json.loads((src/'pilot.json').read_text())
assert len(records)==124 and all(r['status']=='BUILT' for r in records)
pool={r['pid']:r for r in csv.DictReader(open('/mnt/t7/smad_next/AR1/pool.csv'))}
paths=[];rows=[];extra=[]
for r in records:
    p=pool[r['host']]
    wh=cv2.imread(r['outputs']['WH']['path']).astype(np.int16)
    mask=splice.hull(str(pathlib.Path(p['H']).with_suffix('.tem')),str(pathlib.Path(p['B']).with_suffix('.tem')),wh.shape)
    assert mask.any()
    for role,label in (('P',1),('N',0)):
        entry=r['outputs'][role];path=pathlib.Path(entry['path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        image=cv2.imread(str(path));assert image.shape==wh.shape
        diff=np.abs(image.astype(np.int16)-wh)
        # BD1's D convention: mean absolute RGB difference over shared R4 hull.
        d=float(diff[mask].mean())
        f=image.astype(np.float64);face=f[mask]
        luma=face@np.array([.114,.587,.299])
        color=np.max(face,1)-np.min(face,1)
        extra.append([luma.mean(),luma.std(),*np.quantile(luma,[.1,.5,.9]),
                      color.mean(),color.std(),float((color<=1).mean())])
        paths.append(str(path))
        rows.append({'id':r['host']+'/'+role,'host':r['host'],'partner':r['partner'],'source':r['source'],
                     'label':label,'role':role,'path':str(path),'sha256':entry['sha256'],'D':d,
                     'persons':r['host']+';'+r['partner']})
persons=[tuple(r['persons'].split(';')) for r in rows]
components=floor.components(persons)
sources=np.array([r['source'] for r in rows])
for g in np.unique(components):assert len(set(sources[components==g]))==1
for i,r in enumerate(rows):r['component']=int(components[i])
names=feats.names()+['LUMA:mean','LUMA:std','LUMA:p10','LUMA:p50','LUMA:p90','COLOR:range_mean','COLOR:range_std','COLOR:gray_fraction']
X=np.concatenate([feats.compute(paths,workers=2),np.asarray(extra)],axis=1)
assert X.shape==(248,len(names))
edges=np.quantile(np.log(np.maximum([r['D'] for r in rows],1e-12)),[.2,.4,.6,.8])
for r in rows:r['D_quintile']=int(np.searchsorted(edges,np.log(max(r['D'],1e-12)),side='right'))
with (out/'rows.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
np.savez(out/'features.npz',X=X,names=np.asarray(names),component=components,
         label=np.array([r['label'] for r in rows]),D_quintile=np.array([r['D_quintile'] for r in rows]))
summary={'scope':'TRAIN124 native construction nuisance diagnostic; not detector fit/heldout test',
  'rows':248,'pairs':124,'components':int(len(np.unique(components))),
  'max_component_rows':int(max(np.sum(components==g) for g in np.unique(components))),
  'D_definition':'BD1 mean absolute RGB(composite-WH) inside SAME H/B hull, natural native composites',
  'log_D_quintile_edges':edges.tolist(),'within_D_weighting':'equal quintiles if each class present; otherwise unreadable, no hidden bin pooling',
  'quintile_class_counts':{str(q):{str(y):sum(r['D_quintile']==q and r['label']==y for r in rows) for y in (0,1)} for q in range(5)},
  'known_preread_risk':'First host H/B color,Sgrayscale; N may be desaturated. Never remove after visualQC.',
  'source_pins':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (pathlib.Path(__file__),src/'pilot.json',repo/'src/adversary/feats.py',repo/'src/adversary/floor.py',repo/'src/AR1/splice.py')},
  'models_fitted':False,'candidate_scores_read':False}
(out/'PREPARATION.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

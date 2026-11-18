"""HN native124 metadata/byte audit and prospective folds; no learner fitting."""
import argparse,collections,csv,hashlib,json,pathlib,sys
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
R=pathlib.Path('/home/narolski/smad-next');B=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/train124_native_floor_v1');F=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/floor_native_features_v1')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
records=json.loads((B/'pilot.json').read_text());rows=list(csv.DictReader((F/'rows.csv').open()));z=np.load(F/'features.npz',allow_pickle=False);old=json.loads((F/'PREPARATION.json').read_text());meta=json.loads((B/'metadata.json').read_text())
assert len(records)==124 and len(rows)==248 and z['X'].shape==(248,70)
assert all(r['status']=='BUILT' for r in records);pins={}
for p,h in {**meta['source_pins'],**old['source_pins']}.items():assert sha(p)==h,p;pins[p]=h
parent={}
def find(x):
 parent.setdefault(x,x)
 if parent[x]!=x:parent[x]=find(parent[x])
 return parent[x]
def union(x,y):
 x,y=find(x),find(y)
 if x!=y:parent[max(x,y)]=min(x,y)
for r in records:
 union(r['host'],r['partner']);assert r['B_provenance']['role']=='train'
 for p,h in r['input_pins'].items():assert sha(p)==h,p;pins[p]=h
 for v in r['outputs'].values():assert sha(v['path'])==v['sha256'],v['path'];pins[v['path']]=v['sha256']
assert [r['id'] for r in rows]==[r['host']+'/'+k for r in records for k in ('P','N')]
y=z['label'];g=np.array([find(r['host']) for r in rows]);source=np.array([r['source'] for r in rows]);d=z['D_quintile']
assert np.array_equal(y,np.array([int(r['label']) for r in rows]));assert np.array_equal(d,np.array([int(r['D_quintile']) for r in rows]))
# Compare equivalence relations, independent of arbitrary component numbering.
assert np.array_equal(g[:,None]==g[None,:],z['component'][:,None]==z['component'][None,:])
assert len(np.unique(g))==50 and all(len(set(source[g==k]))==1 for k in np.unique(g))
# One CV splitter per source, union same-index test folds. No source is absent from a test fold.
foldparts=[]
for s in sorted(set(source)):
 ii=np.flatnonzero(source==s);local=list(StratifiedGroupKFold(5,shuffle=True,random_state=2026111405).split(np.zeros((len(ii),1)),y[ii],g[ii]));foldparts.append([(ii[tr],ii[te]) for tr,te in local])
folds=[]
for k in range(5):
 tr=np.sort(np.concatenate([s[k][0] for s in foldparts]));te=np.sort(np.concatenate([s[k][1] for s in foldparts]));assert not set(g[tr])&set(g[te]);assert len(set(y[tr]))==len(set(y[te]))==2
 folds.append({'train':tr.tolist(),'test':te.tolist()})
assert sorted(i for f in folds for i in f['test'])==list(range(248))
# D is the stored-composite versus SAME sharedhost layer; verify directly, including pinned hull inputs.
import cv2
sys.path.insert(0,str(R/'src/AR1'));import splice
pool={r['pid']:r for r in csv.DictReader(open('/mnt/t7/smad_next/AR1/pool.csv'))}
maxerr=0.
for k,rec in enumerate(records):
 p=pool[rec['host']];wh=cv2.imread(rec['outputs']['WH']['path']);assert wh is not None and wh.shape==(512,512,3)
 mask=splice.hull(str(pathlib.Path(p['H']).with_suffix('.tem')),str(pathlib.Path(p['B']).with_suffix('.tem')),wh.shape)
 for j,role in enumerate(('P','N')):
  im=cv2.imread(rec['outputs'][role]['path']);val=float(np.abs(im.astype(np.int16)-wh.astype(np.int16))[mask].mean());maxerr=max(maxerr,abs(val-float(rows[2*k+j]['D'])))
assert maxerr<1e-12
for p in [B/'pilot.json',B/'metadata.json',F/'rows.csv',F/'features.npz',F/'PREPARATION.json',R/'src/adversary/feats.py',R/'src/adversary/floor.py',R/'src/AR1/splice.py',pathlib.Path(__file__)]:pins[str(p)]=sha(p)
# Pin transitive existing feature dependencies (kernel imports assert these too).
for p in [R/'src/AF0/cues_all.py',R/'src/TT1/build_border_ref.py',pathlib.Path('/home/narolski/mambamorph-code/smadcvpr/cue_floor.py')]:pins[str(p)]=sha(p)
assert not a.out.exists();a.out.mkdir(parents=True)
(a.out/'folds.json').write_text(json.dumps(folds,indent=2)+'\n')
(a.out/'components.json').write_text(json.dumps({'groups':g.tolist(),'sources':source.tolist()},indent=2)+'\n')
summary={'status':'PREPARED_NO_FIT','rows':248,'pairs':124,'components':50,'components_by_source':{s:len(np.unique(g[source==s])) for s in sorted(set(source))},'largest_component_rows':int(max(np.sum(g==k) for k in np.unique(g))),'D_verified_max_error':maxerr,'D_definition':'mean absolute RGB(stored P or N minus shared WH) over pinned common H/B hull; NOT unrounded rawdonor-layer difference; sameBD1convention','source_pins':pins,'feature_nonfinite':int((~np.isfinite(z['X'])).sum()),'fixed_D_edges':old['log_D_quintile_edges'],'class_quintile_counts':old['quintile_class_counts'],'fold_seed':2026111405,'fold_counts':[{'train':len(f['train']),'test':len(f['test'])} for f in folds],'known_risk':'grayS/colorH+B may cause Ndesaturation; fixedCOLORfeatures retain all124hosts, noQCexclusions','scope':'trainingconstructionfeasibility only; no heldouttest or detector score access','output_pins':{str(a.out/n):sha(a.out/n) for n in ['folds.json','components.json']}}
(a.out/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['source_pins','output_pins']},indent=2))

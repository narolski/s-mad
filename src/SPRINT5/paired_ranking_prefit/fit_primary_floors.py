"""Prospective CPU-only primary floors. Requires separately reviewed release JSON.
No detector scores, images, checkpoints, or old floor outcomes are read.
"""
import argparse,csv,hashlib,importlib.util,json,pathlib,sys
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--prepared',type=pathlib.Path,required=True);ap.add_argument('--d-values',type=pathlib.Path,required=True);ap.add_argument('--floor-module',type=pathlib.Path,required=True);ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(a.release.read_text());assert r['decision']=='GO_PRIMARY_FLOORS' and r['reviewer']!=r['author']
assert r['script_sha256']==sha(pathlib.Path(__file__))
for k,p in [('floor_module',a.floor_module),('d_values',a.d_values),('features',a.prepared/'floor_features.npz'),('folds',a.prepared/'floor_folds.json')]:assert sha(p)==r[k+'_sha256'],k
assert r['construction']=='global component-crossfit; fixed equal-weight D-stratum evaluation'
assert not a.out.exists();a.out.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('pinned_floor',a.floor_module);FL=importlib.util.module_from_spec(spec);spec.loader.exec_module(FL)
z=np.load(a.prepared/'floor_features.npz',allow_pickle=False);X=z['X'];names=z['names'].astype(str).tolist();y=z['y'];g=z['groups'];ids=z['ids'].astype(str).tolist()
D={v['id']:v for v in csv.DictReader(a.d_values.open())}
geom=np.array([[float(D[i]['G']),float(D[i]['hull_px'])] for i in ids]);X=np.column_stack([X,geom]);names+=['GEOMETRY:G','GEOMETRY:hull_px']
folds=[(np.array(f['train']),np.array(f['test'])) for f in json.loads((a.prepared/'floor_folds.json').read_text())]
for tr,te in folds:assert not set(g[tr])&set(g[te])
sets={'all_cue':list(range(len(names))),'luma':[names.index(n) for n in ['F27:mean_Y','F27:mean_Y_face','F27:std_Y_face']],'render':[j for j,n in enumerate(names) if n.startswith('RENDER:')],'storage':[j for j,n in enumerate(names) if n.startswith('STORE:') or n=='F27:png_bytes'],'geometry':[j for j,n in enumerate(names) if n.startswith('GEOMETRY:')]}
out={'id':ids,'label':y.tolist(),'component':g.astype(str).tolist(),'D_stratum':z['D_stratum'].tolist()}
for subset,cols in sets.items():
 assert cols
 for kind in ('single','logreg','gbt'):
  scores,chosen=FL.crossfit(X[:,cols],y,g,kind,fl=folds,names=[names[j] for j in cols]);assert scores.shape==(200,) and np.isfinite(scores).all()
  out[subset+'__'+kind]=scores.tolist()
fields=list(out)
with (a.out/'primary_floors.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(fields);w.writerows(zip(*(out[k] for k in fields)))
import sklearn
meta={'status':'FLOORS_FITTED_NO_CANDIDATE_READ','release_sha256':sha(a.release),'row_count':200,'feature_columns':{k:[names[j] for j in c] for k,c in sets.items()},'numpy':np.__version__,'sklearn':sklearn.__version__,'python':sys.version,'primary_floors_sha256':sha(a.out/'primary_floors.csv'),'interpretation':'No scalar floor selected here. Reader computes all15 within-D statistics and conservative maximum in every paired bootstrap replicate; no tuning from candidate outcomes.'}
(a.out/'RECEIPT.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))

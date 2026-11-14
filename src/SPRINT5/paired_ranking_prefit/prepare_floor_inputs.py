"""Prepare fixed feature columns and person-disjoint CV folds; fit no learner."""
import argparse,collections,hashlib,json,pathlib
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=pathlib.Path,required=True);ap.add_argument('--prepared',type=pathlib.Path,required=True);a=ap.parse_args()
p=a.prepared;rows=json.loads((p/'primary_with_D_components.json').read_text());z=np.load(a.inputs/'ab1x_features.npz',allow_pickle=False)
paths=z['paths'].astype(str);names=z['names'].astype(str);inds=[]
for r in rows:
 matches=[i for i,x in enumerate(paths) if x.endswith('/'+r['path'])]
 assert len(matches)==1,(r['id'],len(matches))
 inds.append(matches[0])
X=z['X'][inds];y=np.array([int(r['label']) for r in rows]);g=np.array([r['component'] for r in rows]);d=np.array([r['D_stratum'] for r in rows]);source=np.array([r['source'] for r in rows])
folds=list(StratifiedGroupKFold(5,shuffle=True,random_state=2026111402).split(X,y,g))
for tr,te in folds:
 assert not set(g[tr])&set(g[te]);assert len(np.unique(y[tr]))==len(np.unique(y[te]))==2
np.savez(p/'floor_features.npz',X=X,names=names,ids=np.array([r['id'] for r in rows]),y=y,groups=g,D_stratum=d)
foldspec=[{'train':tr.tolist(),'test':te.tolist()} for tr,te in folds]
(p/'floor_folds.json').write_text(json.dumps(foldspec,indent=2)+'\n')
# Check endpoint feasibility, not candidate scores.
rng=np.random.default_rng(2026111401);bad=0
idx={v:np.flatnonzero(g==v) for v in np.unique(g)}
by={s:np.unique(g[source==s]) for s in np.unique(source)}
for b in range(10000):
 ii=np.concatenate([idx[v] for s,gs in sorted(by.items()) for v in rng.choice(gs,len(gs),replace=True)])
 bad+=any(not np.any(y[ii][d[ii]==k]==lab) for k in range(5) for lab in (0,1))
report={'status':'PREPARED_NO_LEARNER_FIT','feature_cache_sha256':hashlib.sha256((a.inputs/'ab1x_features.npz').read_bytes()).hexdigest(),'n_rows':len(rows),'n_features':X.shape[1],'nonfinite_feature_values':int((~np.isfinite(X)).sum()),'folds':[{'train':len(tr),'test':len(te),'test_components':len(np.unique(g[te]))} for tr,te in folds],'bootstrap_unreadable_count':bad,'bootstrap_draws':10000,'bootstrap_unreadable_share':bad/10000,'note':'Metadata-only denominator feasibility; reader must use identical component-draw ordering and fixed D strata. Seed-resampling can use separate deterministic RNG to preserve denominator audit. No outcomes accessed.','subsets_proposed':{'all_cue':names.tolist(),'luma':[n for n in names if n in ['F27:mean_Y','F27:mean_Y_face','F27:std_Y_face']],'render':[n for n in names if n.startswith('RENDER:')],'storage':[n for n in names if n.startswith('STORE:') or n=='F27:png_bytes'],'geometry':'G and hull_px from pinned d_values.csv; to add after review, excludes D itself'},'outputs':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['floor_features.npz','floor_folds.json']}}
(p/'FLOOR_PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

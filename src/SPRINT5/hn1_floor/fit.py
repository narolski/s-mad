"""Root-reviewed HN124 CPU nuisance floor only. No detector/benchmark inputs."""
import argparse,csv,hashlib,importlib.util,json,pathlib,sys,time
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=json.loads(a.release.read_text());assert r['decision']=='GO_HN124_FLOOR' and r['reviewer']!=r['author']
assert r['script_sha256']==sha(pathlib.Path(__file__))
for p,h in r['pins'].items():assert sha(p)==h,p
assert r['scope']=='TRAIN124_NATIVE_CONSTRUCTION_ONLY' and r['bootstrap_draws']==10000
assert not a.out.exists();a.out.mkdir(parents=True);t0=time.monotonic()
F=pathlib.Path(r['features_dir']);P=pathlib.Path(r['prepared_dir']);z=np.load(F/'features.npz',allow_pickle=False);rows=list(csv.DictReader((F/'rows.csv').open()));c=json.loads((P/'components.json').read_text());g=np.array(c['groups']);sources=np.array(c['sources']);y=z['label'];d=z['D_quintile'];X=z['X'];names=z['names'].astype(str).tolist()
assert X.shape==(248,70) and len(rows)==248 and np.isfinite(X).all();assert np.array_equal(y,np.array([int(x['label']) for x in rows]))
folds=[(np.array(f['train']),np.array(f['test'])) for f in json.loads((P/'folds.json').read_text())]
for tr,te in folds:assert not set(g[tr])&set(g[te])
module=pathlib.Path(r['floor_module']);sp=importlib.util.spec_from_file_location('pinned_floor',module);FL=importlib.util.module_from_spec(sp);sp.loader.exec_module(FL)
sets={'allcue':list(range(70)),'luma':[j for j,n in enumerate(names) if n.startswith('LUMA:')],'color':[j for j,n in enumerate(names) if n.startswith('COLOR:')]};assert len(sets['luma'])==5 and len(sets['color'])==3
scores={};choices={}
for subset,cols in sets.items():
 for kind in ('single','logreg','gbt'):
  name=subset+'__'+kind;s,ch=FL.crossfit(X[:,cols],y,g,kind,fl=folds,names=[names[j] for j in cols]);assert s.shape==(248,) and np.isfinite(s).all();scores[name]=s;choices[name]=ch
keys=list(scores);matrix=np.stack([scores[k] for k in keys])
def aucs(ii):
 pp=ii[y[ii]==1];nn=ii[y[ii]==0]
 if not len(pp) or not len(nn):return np.full(len(keys),np.nan)
 ps=matrix[:,pp,None];ns=matrix[:,None,nn]
 return ((ps>ns)+.5*(ps==ns)).mean(axis=(1,2))
def stat(ii):
 ss=[aucs(ii[d[ii]==q]) for q in range(5)]
 if not np.isfinite(ss).all():return None
 return np.mean(ss,axis=0)
point=stat(np.arange(248));assert point is not None
rng=np.random.default_rng(2026111406);idx={x:np.flatnonzero(g==x) for x in np.unique(g)};by={s:np.unique(g[sources==s]) for s in sorted(set(sources))};boot=[];bad=0
for _ in range(10000):
 ii=np.concatenate([idx[v] for s,gs in by.items() for v in rng.choice(gs,len(gs),replace=True)])
 v=stat(ii)
 if v is None:bad+=1
 else:boot.append(v)
boot=np.array(boot);assert len(boot)>0
cols=['id','label','component','source','D_quintile']+keys
with (a.out/'heldout_floor_rows.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(cols)
 for i,row in enumerate(rows):w.writerow([row['id'],int(y[i]),g[i],sources[i],int(d[i])]+matrix[:,i].tolist())
res={}
for subset in sets:
 ix=[i for i,k in enumerate(keys) if k.startswith(subset+'__')];bs=boot[:,ix].max(axis=1)
 res[subset]={'point_max':float(point[ix].max()),'conditional_component_CI95':np.quantile(bs,[.025,.975]).tolist(),'model_points':{keys[i]:float(point[i]) for i in ix}}
maxpoint=float(point.max());maxboot=boot.max(axis=1)
# Historical point thresholds fixed before fit. Color is included prospectively as an explicit nuisance diagnostic/gate.
if bad/10000>.05:decision='INCONCLUSIVE_BOOTSTRAP_COVERAGE'
elif maxpoint>=.75:decision='CONSTRUCTION_LEAK_HOLD_DETECTOR_FIT'
elif maxpoint<=.60:decision='LOW_POINT_FLOOR_ELIGIBLE_FOR_SEPARATE_FIT_REVIEW'
else:decision='INTERMEDIATE_QUALIFIED_FIT_ONLY_AFTER_SEPARATE_REVIEW'
source_points={}
for s in sorted(set(sources)):
 v=stat(np.flatnonzero(sources==s));source_points[s]=None if v is None else dict(zip(keys,map(float,v)))
import sklearn
summary={'scope':r['scope'],'decision':decision,'warning':'Training-source construction feasibility only. Crossfitting does not make this an independentlyheldoutconstructiontest. Lowpointfloor is NOT certifiednuisanceabsence; CIs conditiononfixedcrossfittedlearners, exclude learner-refit variability and modelmisspecification.','known_preread_risk':'grayS versus colorH/B retained, no hostexcluded','sets':res,'max_all9':{'point':maxpoint,'conditional_component_CI95':np.quantile(maxboot,[.025,.975]).tolist()},'unstratified_model_auc':dict(zip(keys,map(float,aucs(np.arange(248))))),'source_points_descriptive':source_points,'unreadable_bootstraps':bad,'bootstrap_draws':10000,'fold_selection_choices':choices,'rows':248,'components':50,'versions':{'python':sys.version,'numpy':np.__version__,'sklearn':sklearn.__version__},'wall_seconds':time.monotonic()-t0,'release_sha256':sha(a.release),'heldout_sha256':sha(a.out/'heldout_floor_rows.csv'),'detector_scores_read':False}
(a.out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'status':'COMPLETE','decision':decision,'wall_seconds':summary['wall_seconds'],'result_sha256':sha(a.out/'RESULT.json')},indent=2))

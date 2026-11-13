import sys, csv, numpy as np
sys.path.insert(0,"/home/narolski/smad-next/src/BD1"); sys.path.insert(0,"/home/narolski/smad-next/src/TB1"); sys.path.insert(0,"/home/narolski/smad-next/src/RI1")
from bd1_read import auc, strat_auc
from ri1_read import crossfit_auc
import tb1_read as T
R=list(csv.DictReader(open("/mnt/t7/smad_next/TB1/tb1_feats.csv")))
hosts=[r["host"] for r in R]
D={r["id"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/BD1/d_values.csv"))}
for r in csv.DictReader(open("/mnt/t7/smad_next/BD1/d_feats.csv")): D[r["id"]].update(r)
pool={r["pid"]:r for r in csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv"))}
col=lambda pre,n: np.array([[float(r[f"{pre}_{n}{k}"]) for k in range(1,6)] for r in R])
dv=lambda img,key: np.array([float(D[r[f"{img}_id"]][key]) for r in R])
lp4,lp3=np.log(col("P4","p")),np.log(col("P3","p"))
Et4=np.log([float(r["P4_Etot"]) for r in R]); Et3=np.log([float(r["P3_Etot"]) for r in R])
lD4,lD3=np.log(dv("S4","D")),np.log(dv("S3","D"))
c=lambda *a: np.column_stack(a)
for name,(a4,a3) in {"logD":(c(lD4),c(lD3)),"logEtot":(c(Et4),c(Et3)),"logD+logEtot":(c(lD4,Et4),c(lD3,Et3)),
  "profile":(lp4,lp3),"logD+profile":(c(lD4,lp4),c(lD3,lp3)),"logEtot+profile":(c(Et4,lp4),c(Et3,lp3)),"logD+logEtot+profile":(c(lD4,Et4,lp4),c(lD3,Et3,lp3)),
  "logE_k (5 abs band energies)":(np.log(col("P4","p"))+Et4[:,None],np.log(col("P3","p"))+Et3[:,None])}.items():
  print(f"{name:32s} crossfit AUC {crossfit_auc(a4,a3,hosts):.3f}")
# person-disjoint folds: connected components host-partner
par={h:h for h in hosts}
def find(x):
  while par[x]!=x: par[x]=par[par[x]]; x=par[x]
  return x
hs=set(hosts)
for h in hosts:
  b=pool[h]["B_pid"]
  if b in hs: par[find(h)]=find(b)
comp=[find(h) for h in hosts]
print("components",len(set(comp)),"largest",max(np.unique(comp,return_counts=True)[1]))
# folds by component
cs=sorted(set(comp)); rng=np.random.default_rng(20261171); cf=dict(zip(cs,rng.permutation(len(cs))%5))
fold={h:cf[find(h)] for h in hosts}
M,g=T.fold_models(lp4,lp3,hosts,fold); sp,sn=T.score_oof(M,g,lp4),T.score_oof(M,g,lp3)
print("component folds: auc",auc(sp,sn),"within D",strat_auc(sp,sn,np.exp(lD4),np.exp(lD3))[0])
# cluster bootstrap by component
cid=np.array([cs.index(x) for x in comp]); rr=np.random.default_rng(1); bs=[]
for _ in range(1000):
  pick=rr.integers(0,len(cs),len(cs)); ix=np.concatenate([np.where(cid==p)[0] for p in pick])
  v=strat_auc(sp[ix],sn[ix],np.exp(lD4[ix]),np.exp(lD3[ix]))[0]; bs.append(v)
print("component bootstrap CI",np.percentile(bs,[2.5,97.5]))

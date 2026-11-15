import sys, csv, json, numpy as np
sys.path.insert(0,'/home/narolski/smad-next/src/AR1')
import floors10 as FL, ar1_common as K, analyse as A, stats
from multiprocessing import Pool as MP
man=list(csv.DictReader(open(K.OUT/"manifest.csv")))
sp=[r for r in csv.DictReader(open(K.OUT/"manifest_splice2.csv")) if r["variant"]=="native"]
sw=list(csv.DictReader(open(K.OUT/"manifest_swap.csv")))
P=A.Pool(man,"frgcferet"); D=P.D
s4=[r for r in sp if r["rung"]=="S4" and r["tool"]=="opencv"]
need=s4+sw+[r for r in man if r["pool"]=="frgcferet" and r["rung"] in ("R2w","R2w4","R4")]
with MP(2) as mp:
    F={rid:(s,n) for rid,s,n in mp.map(FL.feats,[(r["id"],r["path"],r["p1"]) for r in need],chunksize=16)}
keys=["ratio","lap_in","tone_luma","tone_rg","abs_step"]+[f"band{i}" for i in range(1,6)]
simple=lambda f: np.array([f[0][k] for k in keys],np.float32)
both=lambda f: np.concatenate([simple(f),f[1]])
fa,best=FL.floor_eval(D,s4,sw,F,[("combined_logistic",simple),("simple+residual",both),("residual_only",lambda f:f[1])],keys)
print('(a) S4 vs SW floors', {k:round(v['auc'],3) for k,v in fa.items()})
# lap_in rep
sc={r["id"]:F[r["id"]][0]["lap_in"] for r in s4+sw}
a,rep,_,_=A.contrast(D,sc,s4,sw)
if a<0.5: a,rep=1-a,1-rep
out={}
for name,tag in A.REL:
    S=A.load(tag); S.update(A.load(f"{tag}__splice2") or {}); S.update(A.load(f"{tag}__swap") or {})
    da,drep,_,_=A.contrast(D,S,s4,sw)
    print(name,'S4vsSW',round(da,3),'excess vs lap_in',round(da-a,3),[round(x,3) for x in stats.ci(drep-rep)])
for tool in ("opencv","facemorpher"):
    for base in ("R2w","R2w4"):
        fb,bb=FL.floor_eval(D,P.rows(tool,"R4"),P.rows(tool,base),F,[("residual",lambda f:f[1]),("simple10",simple),("simple+residual",both)],keys)
        print(tool,base,'floors',{k:round(v['auc'],3) for k,v in fb.items()},'best',bb[2],round(bb[0],3))
        for name,tag in A.REL:
            S=A.load(tag); da,drep,_,_=A.contrast(D,S,P.rows(tool,"R4"),P.rows(tool,base))
            print('   ',name,round(da,3),'excess over best-of-all',round(da-bb[0],3),[round(x,3) for x in stats.ci(drep-bb[1])])

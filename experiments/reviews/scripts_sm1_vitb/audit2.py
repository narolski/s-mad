import sys, csv, numpy as np
RAW=sys.argv[1]; FL="/mnt/t7/smad_next/SM1/flists"
aud=list(csv.DictReader(open(f"{FL}/audit.csv")))
rows=[]
for t in ("test_eval",): rows+=list(csv.DictReader(open(f"{FL}/{t}.csv")))
def conv(i):
    i=str(i); return i if i.startswith(("ar1:","ar1h:","ev:","m22:")) else "ev:"+i
keys=sorted({r["key"] for r in aud if r["kind"]=="KP"})
idx={(r["kind"],r["key"],int(r["slot"])):r["id"] for r in aud if r["kind"] in("KP","KE","KU")}
rng=np.random.default_rng(20261111); dr=rng.integers(0,len(keys),(10000,len(keys)))
def perkey_auc(z):
    # per key: AUC of its 5 KP vs its 5 KE logits
    out=[]
    for k in keys:
        p=np.array([z[idx[("KP",k,j)]] for j in range(5)]); e=np.array([z[idx[("KE",k,j)]] for j in range(5)])
        out.append(((p[:,None]>e[None,:]).mean()+0.5*(p[:,None]==e[None,:]).mean()))
    return np.array(out)
def gap(z):
    return np.array([np.mean([z[idx[("KP",k,j)]] for j in range(5)])-np.mean([z[idx[("KE",k,j)]] for j in range(5)]) for k in keys])
def tail(z,thr):
    p=np.array([z[i] for (kk,_,_),i in idx.items() if kk=="KP"]); e=np.array([z[i] for (kk,_,_),i in idx.items() if kk=="KE"])
    return float((p<thr).mean()), float((e<thr).mean())
res={}
for fit in sys.argv[2:]:
    f=np.load(f"{RAW}/{fit}/audit/scores_audit.npz"); p=np.clip(f["score_noTTA"].astype(float),1e-7,1-1e-7)
    z=dict(zip(map(str,f["id"]),np.log(p/(1-p))))
    a=perkey_auc(z); g=gap(z); res[fit]=(a,g)
    ci=lambda x: np.percentile(x[dr].mean(1),[2.5,97.5]).round(3)
    print(fit,"perkeyAUC",a.mean().round(3),ci(a),"gap",g.mean().round(4),ci(g),"median gap",np.median(g).round(4),"tail<3.0 KP/KE",tail(z,3.0),"tail<3.3",tail(z,3.3))
for arm in ("a","c","e","f"):
    A=np.mean([res[f"SM1B_{arm}_s{s}"][0] for s in (401,402)],0); print(arm,"2-seed perkeyAUC",A.mean().round(3),np.percentile(A[dr].mean(1),[2.5,97.5]).round(3))
d=np.mean([res[f"SM1B_a_s{s}"][0] for s in (401,402)],0)-np.mean([res[f"SM1B_c_s{s}"][0] for s in (401,402)],0)
print("DiD AUC a-c",d.mean().round(3),np.percentile(d[dr].mean(1),[2.5,97.5]).round(3))
d=np.mean([res[f"SM1B_a_s{s}"][0] for s in (401,402)],0)-np.mean([res[f"SM1B_e_s{s}"][0] for s in (401,402)],0)
print("DiD AUC a-e",d.mean().round(3),np.percentile(d[dr].mean(1),[2.5,97.5]).round(3))

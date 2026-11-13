# Independent recomputation of AB1 reads (no import of ab1_read / c2p_read). Dev rows only; role=='test' never touched.
import csv, io, tarfile, json, sys, hashlib
import numpy as np
from scipy.stats import rankdata, t as tdist
RES="/mnt/t7/smad_next/AB1/results"; MAN="/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv"
ARMS=["A","B","Sb","Sp","SbZ","SbH","SbS","AS"]; SEEDS=[408,409,410,411,412]; SIZES=["fm61","amsl112"]
M=[r for r in csv.DictReader(open(MAN))]
def ids(**kw): return [r["id"] for r in M if all(r[k]==v for k,v in kw.items())]
P=dict(lc_m=ids(fam="ffhq_lcomb",rung="landmark_combined_orig"), lc_g=ids(fam="ffhq_lcomb",rung="landmark_combined_resmatch"),
 S3=ids(fam="splice",role="dev",rung="S3"),S0=ids(fam="splice",role="dev",rung="S0"),S4=ids(fam="splice",role="dev",rung="S4"),
 warp=ids(fam="ladder",role="dev",rung="R2w",tool="opencv",strength="")+ids(fam="ladder",role="dev",rung="R2w4",tool="opencv",strength="")+ids(fam="af0",role="dev",rung="zero"),
 warp_fm=ids(fam="ladder",role="dev",rung="R2w",tool="facemorpher",strength="")+ids(fam="ladder",role="dev",rung="R2w4",tool="facemorpher",strength=""),
 halves=ids(fam="af0",role="dev",rung="halfA")+ids(fam="af0",role="dev",rung="halfB"),
 soft=ids(fam="ladder",role="dev",rung="R0",strength="61")+ids(fam="af0",role="dev",rung="photo",strength="61")+ids(fam="ladder",role="dev",rung="R0",strength="112")+ids(fam="af0",role="dev",rung="photo",strength="112"),
 camera=ids(fam="ladder",role="dev",rung="R0",strength="")+ids(fam="af0",role="dev",rung="photo",strength=""),
 ffzero=ids(fam="ms1ffhq",rung="zero"), devR3=ids(fam="ladder",role="dev",rung="R3",strength=""), devR3m=ids(fam="ladder",role="dev",rung="R3m",strength=""),
 devR4=ids(fam="ladder",role="dev",rung="R4",strength=""), devR4_61=ids(fam="ladder",role="dev",rung="R4",strength="61"),devR3_61=ids(fam="ladder",role="dev",rung="R3",strength="61"),
 afu50=ids(fam="af0",role="dev",rung="u50",strength=""))
for k in ("S0_bg","S0_face","S3_bg","S3_face","S4_bg","S4_face","R4_face","R2w_face","R2w_bg"): P["sp_"+k]=ids(fam="splice",role="dev",rung=k)
assert not any(r["role"]=="test" for r in M if r["id"] in set(sum(P.values(),[])))
natp=sorted(ids(fam="ms1ffhq",rung="photo",strength="")); natm=sorted(ids(fam="ms1ffhq",rung="u50",strength=""))
allid=set(r["id"] for r in M)
pairs={z:[i for i in natp if f"{i}_{z}" in allid] for z in SIZES}; mpairs={z:[i for i in natm if f"{i}_{z}" in allid] for z in SIZES}
print({z:(len(pairs[z]),len(mpairs[z])) for z in SIZES})
rng=np.random.default_rng(20261131)
boot={z:[rng.integers(0,len(pairs[z]),len(pairs[z])) for _ in range(2000)] for z in SIZES}
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); r=rankdata(np.concatenate([p,n])); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
def sh(L,I): return float(np.mean(np.array([L[i] for i in I])>0))
out={}
for a in ARMS:
  for s in SEEDS:
    T=f"AB1_{a}_s{s}"; tp=f"{RES}/{T}.tar"
    h=hashlib.sha256(open(tp,'rb').read()).hexdigest(); assert h==open(tp+".sha256").read().split()[0]
    with tarfile.open(tp) as t:
        z=np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read())); zt=np.load(io.BytesIO(t.extractfile(f"{T}/scores_train.npz").read()))
        gpu=t.extractfile(f"{T}/gpu.txt").read().decode()
    L=dict(zip(map(str,z["id"]),z["logit"].astype(float)))
    st=dict(gpu=gpu.strip()[:60])
    st["lc"]=auc([L[i] for i in P["lc_m"]],[L[i] for i in P["lc_g"]])
    for k in P:
        if k not in("lc_m","lc_g"): st[k]=sh(L,P[k])
    st["dsoft"]=st["soft"]-st["camera"]
    st["S0vS4"]=auc([L[i] for i in P["S4"]],[L[i] for i in P["S0"]]); st["S3vS4"]=auc([L[i] for i in P["S4"]],[L[i] for i in P["S3"]])
    g=np.array([L[i] for i in natp]); sd=g.std(ddof=1); st["natflag"]=float((g>0).mean()); st["sd"]=float(sd)
    st["gmean"]=float(g.mean())
    mn_all=np.array([L[i] for i in natm]); st["auc_u50_photo_ffhq"]=auc(mn_all,g)
    for zz in SIZES:
        nat=np.array([L[i] for i in pairs[zz]]); sto=np.array([L[f"{i}_{zz}"] for i in pairs[zz]])
        df=(sto>0).mean()-(nat>0).mean(); dm=(sto-nat).mean()/sd
        rep=[(sto[w]>0).mean()-(nat[w]>0).mean() for w in boot[zz]]
        mn=np.array([L[i] for i in mpairs[zz]]); ms=np.array([L[f"{i}_{zz}"] for i in mpairs[zz]])
        st[zz]=dict(df=float(df),dm=float(dm),up95=float(np.percentile(rep,97.5)),dmatt=float((ms-mn).mean()/sd),
            up=int(((nat<=0)&(sto>0)).sum()),down=int(((nat>0)&(sto<=0)).sum()), dmed=float(np.median(sto-nat)/sd),
            nat_mean=float(nat.mean()), miss_nat=float((mn<=0).mean()), miss_sto=float((ms<=0).mean()), auc_sto=auc(ms,np.array([L[f"{i}_{zz}"] for i in pairs[zz]])))
    tr={}
    for k,v in zip(map(str,zt["kind"]),zt["logit"].astype(float)): tr.setdefault(k,[]).append(v)
    st["train"]={k:float(np.mean(np.array(v)>0)) for k,v in tr.items()}
    out[f"{a}_{s}"]=st
json.dump(out,open(sys.argv[1],"w"),indent=1)

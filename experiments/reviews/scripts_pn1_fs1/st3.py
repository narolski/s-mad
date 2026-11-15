import csv, io, tarfile, pathlib, numpy as np
from sklearn.metrics import roc_auc_score as ra
from scipy.stats import spearmanr
R=pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
man=list(csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")))
ids=lambda fam,role,rung,st="": [r["id"] for r in man if r["fam"]==fam and r["role"]==role and r["rung"]==rung and r["strength"]==st]
lm=[r["id"] for r in man if r["rung"]=="landmark_combined_orig"]; lg=[r["id"] for r in man if r["rung"]=="landmark_combined_resmatch"]
nat={r["host"]:r["id"] for r in man if r["rung"]=="ffhq_bona_orig"}; rm={r["host"]:r["id"] for r in man if r["rung"]=="landmark_complete_resmatch"}
keys=sorted(set(nat)&set(rm))
z=np.load("/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz"); names=[str(n) for n in z["names"]]; cid={str(i):c for i,c in zip(z["ids"],z["cues"])}
jb=names.index("noise_std_border")
bm=np.array([cid[i][jb] for i in lm]); bg=np.array([cid[i][jb] for i in lg])
edges=np.quantile(np.r_[bm,bg],np.linspace(0,1,11)); km=np.clip(np.searchsorted(edges,bm,"right")-1,0,9); kg=np.clip(np.searchsorted(edges,bg,"right")-1,0,9)
def strat(m,g):
    num=den=0
    for k in range(10):
        a,b=m[km==k],g[kg==k]
        if len(a) and len(b): w=len(a)*len(b); num+=w*ra(np.r_[np.ones(len(a)),np.zeros(len(b))],np.r_[a,b]); den+=w
    return num/den
def load(n):
    with tarfile.open(R/f"{n}.tar") as t: q=np.load(io.BytesIO(t.extractfile(f"{n}/scores_eval.npz").read()))
    return dict(zip([str(i) for i in q["id"]],q["logit"].astype(float)))
au=lambda S,p,n: ra(np.r_[np.ones(len(p)),np.zeros(len(n))],np.r_[[S[i] for i in p],[S[i] for i in n]])
sh={}
for s in (403,404,405,406,407):
    out=[]
    for a in ("A","B","Sb"):
        S=load(f"PN1_{a}_s{s}")
        m=np.array([S[i] for i in lm]); g=np.array([S[i] for i in lg])
        out.append(f"{a}: borderStrat {strat(m,g):.3f} S4vS0 {au(S,ids('splice','dev','S4'),ids('splice','dev','S0')):.3f} S4vS3 {au(S,ids('splice','dev','S4'),ids('splice','dev','S3')):.3f} S3vS0 {au(S,ids('splice','dev','S3'),ids('splice','dev','S0')):.3f} R4vR3(dev,ocv) {au(S,ids('ladder','dev','R4')[:0] or [r['id'] for r in man if r['fam']=='ladder' and r['role']=='dev' and r['rung']=='R4' and r['tool']=='opencv' and r['strength']==''],[r['id'] for r in man if r['fam']=='ladder' and r['role']=='dev' and r['rung']=='R3' and r['tool']=='opencv' and r['strength']=='']):.3f}")
        sh[(a,s)]=np.array([S[rm[k]]-S[nat[k]] for k in keys])
    print(s," | ".join(out))
# cross-seed per-person shift consistency for A
A401=load("PN1_Arep_s401"); sh[("A",401)]=np.array([A401[rm[k]]-A401[nat[k]] for k in keys])
for a in ("A","B","Sb"):
    ss=[s for s in (401,403,404,405,406,407) if (a,s) in sh]
    rh=[spearmanr(sh[(a,x)],sh[(a,y)]).correlation for i,x in enumerate(ss) for y in ss[i+1:]]
    print(a,"cross-seed Spearman of per-person shift: median %.2f range %.2f-%.2f"%(np.median(rh),min(rh),max(rh)))
# top-decile overlap for A
top=[set(np.argsort(-sh[("A",s)])[:200]) for s in (403,404,405,406,407)]
print("A top-10% persons overlap pairwise:",[round(len(top[i]&top[j])/200,2) for i in range(5) for j in range(i+1,5)])

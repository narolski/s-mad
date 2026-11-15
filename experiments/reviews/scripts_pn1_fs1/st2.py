import csv, io, tarfile, pathlib, numpy as np
from sklearn.metrics import roc_auc_score as ra
from scipy.stats import binomtest
R=pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
man=list(csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")))
nat={r["host"]:r["id"] for r in man if r["rung"]=="ffhq_bona_orig"}
rm={r["host"]:r["id"] for r in man if r["rung"]=="landmark_complete_resmatch"}
keys=sorted(set(nat)&set(rm))
def load(n):
    with tarfile.open(R/f"{n}.tar") as t: q=np.load(io.BytesIO(t.extractfile(f"{n}/scores_eval.npz").read()))
    return dict(zip([str(i) for i in q["id"]],q["logit"].astype(float)))
for a in ("A","B","Sb"):
  for s in (403,404,405,406,407):
    S=load(f"PN1_{a}_s{s}"); x=np.array([S[nat[k]] for k in keys]); y=np.array([S[rm[k]] for k in keys])
    auc=ra(np.r_[np.ones(2000),np.zeros(2000)],np.r_[y,x])
    b=int(((y>0)&(x<=0)).sum()); c=int(((x>0)&(y<=0)).sum())
    p=binomtest(b,b+c,0.5).pvalue if b+c else 1
    q90=np.percentile(y-x,90); q10=np.percentile(y-x,10)
    print(a,s,"AUC rm-vs-nat %.3f"%auc,"flag nat %d rm %d discordant +%d/-%d McNemar p %.2g"%((x>0).sum(),(y>0).sum(),b,c,p),"shift p10 %.2f p90 %.2f"%(q10,q90))

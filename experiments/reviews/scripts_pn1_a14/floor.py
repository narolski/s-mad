import csv, numpy as np
from scipy.stats import rankdata, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
A14="/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14/"
M="/mnt/t7/smad_next/PN1/a14_tree/pn14/data/manifests/pn1_a14.csv"
F="/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz"
man=list(csv.DictReader(open(M)))
def ld(p):
    z=np.load(p); return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
def auc(p,n):
    r=rankdata(np.r_[p,n])[:len(p)]; return (r.sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
lc={r['id']:r for r in man if r['fam']=='ffhq_lcomb'}
mo=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_orig')
gb=sorted(i for i,r in lc.items() if r['rung']=='landmark_combined_resmatch')
ids=mo+gb; y=np.r_[np.ones(len(mo)),np.zeros(len(gb))]
z=np.load(F); names=[str(n) for n in z['names']]; cid={str(i):c for i,c in zip(z['ids'],z['cues'])}
X=np.array([cid[i] for i in ids],float)
print(len(names),names)
j=names.index('noise_std_face'); f=X[:,j]
print("floor auc (morph high)",auc(-f[y==1],-f[y==0]))
# strata: deciles of f pooled
q=np.quantile(f,np.linspace(0,1,11)); bins=np.clip(np.searchsorted(q,f,side='right')-1,0,9)
print("per-decile counts morph/genuine",[(int((bins==b)&(y==1)).sum() if False else int(((bins==b)&(y==1)).sum()), int(((bins==b)&(y==0)).sum())) for b in range(10)])
nets=[(a,s) for s in (401,402) for a in ("A","B","Sb")]+[("Bn",401),("C",401),("Bv",401),("Bn",402),("C",402),("Bv",402)]
skf=StratifiedKFold(5,shuffle=True,random_state=0)
def cvauc(Z):
    p=np.zeros(len(y))
    for tr,te in skf.split(Z,y):
        m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1.0)).fit(Z[tr],y[tr]); p[te]=m.decision_function(Z[te])
    return auc(p[y==1],p[y==0])
base1=cvauc(f[:,None]); base27=cvauc(np.c_[X, np.log(np.abs(X)+1e-9)] if False else X)
print("CV floor-only 1 stat",round(base1,4),"CV 27 stats LR",round(base27,4))
for k in nets:
    S=ld(A14+f"PN1_{k[0]}_s{k[1]}__ffhq_lcomb.npz"); L=np.array([S[i] for i in ids])
    a0=auc(L[y==1],L[y==0])
    rm=spearmanr(L[y==1],f[y==1]).correlation; rg=spearmanr(L[y==0],f[y==0]).correlation
    # stratified AUC: within-decile AUC weighted by pairs
    num=den=0
    for b in range(10):
        pm=L[(bins==b)&(y==1)]; pg=L[(bins==b)&(y==0)]
        if len(pm) and len(pg):
            w=len(pm)*len(pg); num+=auc(pm,pg)*w; den+=w
    # matched: nearest-genuine per morph on f (with replacement), caliper 0.1 SD
    sd=f.std(); fg=f[y==0]; Lg=L[y==0]; o=np.argsort(fg)
    mm=[];mg=[]
    for v,l in zip(f[y==1],L[y==1]):
        k2=np.searchsorted(fg[o],v); cand=[c for c in (k2-1,k2) if 0<=c<len(o)]
        c=min(cand,key=lambda c:abs(fg[o][c]-v))
        if abs(fg[o][c]-v)<=0.1*sd: mm.append(l); mg.append(Lg[o][c])
    mm=np.array(mm);mg=np.array(mg)
    pair=np.mean(mm>mg)+0.5*np.mean(mm==mg)
    # residual: regress logit on f (spline-ish: cubic) in genuine only, apply to all
    P=np.polyfit(f[y==0],L[y==0],3); R=L-np.polyval(P,f)
    ar=auc(R[y==1],R[y==0])
    c1=cvauc(np.c_[f,L]); c27=cvauc(np.c_[X,L])
    print(k,"auc",round(a0,3),"rho_f morph",round(rm,2),"gen",round(rg,2),"strat",round(num/den,3),
          "matched n",len(mm),"pairAUC",round(pair,3),"resid(gen-fit cubic)",round(ar,3),"CV f+L",round(c1,3),"CV27+L",round(c27,3))

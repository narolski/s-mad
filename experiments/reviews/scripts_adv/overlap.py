import csv, numpy as np
from sklearn.metrics import roc_auc_score as A
F="/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/"
R=list(csv.DictReader(open(F+"lcomb_regional_heldout.csv")))
y=np.array([int(r["label"]) for r in R]); ids=[r["id"] for r in R]
for col in ("surround_single","surround_logreg","surround_gbt","face_gbt"):
    s=np.array([float(r[col]) for r in R])
    print(col,"AUC",round(A(y,s),4))
s=np.clip(np.array([float(r["surround_gbt"]) for r in R]),1e-6,1-1e-6); z=np.log(s/(1-s))
m,g=z[y==1],z[y==0]
bins=np.linspace(z.min(),z.max(),41)
hm,_=np.histogram(m,bins,density=True); hg,_=np.histogram(g,bins,density=True)
print("OVL (overlap coefficient, gbt surround logit, 40 bins):",round(np.sum(np.minimum(hm,hg))*(bins[1]-bins[0]),3))
for q in (50,75,90,95,99):
    t=np.percentile(g,q); print(f"morphs below genuine p{q}: {np.mean(m<t):.3f} ({int(np.sum(m<t))})")
for q in (1,5,10,25,50):
    t=np.percentile(m,q); print(f"genuine above morph p{q}: {np.mean(g>t):.3f} ({int(np.sum(g>t))})")
# common support via deciles of pooled score
dec=np.percentile(z,np.linspace(0,100,11))
idx=np.clip(np.searchsorted(dec,z,side='right')-1,0,9)
print("pooled deciles (morph, genuine):",[(int(((idx==k)&(y==1)).sum()),int(((idx==k)&(y==0)).sum())) for k in range(10)])
# weights using gbt and logreg score as propensity proxies (cross-fitted scores, base rate 1/3)
for col in ("surround_logreg","surround_gbt"):
    p=np.clip(np.array([float(r[col]) for r in R]),1e-3,1-1e-3)
    # ATT: morphs w=1, genuine w=p/(1-p)
    wg=p[y==0]/(1-p[y==0]); essg=wg.sum()**2/(wg**2).sum()
    # overlap weights: morph 1-p, genuine p
    wm=1-p[y==1]; wo=p[y==0]
    print(col,"ATT ESS genuine",round(essg,1),"| overlap-weight ESS morph",round(wm.sum()**2/(wm**2).sum(),1),"genuine",round(wo.sum()**2/(wo**2).sum(),1))
# IPW file check
W={r["id"]:float(r["weight"]) for r in csv.DictReader(open(F+"lcomb_ipw_weights.csv"))}
w=np.array([W[i] for i in ids]); wm=w[y==1]
print("IPW ESS morph recomputed",round(wm.sum()**2/(wm**2).sum(),2),"genuine",round(w[y==0].sum()**2/(w[y==0]**2).sum(),2))
srt=np.sort(wm)[::-1]; print("top-10 morph weight share",round(srt[:10].sum()/wm.sum(),3), "max",round(srt[0],1))
# lcomb_bal check with full-data held-out scores
B={r["id"]:int(r["label"]) for r in csv.DictReader(open(F+"lcomb_bal_rows.csv"))}
mask=np.array([i in B for i in ids]); print("bal rows found",mask.sum(), "morph",int(y[mask].sum()))
for col in ("surround_single","surround_logreg","surround_gbt","face_single","face_logreg","face_gbt","file_single"):
    s=np.array([float(r[col]) for r in R]); print("on bal rows, full-data held-out",col,round(A(y[mask],s[mask]),3))

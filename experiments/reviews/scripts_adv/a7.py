import sys, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
M={r["id"]:r for r in csv.DictReader(open("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm_meta.csv"))}
rl=C.build("lcomb"); X,nm=RF.X_of(rl); y=np.array([l for _,_,l,_ in rl]); g=FL.components([p for *_,p in rl])
ids=[r[0].replace("lcomb_","") for r in rl]; miss=sum(i not in M for i in ids); print("missing meta",miss)
fam={i:M[i]["src"].split("/")[-2] if i in M else "" for i in ids}
print("pos src fam", set(fam[i] for i,l in zip(ids,y) if l==1), "neg sample", list(set(fam[i] for i,l in zip(ids,y) if l==0))[:3])
V={k:np.array([float(M[i][k]) for i in ids]) for k in ("pre_w","pre_ied","scale","border_frac","pre_png_bytes")}
for k,v in V.items():
    print(k,"pos med/sd %.4g/%.3g"%(np.median(v[y==1]),v[y==1].std()),"neg %.4g/%.3g"%(np.median(v[y==0]),v[y==0].std()),"AUC %.3f"%FL.auc(v,y))
H=list(csv.DictReader(open("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_heldout.csv")))
nu=np.array([float(h["nu_gbt"]) for h in H])
from scipy.stats import spearmanr
for k in ("pre_ied","pre_w","scale"):
    for lab,w in (("pos",y==1),("neg",y==0)): print("rho nu_gbt~%s %s %.3f"%(k,lab,spearmanr(nu[w],V[k][w])[0]))
# floor using metadata only
Z=np.c_[V["pre_w"],V["pre_ied"],V["scale"],V["border_frac"]]
fl=FL.folds(y,g)
for m in ("logreg","gbt"):
    s,_=FL.crossfit(Z,y,g,m,fl); print("meta-only floor",m,round(FL.auc(s,y),3))
# nuisance floor restricted to morphs with pre_ied within +-1px of median and genuine with scale<1 (shrunk)
med=np.median(V["pre_ied"][y==1]); w=(np.abs(V["pre_ied"]-med)<1.0)
print("rows in |ied-med|<1:",int(w[y==1].sum()),int(w[y==0].sum()))
NU=[i for i,n in enumerate(nm) if n.startswith(("BORDER:","RES:","STORE:","RENDER:"))]
fl2=FL.folds(y[w],g[w])
for m in ("logreg","gbt"):
    s,_=FL.crossfit(X[w][:,NU],y[w],g[w],m,fl2); print("nuis floor in IED band",m,round(FL.auc(s,y[w]),3))
SUR=[nm.index("F27:noise_std_border"),nm.index("F27:lapvar_border")]
s,_=FL.crossfit(X[w][:,SUR],y[w],g[w],"logreg",fl2); print("surround floor in IED band",round(FL.auc(s,y[w]),3))

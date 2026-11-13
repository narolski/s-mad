import sys, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
name=sys.argv[1]; cal=float(sys.argv[2])
rl=C.build(name); X,nm=RF.X_of(rl); y=np.array([l for _,_,l,_ in rl]); g=FL.components([p for *_,p in rl])
H=list(csv.DictReader(open(f"/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/{name}_heldout.csv")))
p=np.clip(np.array([float(h["nu_gbt"]) for h in H]),1e-4,1-1e-4); L=np.log(p/(1-p)); sd=L.std()
pos=np.where(y==1)[0]; neg=list(np.where(y==0)[0]); used=set(); pairs=[]
rng=np.random.default_rng(0)
for i in rng.permutation(pos):
    cand=[j for j in neg if j not in used and abs(L[j]-L[i])<cal*sd]
    if cand:
        j=min(cand,key=lambda j:abs(L[j]-L[i])); used.add(j); pairs.append((i,j))
idx=np.array([k for pr in pairs for k in pr]); ym=y[idx]; gm=g[idx]
print(name,"matched pairs",len(pairs),"of",len(pos))
NU=[i for i,n in enumerate(nm) if n.startswith(("BORDER:","RES:","STORE:","RENDER:"))]
fl=FL.folds(ym,gm)
for lab,cols in (("nuis",NU),("all",list(range(X.shape[1]))),("F27",[i for i,n in enumerate(nm) if n.startswith("F27:")]),("BLEND",[i for i,n in enumerate(nm) if n.startswith("BLEND:")])):
    for m in ("logreg","gbt"):
        s,_=FL.crossfit(X[idx][:,cols],ym,gm,m,fl); print("  refit",lab,m,round(FL.auc(s,ym),3))
for n in ["F27:noise_std_face","RENDER:resid_corr_gb","F27:noise_std_border","BLEND:eye_lap_energy"]:
    j=nm.index(n); print("  single",n,round(FL.auc(X[idx,j],ym),3))

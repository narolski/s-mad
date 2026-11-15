import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
def get(name):
    rl = C.build(name); X, nm = RF.X_of(rl); y = np.array([l for _, _, l, _ in rl])
    g = FL.components([p for *_, p in rl]); return X, y, g, nm
def sub(nm, pref): return [i for i,n in enumerate(nm) if n.startswith(pref)]
X,y,g,nm = get("lcomb"); fl = FL.folds(y,g)
sets = {"RES":("RES:",),"RENDER":("RENDER:",),"BORDER+STORE":("BORDER:","STORE:"),
        "RES+BORDER+STORE":("RES:","BORDER:","STORE:"),"nuis-RENDER-resid":None,
        "RES_frame_only":("RES:frame",),"RES_face_only":("RES:face",)}
for k,p in sets.items():
    if p is None: cols=[i for i,n in enumerate(nm) if n.startswith(("RES:","BORDER:","STORE:","RENDER:")) and "resid_corr" not in n]
    else: cols=sub(nm,p)
    for m in ("logreg","gbt"):
        s,_=FL.crossfit(X[:,cols],y,g,m,fl); print("lcomb",k,m,round(FL.auc(s,y),3))
# transfer: fit nuisance models on one contrast, apply to another
NU=("BORDER:","RES:","STORE:","RENDER:")
def fit_apply(a,b):
    Xa,ya,_,nm=get(a); Xb,yb,_,_=get(b); cols=sub(nm,NU)
    for m in ("logreg","gbt"):
        Xtr,Xte,keep=FL._clean(Xa[:,cols],Xb[:,cols]); mod=FL._model(m).fit(Xtr,ya)
        print("transfer nuis",m,a,"->",b, round(FL.auc(mod.predict_proba(Xte)[:,1],yb),3))
    cols=list(range(Xa.shape[1]))
    for m in ("logreg","gbt"):
        Xtr,Xte,keep=FL._clean(Xa[:,cols],Xb[:,cols]); mod=FL._model(m).fit(Xtr,ya)
        print("transfer all ",m,a,"->",b, round(FL.auc(mod.predict_proba(Xte)[:,1],yb),3))
fit_apply("test_cv_R4_vs_R2w","lcomb")
fit_apply("lcomb","test_cv_R4_vs_R2w")
fit_apply("lcomb","test_fm_R4_vs_R2w")
fit_apply("test_cv_R4_vs_R3","lcomb")

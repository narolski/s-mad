import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
SUR=["F27:noise_std_border","F27:lapvar_border"]
FACE=["F27:noise_std_face","F27:lapvar_face","RENDER:resid_corr_gb","RENDER:resid_corr_rg"]
for name in ["lcomb","test_S4_vs_S3","dev_S4_vs_S0","test_cv_R4_vs_R2w","test_cv_R4_vs_R3"]:
    try: rl=C.build(name)
    except Exception as e: print(name,"ERR",e); continue
    X,nm=RF.X_of(rl); y=np.array([l for _,_,l,_ in rl]); g=FL.components([p for *_,p in rl]); fl=FL.folds(y,g)
    out=[]
    for n in SUR+FACE:
        j=nm.index(n); a=FL.auc(X[:,j],y); out.append("%s=%.3f"%(n.split(':')[1],a))
    for lab,cols in (("surround2",SUR),("face4",FACE)):
        s,_=FL.crossfit(X[:,[nm.index(c) for c in cols]],y,g,"logreg",fl); out.append("%s_cv=%.3f"%(lab,FL.auc(s,y)))
    print(name,len(y),"; ".join(out))

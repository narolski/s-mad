import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
for name in ["test_cv_R4_vs_R2w","test_fm_R4_vs_R2w","test_cv_R4_vs_R3","test_fm_R4_vs_R3"]:
    rl=C.build(name); X,nm=RF.X_of(rl); y=np.array([l for _,_,l,_ in rl])
    res=[]
    for j,n in enumerate(nm):
        if not n.startswith(("BORDER:","RES:","STORE:","RENDER:")): continue
        x=X[:,j]; ok=np.isfinite(x); a=FL.auc(x[ok],y[ok]) if len(np.unique(x[ok]))>1 else 0.5
        res.append((max(a,1-a),n,np.nanmedian(x[y==1]),np.nanmedian(x[y==0])))
    res.sort(reverse=True); print("==",name)
    for r in res[:8]: print("  %.3f %-26s pos=%.4g neg=%.4g"%r)
    # pngmeta check
    for n in ["STORE:png_zlib_level","STORE:png_filter1_share","STORE:png_n_idat"]:
        j=nm.index(n); print("  ",n, np.unique(X[y==1,j])[:5], np.unique(X[y==0,j])[:5])
    # pairing: same hosts?
    hp=set(r[0].split("_")[-1] for r in rl[:5]); print("  ids", [r[0] for r in rl[:2]], [r[0] for r in rl if r[2]==0][:2], "persons", rl[0][3], [r for r in rl if r[2]==0][0][3])

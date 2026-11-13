import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
R=["F27:noise_face_over_border","F27:lap_face_over_border","BLEND:face_over_border_grad"]
for name in ["lcomb","dev_S4_vs_S0","test_S4_vs_S3","test_cv_R4_vs_R2w"]:
    rl=C.build(name); X,nm=RF.X_of(rl); y=np.array([l for _,_,l,_ in rl]); g=FL.components([p for *_,p in rl]); fl=FL.folds(y,g)
    o=["%s=%.3f"%(c.split(':')[1],FL.auc(X[:,nm.index(c)],y)) for c in R]
    s,_=FL.crossfit(X[:,[nm.index(c) for c in R]],y,g,"logreg",fl); o.append("ratio3_cv=%.3f"%FL.auc(s,y))
    print(name,"; ".join(o))

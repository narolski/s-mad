import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
R=C.rows(C.AB1X)
def mk(pos,neg):
    P=C.sel(R,**pos); N=C.sel(R,**neg)
    return [(r["id"],C.resolve(r["path"]),1,C.persons(r)) for r in P]+[(r["id"],C.resolve(r["path"]),0,C.persons(r)) for r in N]
SUR=["F27:noise_std_border","F27:lapvar_border"]; FACE=["F27:noise_std_face","F27:lapvar_face","RENDER:resid_corr_gb","RENDER:resid_corr_rg"]
NU=("BORDER:","RES:","STORE:","RENDER:")
for lab,pos,neg in [("R2w(cv) vs R0",dict(fam="ladder",rung="R2w",strength="",tool="opencv"),dict(fam="ladder",rung="R0",strength="")),
                    ("R2w(all) vs R0",dict(fam="ladder",rung="R2w",strength=""),dict(fam="ladder",rung="R0",strength="")),
                    ("R3 vs R0",dict(fam="ladder",rung="R3",strength=""),dict(fam="ladder",rung="R0",strength="")),
                    ("ffhq bona vs lcomp resmatch",dict(fam="ffhq",rung="ffhq_bona_orig"),dict(fam="ffhq",rung="landmark_complete_resmatch")),
                    ("lcomp resmatch vs lcomb resmatch",dict(fam="ffhq",rung="landmark_complete_resmatch"),dict(fam="ffhq_lcomb",rung="landmark_combined_resmatch")),
                    ("lcomp orig vs lcomb orig",dict(fam="ffhq",rung="landmark_complete_orig"),dict(fam="ffhq_lcomb",rung="landmark_combined_orig"))]:
    try: rl=mk(pos,neg)
    except Exception as e: print(lab,"ERR",repr(e)); continue
    if not rl or len(set(r[2] for r in rl))<2: print(lab,"empty",len(rl)); continue
    try: X,nm=RF.X_of(rl)
    except AssertionError as e: print(lab,"nofeat",str(e)[:80]); continue
    y=np.array([l for _,_,l,_ in rl]); g=FL.components([p for *_,p in rl]); fl=FL.folds(y,g)
    o=[]
    for c in SUR+FACE: o.append("%s=%.3f"%(c.split(':')[1],FL.auc(X[:,nm.index(c)],y)))
    for l2,cols in (("sur_cv",[nm.index(c) for c in SUR]),("nuis_gbt",[i for i,n in enumerate(nm) if n.startswith(NU)])):
        s,_=FL.crossfit(X[:,cols],y,g,"gbt" if "gbt" in l2 else "logreg",fl); o.append("%s=%.3f"%(l2,FL.auc(s,y)))
    print(lab,int(y.sum()),int(len(y)-y.sum()),"; ".join(o))

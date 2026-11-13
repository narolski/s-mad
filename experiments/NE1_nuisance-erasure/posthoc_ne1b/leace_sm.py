# post hoc, descriptive review checks (read-only): LEACE in-sample correctness and oblique-projector norm;
# second-moment of border logits after erasure (half-B pairs).
import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/NE1")
import ne1b as E, ne1_heads as N
F="/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats"; M="/mnt/t7/smad_next/NE1"; NT="/mnt/t7/smad_next/NE1/nets_tree/ne1nets/nets"
for n in E.NETS:
    D,w,b=N.load(F,M,NT,n,False)
    T,Gt,Rd=D["train"],D["gate"],D["read"]
    rcam=N.sel(Gt,Gt["kind"]=="R_cam"); B=N.sel(Rd,Rd["set"]=="B")
    hA=lambda x: np.array([N.half_a(h) for h in x["host"]])
    BA,BB=N.sel(B,hA(B)),N.sel(B,~hA(B)); rA,rB=N.sel(rcam,hA(rcam)),N.sel(rcam,~hA(rcam))
    masks=sorted({k.split(":")[1] for k in B["kind"]})
    XL=np.concatenate([rA["F"],BA["F"]]); zL=np.r_[np.zeros(len(rA["F"]),int),[1+masks.index(k.split(":")[1]) for k in BA["kind"]]]
    Le,diag=E.leace_eraser(XL,zL)
    Y=Le(XL); spreadA=max(np.linalg.norm(Y[zL==k].mean(0)-Y[zL==0].mean(0)) for k in range(1,8))
    # operator: r(x)=x-(x-mu)M^T ; I-M^T norm
    Id=np.eye(XL.shape[1]); Mt=(Le(Id+XL.mean(0))-XL.mean(0))  # = I - M^T applied to unit rows -> rows of (I-M^T)
    sv=np.linalg.svd(Mt,compute_uv=False)
    D7=np.stack([BA["F"][BA["kind"]==f"border:{m}"].mean(0)-rA["F"].mean(0) for m in masks],1)
    E7,Q=E.span_eraser(D7)
    # half-B mean diffs: decompose into in-span and off-span
    DB=np.stack([BB["F"][BB["kind"]==f"border:{m}"].mean(0)-rB["F"].mean(0) for m in masks],1)
    off=np.linalg.norm(DB-Q@(Q.T@DB),axis=0); tot=np.linalg.norm(DB,axis=0)
    # second moment: refit heads, paired logits
    ridx={i:k for k,i in enumerate(rcam["id"])}; bp=np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    bm=np.array([k.split(":")[1] for k in BB["kind"]])
    D7c=np.stack([BB["F"][BB["kind"]==f"border:{m}"].mean(0)-rB["F"].mean(0) for m in masks],1); E7c,_=E.span_eraser(D7c)
    res={}
    for name,f in (("H1",None),("E7r",E7),("E7cr",E7c),("LEACEr",Le)):
        X=T["F"] if f is None else f(T["F"]); m=N.logreg(X,T["y"]); ww,bb=m.coef_[0],m.intercept_[0]
        g=lambda Z: (Z if f is None else f(Z))@ww+bb
        sc_b=g(BB["F"]); sc_p=g(rcam["F"])[bp]
        rows=[]
        for mk in ("cfp_ff","msu_mfsd","agedb_30"):
            s=bm==mk; dl=sc_b[s]-sc_p[s]
            rows.append("%s mean %.3f sd(copy)/sd(photo) %.3f sd(dl) %.3f"%(mk[:6],dl.mean(),sc_b[s].std()/sc_p[s].std(),dl.std()))
        res[name]=rows
    print(n,"LEACE in-sample spread %.2e (before %.3f)"%(spreadA, max(np.linalg.norm(XL[zL==k].mean(0)-XL[zL==0].mean(0)) for k in range(1,8))),
          "||I-M|| max sv %.2f, #sv<0.5 %d"%(sv.max(),(sv<0.5).sum()), "halfB off-span frac of mean diff", np.round(off/tot,2))
    for k,v in res.items(): print("  ",k," | ".join(v))
    sys.stdout.flush()

import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/NE1")
import ne1_heads as N
F="/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats"; M="/mnt/t7/smad_next/NE1"; NT="/mnt/t7/smad_next/NE1/nets_tree/ne1nets/nets"
def hm(dl,hosts):
    u,inv=np.unique(hosts,return_inverse=True); return float((np.bincount(inv,dl)/np.bincount(inv)).mean())
for n in N.NETS:
    D,w,b = N.load(F,M,NT,n,False)
    T,Gt,Rd = D["train"],D["gate"],D["read"]
    rcam = N.sel(Gt, Gt["kind"]=="R_cam"); B=N.sel(Rd,Rd["set"]=="B"); L=N.sel(Rd,Rd["set"]=="L"); S=N.sel(Rd,Rd["set"]=="S"); Cc=N.sel(Rd,Rd["set"]=="C")
    hA=lambda d: np.array([N.half_a(h) for h in d["host"]])
    P = N.cat(rcam, N.sel(L, np.char.startswith(L["kind"].astype(str),"ladder:R0:")))
    BB=N.sel(B,~hA(B)); ridx={i:k for k,i in enumerate(rcam["id"])}
    bpair=np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    d3=N.unit(B["F"][hA(B)].mean(0)-rcam["F"][hA(rcam)].mean(0))
    # per-mask logit shift before / after
    dl0=(BB["F"]-rcam["F"][bpair])@w
    Xe=lambda X: N.erase(X,d3)
    dl1=(Xe(BB["F"])-Xe(rcam["F"][bpair]))@w
    pm={k.split(":")[1]:(round(dl0[BB['kind']==k].mean(),2),round(dl1[BB['kind']==k].mean(),2)) for k in np.unique(BB["kind"])}
    # PCA of T
    Tc=T["F"]-T["F"].mean(0); ev,V=np.linalg.eigh(np.cov(T["F"],rowvar=False)); ev=ev[::-1];V=V[:,::-1]
    pc1=V[:,0]
    # does PC1 separate morph/genuine in T?
    p1=T["F"]@pc1
    a_pc1=N.auc(p1[T["y"]==1],p1[T["y"]==0])
    print(n, f"PC1 var {ev[0]/ev.sum():.3f} PC2 {ev[1]/ev.sum():.3f} |cos(pc1,d3)|={abs(pc1@d3):.2f} PC1 morph AUC(T) {max(a_pc1,1-a_pc1):.3f} |cos(pc1,w)|={abs(pc1@w)/np.linalg.norm(w):.2f}")
    print("   logit-unit removal H0e:", f"{1-hm(dl1,BB['host'])/hm(dl0,BB['host']):.2f}", " per-mask (before, after):", pm)
    # isotropic null and H1 removal in rank units
    H1=N.head_of(N.logreg(T["F"],T["y"]))
    def bshift(h):
        ref=np.sort(N.score(h,P["F"])); return hm(N.prank(N.score(h,BB["F"]),ref)-N.prank(N.score(h,rcam["F"])[bpair],ref),BB["host"])
    def lshift(h):
        return hm(N.score(h,BB["F"])-N.score(h,rcam["F"])[bpair],BB["host"])
    s1=bshift(H1); l1=lshift(H1)
    H3=N.head_of(N.logreg(N.erase(T["F"],d3),T["y"]),d3)
    print(f"   H1 rank {s1:+.3f} logit {l1:+.3f}; H3 rank {bshift(H3):+.3f} logit {lshift(H3):+.3f} -> logit removal {1-lshift(H3)/l1:.2f}")
    rng=np.random.default_rng(7)
    iso=[];isol=[]; cov=np.cov(T["F"],rowvar=False); g=np.random.default_rng(20261129)
    for j in range(20):
        dn=N.unit(rng.normal(size=512)); h=N.head_of(N.logreg(N.erase(T["F"],dn),T["y"]),dn)
        iso.append(1-bshift(h)/s1); isol.append(1-lshift(h)/l1)
    cn=[];cl=[];cs=[]
    for j in range(20):
        dn=N.unit(g.multivariate_normal(np.zeros(512),cov,method="eigh")); h=N.head_of(N.logreg(N.erase(T["F"],dn),T["y"]),dn)
        cn.append(1-bshift(h)/s1); cl.append(1-lshift(h)/l1); cs.append(abs(dn@pc1))
    print(f"   isotropic null rank-removal max {max(iso):.2f} med {np.median(iso):.2f}; logit max {max(isol):.2f}")
    print(f"   cov-null (fresh stream) rank max {max(cn):.2f}, logit max {max(cl):.2f}, |cos pc1| med {np.median(cs):.2f}; corr(rank-removal, |cos pc1|) {np.corrcoef(cn,cs)[0,1]:.2f}")
    # storage saturation
    Sp=N.sel(S,np.char.startswith(S["kind"].astype(str),"photo:")); SB=N.sel(Sp,~hA(Sp))
    h0=(None,w,b); ref=np.sort(N.score(h0,P["F"]))
    for k in ("photo:","photo:fm61","photo:amsl112"):
        s=N.score(h0,SB["F"][SB["kind"]==k]); r=N.prank(s,ref)
        print(f"   S {k:14s} n={len(s)} logit mean {s.mean():+.2f} rank mean {r.mean():.3f} share rank==1 {np.mean(r>=0.9999):.2f} share rank<=0 {np.mean(r<=1e-4):.2f} flag@0 {np.mean(s>0):.3f}")
    sc=N.score(h0,Cc["F"]); g0=Cc["kind"]!="landmark_combined_orig"
    print(f"   C resmatch genuine rank mean {N.prank(sc[g0],ref).mean():.3f}; P logit range {ref[0]:.2f}..{ref[-1]:.2f}")

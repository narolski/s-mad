import sys, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/NE1")
import ne1_heads as N
F="/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats"; M="/mnt/t7/smad_next/NE1"; NT="/mnt/t7/smad_next/NE1/nets_tree/ne1nets/nets"
for n in N.NETS:
    D,w,b = N.load(F,M,NT,n,False)
    T,Gt,Rd = D["train"],D["gate"],D["read"]
    rcam = N.sel(Gt, Gt["kind"]=="R_cam"); B=N.sel(Rd,Rd["set"]=="B"); L=N.sel(Rd,Rd["set"]=="L"); S=N.sel(Rd,Rd["set"]=="S")
    hA=lambda d: np.array([N.half_a(h) for h in d["host"]])
    P = N.cat(rcam, N.sel(L, np.char.startswith(L["kind"].astype(str),"ladder:R0:")))
    BB=N.sel(B,~hA(B)); ridx={i:k for k,i in enumerate(rcam["id"])}
    bpair=np.array([ridx[i.split("__")[0][len("bref_"):]] for i in BB["id"]])
    d3=N.unit(B["F"][hA(B)].mean(0)-rcam["F"][hA(rcam)].mean(0))
    def hostmean(dl,hosts):
        u,inv=np.unique(hosts,return_inverse=True); return float((np.bincount(inv,dl)/np.bincount(inv)).mean())
    out=[]
    for name,d in (("H0",None),("H0e",d3)):
        h=(d,w,b); sP=np.sort(N.score(h,P["F"])); sB=N.score(h,BB["F"]); sR=N.score(h,rcam["F"])[bpair]
        dlog=sB-sR
        rB=N.prank(sB,sP); rR=N.prank(sR,sP)
        out.append(f"{name}: logitΔ hostmean {hostmean(dlog,BB['host']):+.3f} median {np.median(dlog):+.3f} frac>0 {np.mean(dlog>0):.2f} | rankΔ {hostmean(rB-rR,BB['host']):+.3f} | photo rank mean {rR.mean():.2f} copy rank mean {rB.mean():.2f} | sdP {sP.std():.2f}")
    # projection decomposition
    xB=BB["F"]@d3; xR=rcam["F"][bpair]@d3
    print(n, f"w·d3={w@d3:+.3f} |w|={np.linalg.norm(w):.2f}  mean proj copy {xB.mean():+.3f} photo {xR.mean():+.3f} P {(P['F']@d3).mean():+.3f}")
    # perp part of copy-photo diff contribution
    dperp = (BB["F"]-rcam["F"][bpair]); dperp = dperp - np.outer(dperp@d3,d3)
    print("   w·mean(Δperp) =", f"{(dperp@w).mean():+.3f}", " w·d3*mean(Δpar)=", f"{(w@d3)*(xB-xR).mean():+.3f}")
    for o in out: print("  ",o)
    # P projection on d3 shift: erasure moves P scores by -(x·d)(w·d)
    print("   P proj on d3 mean", f"{(P['F']@d3).mean():+.3f}", " photo(rcam half B) proj", f"{xR.mean():+.3f}", " copy proj", f"{xB.mean():+.3f}")

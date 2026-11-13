# post hoc, descriptive: replicate ne1b.part_b exactly (same rng stream) and print FFHQ C cost for nulls,
# second-moment of border logits after erasure, LEACE in-sample check. Read-only.
import sys, json, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/NE1")
import ne1b as E, ne1_heads as N
F="/mnt/t7/smad_next/NE1/results/unpacked/NE1_feats/feats"; M="/mnt/t7/smad_next/NE1"; NT="/mnt/t7/smad_next/NE1/nets_tree/ne1nets/nets"
ref=json.load(open("/home/narolski/smad-next/experiments/NE1_nuisance-erasure/ne1b_read.json"))
rng=np.random.default_rng(20261130)
out={}
for n in E.NETS:
    D,w,b=N.load(F,M,NT,n,False)
    R,heads,reads,sc,info=E.part_b(D,w,b,rng)
    # reproduction check
    for h in ("H1","E7r","LEACEr"):
        assert abs(R[h]["dflag"]-ref["nets"][n]["partB"]["heads"][h]["dflag"])<1e-9,(n,h)
    o={}
    for t in "IVM":
        o[t]=dict(recC_loss=[round(R["H1"]["recall_C_p99"]-R[f"{t}{j:02d}r"]["recall_C_p99"],3) for j in range(20)],
                  aucC_loss=[round(R["H1"]["auc_C"]-R[f"{t}{j:02d}r"]["auc_C"],3) for j in range(20)])
    # second moment: per head, std of copy logits / std of photo logits (half B pairs), and tail
    T,Gt,Rd=D["train"],D["gate"],D["read"]
    o["E7_C"]=(round(R["H1"]["recall_C_p99"]-R["E7r"]["recall_C_p99"],3),round(R["H1"]["auc_C"]-R["E7r"]["auc_C"],3))
    sm={}
    for h in ("H1","E7r","E7cr","LEACEr"):
        s=sc[h]; bp=None
        sm[h]=dict(sd_copy=float(s["BB"].std()), sd_photo=float(s["rcam"].std()), thr=R[h]["thr"])
    o["sm"]=sm
    out[n]=o
    print(n, "E7 C loss", o["E7_C"])
    for t in "IVM":
        print("  null",t,"recC loss min/med/max %.3f %.3f %.3f"%(min(o[t]["recC_loss"]),np.median(o[t]["recC_loss"]),max(o[t]["recC_loss"])),
              "aucC loss med/max %.3f %.3f"%(np.median(o[t]["aucC_loss"]),max(o[t]["aucC_loss"])))
    print("  sd", {h:(round(v["sd_copy"],3),round(v["sd_photo"],3)) for h,v in sm.items()}, flush=True)
json.dump(out,open("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/ne1brev/nulls_c.json","w"))

import csv, sys, json, numpy as np
RAW, FL = sys.argv[1], "/mnt/t7/smad_next/SM1/flists"
rows=[]
for t in ("test_eval","test_mad22","test_ar1","test_ar1h","test_eval_jpeg"):
    rows += list(csv.DictReader(open(f"{FL}/{t}.csv")))
aud = list(csv.DictReader(open(f"{FL}/audit.csv")))
def conv(i):
    i=str(i)
    if i.startswith("mad22c/"): return "m22:"+(i[7:-4] if i.endswith(".png") else i[7:])
    if i.startswith(("ar1:","ar1h:","ev:")): return i
    return "ev:"+i
def load(fit):
    z={}
    for sub in ("ad4eval","ar1eval","jpegeval","audit"):
        f=np.load(f"{RAW}/{fit}/{sub}/"+("scores_audit.npz" if sub=="audit" else "scores_eval.npz"))
        p=np.clip(f["score_noTTA"].astype(np.float64),1e-7,1-1e-7)
        for i,v in zip(f["id"],np.log(p/(1-p))): z[str(i) if sub=="audit" else conv(i)]=v
    return z
def sel(z,cell,label,hist=None):
    return np.array([z[r["id"]] for r in rows if r["cell"]==cell and r["label"]==label and (hist is None or r["hist"]==hist) and r["id"] in z])
def eer(g,m):
    t=np.unique(np.concatenate([g,m])); fpr=np.array([(g>=x).mean() for x in t]); fnr=np.array([(m<x).mean() for x in t])
    j=np.argmin(abs(fpr-fnr)); return 100*(fpr[j]+fnr[j])/2
FR=("amsl","facemorpher","opencv","stylegan","webmorph"); DIM=("dim_a","dim_c","fast_dim","fast_dim_ode","greedy_dim","greedy_dim_s")
def cell(c):
    fam,f=c.split(":"); gn={"frllm":"frllm:bona","mordiff":"mordiff:bona","dim":"dim:bona","mad22":"mad22:bona"}[fam]
    return gn,c
L7=["frllm:amsl","frllm:facemorpher","frllm:opencv","frllm:webmorph","mad22:FaceMorpher","mad22:OpenCV","mad22:Webmorph"]
D7=["mordiff:mordiff"]+["dim:"+d for d in DIM]; G3=["frllm:stylegan","mad22:MIPGAN_I","mad22:MIPGAN_II"]
ALL=[f"frllm:{f}" for f in FR]+D7+[f"mad22:{f}" for f in ("FaceMorpher","MIPGAN_I","MIPGAN_II","OpenCV","Webmorph")]
out={}
for fit in sys.argv[2:]:
    z=load(fit); o={}
    def grp(cs):
        nat=[];e7=[]
        for c in cs:
            gn,mc=cell(c); m=sel(z,mc,"1","morph"); nat.append(eer(sel(z,gn,"0","native"),m)); e7.append(eer(sel(z,mc,"0","e7"),m))
        return np.mean(nat),np.mean(e7)-np.mean(nat)
    o["L7"],o["L7rise"]=grp(L7); o["D7"],o["D7rise"]=grp(D7); o["G3"],_=grp(G3)
    r0=sel(z,"ar1:frgcferet:none:R0","0"); tau=float(np.quantile(r0,0.95))
    fb=sel(z,"frllm:bona","0","native")
    # paired jpeg50
    jp={r["p1"]+r["expr"]:z[r["id"]] for r in rows if r["cell"]=="frllm:bona_jpeg50" and r["id"] in z}
    nt={r["p1"]+r["expr"]:z[r["id"]] for r in rows if r["cell"]=="frllm:bona" and r["hist"]=="native" and r["id"] in z}
    ks=sorted(set(jp)&set(nt))
    lm4=np.concatenate([sel(z,f"frllm:{f}","1","morph") for f in ("amsl","facemorpher","opencv","webmorph")])
    pools={c:sel(z,c,"0","e7") for c in ALL}
    own={c:float((v>=0).mean()) for c,v in pools.items() if len(v)}
    o.update(tau=tau, r0_p5_p50_p95=[float(np.quantile(r0,q)) for q in (.05,.5,.95)], n_r0=len(r0),
      frll_flag_cam=float((fb>=tau).mean()), frll_median=float(np.median(fb)), n_paired=len(ks),
      jpeg50_minus_cam=float(np.mean([jp[k]>=tau for k in ks])-np.mean([nt[k]>=tau for k in ks])),
      lm4_miss_cam=float((lm4<tau).mean()), lm4_miss_own=float((lm4<0).mean()), frll_flag_own=float((fb>=0).mean()),
      mordiff_e7_own=own["mordiff:mordiff"], max_pool_own=max(own.items(),key=lambda x:x[1]),
      mordiff_e7_cam=float((pools["mordiff:mordiff"]>=tau).mean()),
      logit_min=float(min(z.values())), logit_max=float(max(z.values())),
      morph_lm4_p5_p50=[float(np.quantile(lm4,q)) for q in (.05,.5)],
      mordiff_e7_q=[float(np.quantile(pools["mordiff:mordiff"],q)) for q in (.1,.5,.9)],
      mordiff_bona_q=[float(np.quantile(sel(z,"mordiff:bona","0","native"),q)) for q in (.1,.5,.9)],
      n_unique_r0=len(np.unique(np.round(r0,4))))
    # audit
    idx={(r["kind"],r["key"],int(r["slot"])):r["id"] for r in aud if r["kind"] in("KP","KE","KU")}
    keys=sorted({r["key"] for r in aud if r["kind"]=="KP"})
    M={k:np.array([[z[idx[(k,kk,j)]] for j in range(5)] for kk in keys]).mean(1) for k in ("KP","KE","KU")}
    d=M["KP"]-M["KE"]; o["TminusKE"]=float(d.mean()); o["_d"]=d.tolist()
    kp=np.array([z[i] for (k,_,_),i in idx.items() if k=="KP"]); ke=np.array([z[i] for (k,_,_),i in idx.items() if k=="KE"])
    o["KP_mean_max"]=[float(kp.mean()),float(kp.max())]; o["KE_mean_max_min"]=[float(ke.mean()),float(ke.max()),float(ke.min())]
    o["KP_sd"]=float(kp.std()); o["KE_sd"]=float(ke.std())
    o["auc_KP_vs_KE"]=float(((kp[:,None]>ke[None,:]).mean()+0.5*(kp[:,None]==ke[None,:]).mean()))
    out[fit]=o
json.dump(out,open(sys.argv[1]+"/../recomp.json","w"),indent=1)
for f,o in out.items():
    print(f, {k:(round(v,4) if isinstance(v,float) else v) for k,v in o.items() if k!="_d"})

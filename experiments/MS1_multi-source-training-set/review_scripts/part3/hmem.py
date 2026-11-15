import pickle, csv, numpy as np, sys
from scipy.stats import mannwhitneyu
S=pickle.load(open(sys.argv[1],"rb"))
E=list(csv.DictReader(open("/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv")))
MAN={"Sb":"/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv","SbM3":"/mnt/t7/smad_next/MS1/manifests/train_SbM3.csv","SbV":"/mnt/t7/smad_next/MS1/manifests/train_SbV.csv"}
HELD={"af0_photo":lambda r:r["fam"]=="af0" and r["role"]=="dev" and r["rung"]=="photo" and r["strength"]=="",
"af0_photo61":lambda r:r["fam"]=="af0" and r["role"]=="dev" and r["rung"]=="photo" and r["strength"]=="61",
"af0_zero":lambda r:r["fam"]=="af0" and r["role"]=="dev" and r["rung"]=="zero",
"af0_half":lambda r:r["fam"]=="af0" and r["role"]=="dev" and r["rung"] in("halfA","halfB"),
"af0_u50":lambda r:r["fam"]=="af0" and r["role"]=="dev" and r["rung"]=="u50" and r["strength"]=="",
"lad_R0":lambda r:r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R0" and r["strength"]=="",
"lad_R2w":lambda r:r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R2w" and r["strength"]=="",
"lad_R4":lambda r:r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R4" and r["strength"]=="",
"lad_S0":lambda r:r["fam"]=="splice" and r["role"]=="dev" and r["rung"]=="S0",
"lad_S3":lambda r:r["fam"]=="splice" and r["role"]=="dev" and r["rung"]=="S3",
"lad_S4":lambda r:r["fam"]=="splice" and r["role"]=="dev" and r["rung"]=="S4"}
ATT={"af0_u50","lad_R4","lad_S4"}
heldrows={k:[r for r in E if f(r)] for k,f in HELD.items()}
# held-out source mix and labels
for k,rs in heldrows.items():
    src={}; lab=set(r["label"] for r in rs)
    for r in rs: src[r["host"].split(":")[0]]=src.get(r["host"].split(":")[0],0)+1
    print("HELD",k,len(rs),src,"labels",lab)
mans={a:list(csv.DictReader(open(p))) for a,p in MAN.items()}
for a,m in mans.items():
    u={}
    for r in m: u.setdefault(r["path"],r)
    print("MAN",a,"rows",len(m),"unique",len(u))
    for k in HELD:
        rs=[r for r in u.values() if r["kind"]==k and r["db"] in("frgc","feret")]
        c={}; 
        for r in rs: c[r["db"]]=c.get(r["db"],0)+1
        mult=sum(1 for r in m if r["kind"]==k and r["db"] in("frgc","feret"))
        print("   ",k,len(rs),c,"labels",set(r["label"] for r in rs),"rows incl dup",mult)
    mans[a]=u
res={}
sig=lambda x:1/(1+np.exp(-x))
for (a,s),d in S.items():
    ev=dict(zip(d["scores_eval.npz"]["id"].astype(str),d["scores_eval.npz"]["logit"].astype(float)))
    tp=d["scores_train.npz"]["path"].astype(str); tl=d["scores_train.npz"]["logit"].astype(float); tk=d["scores_train.npz"]["kind"].astype(str)
    man=mans[a]; miss=0; kindmis=0; T={}
    for p,l,k in zip(tp,tl,tk):
        key=p[p.index("train/"):] if "train/" in p else p
        x=man.get(key)
        if x is None: miss+=1; continue
        if x["kind"]!=k: kindmis+=1
        if x["db"] in("frgc","feret"): T.setdefault((x["kind"],x["db"]),[]).append(l)
    r={}
    for k,rs in heldrows.items():
        t=np.array(sum([T.get((k,db),[]) for db in("frgc","feret")],[])); h=np.array([ev[x["id"]] for x in rs])
        sgn=1 if k in ATT else -1
        gap=sgn*(t.mean()-h.mean())
        pgap=sgn*(sig(t).mean()-sig(h).mean())
        # rank: P(train more confident than held)
        U=mannwhitneyu(sgn*t,sgn*h).statistic/(len(t)*len(h))
        # source-stratified gap
        sg={}
        for db in("frgc","feret"):
            tt=np.array(T.get((k,db),[])); hh=np.array([ev[x["id"]] for x in rs if x["host"].startswith(db)])
            if len(tt) and len(hh): sg[db]=sgn*(tt.mean()-hh.mean())
        r[k]=dict(gap=gap,pgap=pgap,auc=U,sg=sg,tmed=np.median(t),hmed=np.median(h))
    res[(a,s)]=r
    print("FIT",a,s,"train rows",len(tp),"unmatched",miss,"kind mismatch",kindmis)
pickle.dump(res,open(sys.argv[2],"wb"))

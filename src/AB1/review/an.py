import csv, numpy as np, pickle, sys, collections
from scipy.stats import rankdata
c=pickle.load(open(sys.argv[1],"rb")); nets=c["nets"]; D=c["D"]; lad=c["lad"]
dev,test,clean,linked=c["dev"],c["test"],c["clean"],c["linked"]
row={}
for r in csv.DictReader(open("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")):
    if r["strength"]!="": continue
    if r["fam"] in ("ladder","splice"): row[(r["rung"],r["tool"],r["host"])]=r["id"]
def auc(p,n):
    r=rankdata(np.concatenate([p,n])); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
def strat(ps,pd,ns,nd):
    ld=np.log(np.concatenate([pd,nd])); e=np.quantile(ld,[.2,.4,.6,.8])
    qp=np.searchsorted(e,np.log(pd),side="right"); qn=np.searchsorted(e,np.log(nd),side="right")
    num=den=used=0
    for k in range(5):
        a,b=ps[qp==k],ns[qn==k]
        if len(a)>=10 and len(b)>=10: w=len(a)*len(b); num+=w*auc(a,b); den+=w; used+=len(a)+len(b)
    if den==0 or used<0.5*(len(ps)+len(ns)): return None,used/(len(ps)+len(ns))
    return num/den, used/(len(ps)+len(ns))
C={"R4R3cv":("R4","R3","opencv"),"S4S3":("S4","S3","opencv"),"R4R3fm":("R4","R3","facemorpher")}
def arr(hosts,cn,x):
    p,n,t=C[cn]; dp="S4"
    ps=np.array([x[row[(p,t,h)]] for h in hosts]); ns=np.array([x[row[(n,t,h)]] for h in hosts])
    return ps,np.array([D[(dp,h)] for h in hosts]),ns,np.array([D[("S3",h)] for h in hosts])
S=range(408,413)
def stat(hosts,cn,arm,s,st=True):
    ps,pd,ns,nd=arr(hosts,cn,nets[(arm,s)])
    return strat(ps,pd,ns,nd)[0] if st else auc(ps,ns)
sets={"dev+clean80":dev+clean,"dev":dev,"clean80":clean,"test191":test}
for cn in C:
  for sn,H in sets.items():
    cov=strat(*arr(H,cn,nets[("Sb",408)]))[1]
    out=[]
    for o in "BA":
        g=[stat(H,cn,"Sb",s)-stat(H,cn,o,s) for s in S]; gu=[stat(H,cn,"Sb",s,False)-stat(H,cn,o,s,False) for s in S]
        out.append(f"Sb-{o} {np.mean(g):+.3f} (unstrat {np.mean(gu):+.3f}) pos {sum(x>0 for x in g)}/5")
    lv={a:np.mean([stat(H,cn,a,s) for s in S]) for a in ("A","B","Sb")}
    print(cn,sn,"cov%.2f"%cov," | ".join(out)," levels",{k:round(v,3) for k,v in lv.items()})
# components & bootstrap with own rng; report drop rate
def comps(H):
    hs=set(H); par={h:h for h in H}
    def f(x):
        while par[x]!=x: x=par[x]
        return x
    for h in H:
        p=lad[h]["partner_B"]
        if p in hs: par[f(h)]=f(p)
    d=collections.defaultdict(list)
    for h in H: d[f(h)].append(h)
    return list(d.values())
rng=np.random.default_rng(7)
for cn,sn in (("R4R3cv","dev+clean80"),("S4S3","clean80"),("R4R3cv","dev"),("R4R3cv","clean80")):
    H=sets[sn]; cp=comps(H); 
    for o in "BA":
        bs=[];bu=[];drop=0
        for _ in range(1000):
            hs=[h for k in rng.integers(0,len(cp),len(cp)) for h in cp[k]]
            v=[];vu=[]
            for s in S:
                a=stat(hs,cn,"Sb",s); b=stat(hs,cn,o,s)
                vu.append(stat(hs,cn,"Sb",s,False)-stat(hs,cn,o,s,False))
                if a is None or b is None: v=None; break
                v.append(a-b)
            bu.append(np.mean(vu))
            if v is None: drop+=1
            else: bs.append(np.mean(v))
        print(cn,sn,o,"ncomp",len(cp),"strat CI",np.round(np.percentile(bs,[2.5,97.5]),3),"dropped",drop,"/1000","unstrat CI",np.round(np.percentile(bu,[2.5,97.5]),3))
# decomposition vs bona fide R0 on dev+clean80 and clean80, opencv
for sn in ("dev+clean80","dev","clean80"):
    H=sets[sn]
    for a in ("A","B","Sb"):
        r=[]
        for s in S:
            x=nets[(a,s)]; r0=np.array([x[row[("R0","none",h)]] for h in H])
            r4=np.array([x[row[("R4","opencv",h)]] for h in H]); r3=np.array([x[row[("R3","opencv",h)]] for h in H])
            s3=np.array([x[row[("S3","opencv",h)]] for h in H]); s4=np.array([x[row[("S4","opencv",h)]] for h in H])
            r2w=np.array([x[row[("R2w","opencv",h)]] for h in H])
            r.append([auc(r4,r0),auc(r3,r0),auc(r2w,r0),np.mean(r4>0),np.mean(r3>0),np.mean(r0>0),np.mean(s4>0),np.mean(s3>0)])
        r=np.mean(r,0)
        print(sn,a,"AUC R4vR0 %.3f R3vR0 %.3f R2wvR0 %.3f | flag rate R4 %.2f R3 %.2f R0 %.2f S4 %.2f S3 %.2f"%tuple(r))
# per database
for sn in ("dev","clean80"):
    H=sets[sn]
    for db in ("feret","frgc"):
        Hd=[h for h in H if h.startswith(db)]
        if len(Hd)<10: print(sn,db,len(Hd)); continue
        g=[stat(Hd,"R4R3cv","Sb",s,False)-stat(Hd,"R4R3cv","B",s,False) for s in S]
        lv={a:round(np.mean([stat(Hd,"R4R3cv",a,s,False) for s in S]),3) for a in ("A","B","Sb")}
        print(sn,db,len(Hd),"unstrat Sb-B %+.3f"%np.mean(g),lv)

import csv, tarfile, io, sys, numpy as np, json
from scipy.stats import rankdata
sys.path.insert(0,"/home/narolski/smad-next/src/PN1"); import pn1lib as K
SP="/mnt/t7/smad_next"
def auc(p,n):
    r=rankdata(np.concatenate([p,n])); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
def sauc(p,pd,n,nd):
    ld=np.log(np.concatenate([pd,nd])); e=np.quantile(ld,[.2,.4,.6,.8])
    qp=np.searchsorted(e,np.log(pd),side="right"); qn=np.searchsorted(e,np.log(nd),side="right")
    num=den=0.;u=0
    for k in range(5):
        a,b=p[qp==k],n[qn==k]
        if len(a)>=10 and len(b)>=10: w=len(a)*len(b); num+=w*auc(a,b); den+=w; u+=len(a)+len(b)
    return None if den==0 or u<0.5*(len(p)+len(n)) else num/den
lad,_=K.split_tables()
dev=sorted(h for h,x in lad.items() if x["role"]=="dev")
test=sorted(h for h,x in lad.items() if x["role"]=="test" and x["test_read"]=="1")
clean=sorted(r["host"] for r in csv.DictReader(open(SP+"/DATA/overlap/test_hosts_clean_of_dev.csv")))
D={(r["rung"],r["host"]):float(r["D"]) for r in csv.DictReader(open(SP+"/BD1/d_values.csv"))}
def rows(man):
    row={}
    for r in csv.DictReader(open(man)):
        if r["strength"]!="": continue
        if r["fam"]=="ladder" and r["rung"] in ("R4","R3") and r["tool"]=="opencv": row[(r["rung"],r["host"])]=r["id"]
        if r["fam"]=="splice" and r["rung"] in ("S4","S3"): row[(r["rung"],r["host"])]=r["id"]
    return row
def load(path):
    t=tarfile.open(path); m=[x for x in t.getmembers() if x.name.endswith("/scores_eval.npz")][0]
    z=np.load(io.BytesIO(t.extractfile(m).read())); return dict(zip([str(i) for i in z["id"]],z["logit"].astype(float)))
which=sys.argv[1]
if which=="Sp":
    row=rows(SP+"/AB1/manifests/ab1_eval.csv"); seeds=list(range(408,413)); arms=("Sb","Sp","B","A")
    nets={(a,s):load(f"{SP}/AB1/results/AB1_{a}_s{s}.tar") for a in arms for s in seeds}
    pairs=[("Sb","Sp"),("Sp","B"),("Sb","B"),("Sb","A")]
else:
    row=rows(SP+"/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv"); seeds=list(range(403,408)); arms=("Sb","B","A")
    nets={(a,s):load(f"{SP}/PN1/results_fs/PN1_{a}_s{s}.tar") for a in arms for s in seeds}
    pairs=[("Sb","B"),("Sb","A")]
def comps(hosts):
    hs=set(hosts); par={h:h for h in hosts}
    def f(x):
        while par[x]!=x: x=par[x]
        return x
    for h in hosts:
        p=lad[h]["partner_B"]
        if p in hs: par[f(h)]=f(p)
    c={}
    for h in hosts: c.setdefault(f(h),[]).append(h)
    return list(c.values())
def stat(hosts,pr,nr,x):
    ph=[h for h in hosts if (pr,h) in row and ("S4",h) in D]; nh=[h for h in hosts if (nr,h) in row and ("S3",h) in D]
    p=np.array([x[row[(pr,h)]] for h in ph]); n=np.array([x[row[(nr,h)]] for h in nh])
    return sauc(p,np.array([D[("S4",h)] for h in ph]),n,np.array([D[("S3",h)] for h in nh])), auc(p,n)
rng=np.random.default_rng(777); out={}
for cn,(pr,nr) in {"R4R3":("R4","R3"),"S4S3":("S4","S3")}.items():
    for sn,hosts in {"dev+clean80":dev+clean,"dev":dev,"clean80":clean}.items():
        st={k:stat(hosts,pr,nr,x) for k,x in nets.items()}
        C=comps(hosts); B=1000
        draws=[rng.integers(0,len(C),len(C)) for _ in range(B)]
        bs={p:[] for p in pairs}; bu={p:[] for p in pairs}
        for dr in draws:
            hs=[h for k in dr for h in C[k]]
            sd={k:stat(hs,pr,nr,x) for k,x in nets.items()}
            for a,b in pairs:
                v=[sd[(a,s)][0]-sd[(b,s)][0] if sd[(a,s)][0] is not None and sd[(b,s)][0] is not None else None for s in seeds]
                if None not in v: bs[(a,b)].append(np.mean(v))
                bu[(a,b)].append(np.mean([sd[(a,s)][1]-sd[(b,s)][1] for s in seeds]))
        for a,b in pairs:
            g=[st[(a,s)][0]-st[(b,s)][0] for s in seeds]; gu=[st[(a,s)][1]-st[(b,s)][1] for s in seeds]
            r=dict(strat=round(np.mean(g),4),per_seed=[round(v,3) for v in g],unstr=round(np.mean(gu),4),
                   seed_t95=[round(np.mean(g)-2.776*np.std(g,ddof=1)/5**.5,3),round(np.mean(g)+2.776*np.std(g,ddof=1)/5**.5,3)],
                   ci_s=[round(np.percentile(bs[(a,b)],q),3) for q in (2.5,97.5)] if len(bs[(a,b)])>50 else None, n_s=len(bs[(a,b)]),
                   ci_u=[round(np.percentile(bu[(a,b)],q),3) for q in (2.5,97.5)])
            print(which,cn,sn,f"{a}-{b}",json.dumps(r),flush=True)

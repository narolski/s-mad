import csv, collections, sys
M="/mnt/t7/smad_next/PN1/manifests/"
def db(r):
    s=(r.get("src","")+r.get("id","")+r.get("path","")).lower()
    return "frgc" if "frgc" in s else ("feret" if "feret" in s else "?")
for arm in "AB":
    rows=list(csv.DictReader(open(M+f"train_{arm}.csv")))
    c=collections.Counter(); 
    for r in rows:
        h="61" if r["kind"].endswith("61") else "nat"
        c[(h,r["label"])]+=1
    print(arm,"rows",len(rows),"history x label",dict(c))
    for h in ("nat","61"):
        n0,n1=c[(h,"0")],c[(h,"1")]
        if n0+n1: print("  P(attack|%s)=%.3f"%(h,n1/(n0+n1)))
    src={r["id"]:r for r in csv.DictReader(open(M+f"src_{arm}.csv"))}
    d=collections.Counter()
    for r in rows:
        d[(db(src.get(r["id"],r)),r["label"])]+=1
    print("  db x label",dict(d))
    for k in ("frgc","feret"):
        n0,n1=d[(k,"0")],d[(k,"1")]
        if n0+n1: print("  P(attack|%s)=%.3f"%(k,n1/(n0+n1)))
    s=collections.Counter((("lad" if r["kind"].startswith("lad") else "af0"),r["label"]) for r in rows)
    print("  pool x label",dict(s))
# AF0 pair graph among training persons used in B
af=list(csv.DictReader(open("/mnt/t7/smad_next/AF0/manifest.csv")))
srcB={r["id"] for r in csv.DictReader(open(M+"src_B.csv"))}
used=[r for r in af if r["kind"]=="morph" and r["split"]=="train" and r["field"] in("zero","u50")]
par={}
def f(x):
    while par.setdefault(x,x)!=x: x=par[x]
    return x
for r in used:
    a,b=f(r["pid_A"]),f(r["pid_B"]); par[a]=b
comp=collections.Counter(f(p) for p in list(par))
sz=sorted(comp.values(),reverse=True)
print("AF0 train zero+u50 person graph: persons",len(par),"components",len(sz),"largest",sz[:5])
pz=collections.defaultdict(set)
for r in used: pz[(r["pid_A"],r["pid_B"])].add(r["field"]); 
both=sum(1 for k,v in pz.items() if len(v)>1)
print("ordered pairs with both zero and u50:",both)

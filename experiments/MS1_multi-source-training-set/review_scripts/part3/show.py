import pickle, numpy as np, sys
R=pickle.load(open(sys.argv[1],"rb"))
K=list(R[("Sb",403)].keys()); SE=range(403,408)
for a in ("Sb","SbM3","SbV"):
    print(a,"M",[round(np.mean([R[(a,s)][k]["gap"] for k in K]),3) for s in SE])
for stat in ("gap","pgap","auc"):
    print("==",stat)
    for k in K:
        row=[np.median([R[(a,s)][k][stat] for s in SE]) for a in ("Sb","SbM3","SbV")]
        n=sum(R[("SbM3",s)][k][stat]<R[("Sb",s)][k][stat] for s in SE)
        print("  %-12s Sb %.4f SbM3 %.4f SbV %.4f  SbM3<Sb %d/5"%(k,*row,n))
    for a in ("Sb","SbM3","SbV"):
        print("  mean-over-kinds",a,[round(np.mean([R[(a,s)][k][stat] for k in K]),4) for s in SE])
    print("  seeds SbM3<Sb:",sum(np.mean([R[("SbM3",s)][k][stat] for k in K])<np.mean([R[("Sb",s)][k][stat] for k in K]) for s in SE))
print("== source-stratified gap medians")
for k in K:
    for db in ("frgc","feret"):
        v=[np.median([R[(a,s)][k]["sg"].get(db,np.nan) for s in SE]) for a in ("Sb","SbM3")]
        print("  %-12s %-5s Sb %.3f SbM3 %.3f"%(k,db,*v))
print("== medians train/held")
for k in K:
    print("  %-12s"%k, " ".join("%s t%.2f h%.2f"%(a,np.median([R[(a,s)][k]["tmed"] for s in SE]),np.median([R[(a,s)][k]["hmed"] for s in SE])) for a in ("Sb","SbM3")))

import csv, tarfile, io, numpy as np, sys, collections, pickle
from scipy.stats import rankdata
SP="/mnt/t7/smad_next"
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n)
    r=rankdata(np.concatenate([p,n])); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
sys.path.insert(0,"/home/narolski/smad-next/src/PN1"); import pn1lib as K
lad,_=K.split_tables()
dev=sorted(h for h,x in lad.items() if x["role"]=="dev")
test=sorted(h for h,x in lad.items() if x["role"]=="test" and x["test_read"]=="1")
clean=sorted(r["host"] for r in csv.DictReader(open(SP+"/DATA/overlap/test_hosts_clean_of_dev.csv")))
linked={lad[h]["partner_B"] for h,x in lad.items() if x["role"]=="train" and lad[h]["partner_B"] in set(test)}
print(len(dev),len(test),len(clean),len(linked), len(set(clean)&linked))
D={(r["rung"],r["host"]):float(r["D"]) for r in csv.DictReader(open(SP+"/BD1/d_values.csv"))}
row={}
for r in csv.DictReader(open(SP+"/AB1/manifests/ab1_eval.csv")):
    if r["strength"]!="": continue
    if r["fam"]=="ladder" and r["rung"] in ("R4","R3","R0") and r["tool"] in ("opencv","facemorpher",""): row[(r["rung"],r["tool"] if r["rung"]!="R0" else "x",r["host"])]=r["id"]
    if r["fam"]=="splice" and r["rung"] in ("S4","S3"): row[(r["rung"],"opencv",r["host"])]=r["id"]
print(collections.Counter((k[0],k[1]) for k in row))
nets={}
for arm in ("A","B","Sb"):
  for s in range(408,413):
    t=tarfile.open(f"{SP}/AB1/results/AB1_{arm}_s{s}.tar")
    m=[x for x in t.getmembers() if x.name.endswith("scores_eval.npz")][0]
    z=np.load(io.BytesIO(t.extractfile(m).read()),allow_pickle=False)
    nets[(arm,s)]=dict(zip([str(i) for i in z["id"]],z["logit"].astype(float)))
pickle.dump(dict(nets=nets,row=row,D=D,dev=dev,test=test,clean=clean,linked=linked,lad=lad),open(sys.argv[1],"wb"))

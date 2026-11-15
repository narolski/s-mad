import csv,io,tarfile,numpy as np
M=list(csv.DictReader(open("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")))
allid={r["id"] for r in M}; natp=sorted(r["id"] for r in M if r["fam"]=="ms1ffhq" and r["rung"]=="photo" and r["strength"]=="")
P=[i for i in natp if f"{i}_fm61" in allid]
def flips(a,s):
    T=f"AB1_{a}_s{s}"
    with tarfile.open(f"/mnt/t7/smad_next/AB1/results/{T}.tar") as t: z=np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
    L=dict(zip(map(str,z["id"]),z["logit"])); return {i for i in P if L[i]<=0<L[f"{i}_fm61"]}
F={(a,s):flips(a,s) for a in ["A","AS","SbS","B","Sb"] for s in [408,409,410,411,412]}
N=len(P)
def ov(x,y):
    i=len(x&y); e=len(x)*len(y)/N; return f"{i}/{min(len(x),len(y))} (chance {e:.1f})"
for s in [408,409,410,411,412]:
    print(s,"A&SbS",ov(F["A",s],F["SbS",s]),"A&AS",ov(F["A",s],F["AS",s]),"SbS&AS",ov(F["SbS",s],F["AS",s]),"A&B",ov(F["A",s],F["B",s]))
print("SbS 408&409",ov(F["SbS",408],F["SbS",409]),"AS 408&409",ov(F["AS",408],F["AS",409]), "SbS408 & AS409", ov(F["SbS",408],F["AS",409]))

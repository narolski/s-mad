import csv,io,tarfile,numpy as np
from scipy.stats import hypergeom
M=list(csv.DictReader(open("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")))
photo=sorted({r["id"] for r in M if r["fam"]=="ms1ffhq" and r["rung"]=="photo" and r["strength"]==""})
ids_all={r["id"] for r in M if r["fam"]=="ms1ffhq"}
cz=np.load("/mnt/t7/smad_next/PN1/cues/c2p_holdout.npz"); nm=list(cz["names"])
lap=dict(zip(map(str,cz["ids"]),cz["cues"][:,nm.index("lapvar_face")]))
v=np.array([lap[i] for i in photo]); edge=np.quantile(v,.75); top={i for i in photo if lap[i]>=edge}
print(len(photo),edge,len(top))
tot={}
for arm in "A AS SbS".split():
  for z in ("fm61","amsl112"):
    pr=[i for i in photo if f"{i}_{z}" in ids_all]
    agg=[0,0,0,0]
    for s in range(408,413):
      T=f"AB1_{arm}_s{s}"
      with tarfile.open(f"/mnt/t7/smad_next/AB1/results/{T}.tar") as t:
        zz=np.load(io.BytesIO(t.extractfile(f"{T}/scores_eval.npz").read()))
      L=dict(zip(map(str,zz["id"]),zz["logit"].astype(float)))
      up=[i for i in pr if L[i]<=0<L[f"{i}_{z}"]]; dn=[i for i in pr if L[i]>0>=L[f"{i}_{z}"]]
      ut=sum(i in top for i in up); dt=sum(i in top for i in dn); net=len(up)-len(dn)
      elig=[i for i in pr if L[i]<=0]; et=sum(i in top for i in elig)
      p_lo=hypergeom.cdf(ut,len(elig),et,len(up)); p_hi=hypergeom.sf(ut-1,len(elig),et,len(up))
      agg[0]+=ut;agg[1]+=len(up);agg[2]+=et;agg[3]+=len(elig)
      print(arm,z,s,len(pr),sum(i in top for i in pr),"net",net,"up/dn",len(up),len(dn),"ut/dt",ut,dt,
            "share",round((ut-dt)/net,3) if net>0 else None,"elig_top_frac",round(et/len(elig),3),"p_lo %.3g p_hi %.3g"%(p_lo,p_hi))
    print("  POOLED",arm,z,"up top share",round(agg[0]/agg[1],3),"eligible top frac",round(agg[2]/agg[3],3))

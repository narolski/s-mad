import csv,tarfile,io,sys,numpy as np
F=list(csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")))
def load(p,name):
    with tarfile.open(p) as t:
        m=[x for x in t.getmembers() if x.name.endswith("/scores_eval.npz")][0]
        z=np.load(io.BytesIO(t.extractfile(m).read()))
    return dict(zip([str(i) for i in z["id"]],z["logit"].astype(float)))
def auc(p,n):
    p=np.array(p);n=np.array(n); return float(((p[:,None]>n[None,:]).mean()+0.5*(p[:,None]==n[None,:]).mean()))
rungs=["R2w","R2w4","S0","S3","S4","S0_bg","S3_bg","S4_bg","R2w_bg","R4_bg","S0_face","S3_face","S4_face","R2w_face"]
lad=["R0","R2w","R2w4","R3","R4"]
for bb,root,pre in [("DINO","/mnt/t7/smad_next/BB2/results","BB2"),("CLIP","/mnt/t7/smad_next/PN1/results_fs","PN1")]:
  for arm in ["A","B","Sb"]:
    rows=[]
    for s in [403,404,405,406,407]:
      L=load(f"{root}/{pre}_{arm}_s{s}.tar","")
      g=lambda fam,role,r:[L[x["id"]] for x in F if x["fam"]==fam and x["role"]==role and x["rung"]==r and x["id"] in L]
      fl={r:np.mean(np.array(g("splice","dev",r))>0) for r in rungs}
      fl.update({"L"+r:np.mean(np.array(g("ladder","dev",r))>0) for r in lad})
      fl["auc_S3bg_S0bg"]=auc(g("splice","dev","S3_bg"),g("splice","dev","S0_bg"))
      fl["auc_S4bg_S3bg"]=auc(g("splice","dev","S4_bg"),g("splice","dev","S3_bg"))
      fl["auc_S3f_S0f"]=auc(g("splice","dev","S3_face"),g("splice","dev","S0_face"))
      fl["auc_S3_S0_T"]=auc(g("splice","test","S3"),g("splice","test","S0"))
      fl["auc_S3bg_S0bg_T"]=auc(g("splice","test","S3_bg"),g("splice","test","S0_bg"))
      fl["auc_S3f_S0f_T"]=auc(g("splice","test","S3_face"),g("splice","test","S0_face"))
      fl["auc_LR3_R2w"]=auc(g("ladder","dev","R3"),g("ladder","dev","R2w"))
      fl["auc_LR4_R3"]=auc(g("ladder","dev","R4"),g("ladder","dev","R3"))
      rows.append(fl)
    keys=rows[0].keys()
    print(bb,arm)
    for k in keys:
      v=[r[k] for r in rows]; print(f"  {k:16s} "+" ".join(f"{x:.2f}" for x in v))

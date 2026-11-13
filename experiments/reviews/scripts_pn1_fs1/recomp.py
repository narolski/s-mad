import csv, io, tarfile, pathlib, json, numpy as np
from sklearn.metrics import roc_auc_score as ra
from scipy import stats
R=pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
man=list(csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")))
sel=lambda **k:[r for r in man if all(r[a]==b for a,b in k.items())]
lm=[r["id"] for r in sel(fam="ffhq_lcomb",rung="landmark_combined_orig")]
lg=[r["id"] for r in sel(fam="ffhq_lcomb",rung="landmark_combined_resmatch")]
nat={r["host"]:r["id"] for r in sel(fam="ffhq",rung="ffhq_bona_orig")}
rm={r["host"]:r["id"] for r in sel(fam="ffhq",rung="landmark_complete_resmatch")}
cm=[r["id"] for r in sel(fam="ffhq",rung="landmark_complete_orig")]
keys=sorted(set(nat)&set(rm)); print("n keys",len(keys),"lcomb",len(lm),len(lg))
def ids(fam,role,rung,strength=""): return [r["id"] for r in sel(fam=fam,role=role,rung=rung,strength=strength)]
z=np.load("/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz"); names=[str(n) for n in z["names"]]
cid={str(i):c for i,c in zip(z["ids"],z["cues"])}
CM=np.array([cid[i] for i in lm]);CG=np.array([cid[i] for i in lg])
y=np.r_[np.ones(len(lm)),np.zeros(len(lg))]
fa=[ra(y,np.r_[CM[:,j],CG[:,j]]) for j in range(27)]; fd=[max(a,1-a) for a in fa]
j=int(np.argmax(fd)); print("floor",names[j],round(fd[j],5)); 
top=sorted(zip(fd,names))[::-1][:4]; print("top4",[(n,round(a,3)) for a,n in top])
def load(n):
    with tarfile.open(R/f"{n}.tar") as t: q=np.load(io.BytesIO(t.extractfile(f"{n}/scores_eval.npz").read()))
    return dict(zip([str(i) for i in q["id"]],q["logit"].astype(float)))
def auc(S,p,n): return ra(np.r_[np.ones(len(p)),np.zeros(len(n))],np.r_[[S[i] for i in p],[S[i] for i in n]])
out={}
runs=[(a,s) for s in (403,404,405,406,407) for a in ("A","B","Sb")]+[("Arep",401)]
for a,s in runs:
    S=load(f"PN1_{a}_s{s}")
    d=np.array([S[rm[k]]-S[nat[k]] for k in keys])
    natv=np.array([S[nat[k]] for k in keys]); rmv=np.array([S[rm[k]] for k in keys])
    o=dict(lcomb=auc(S,lm,lg), share=float(np.mean(d>0)), mean_shift=float(d.mean()), med_shift=float(np.median(d)),
      sd_nat=float(natv.std()), shift_sd=float(d.mean()/natv.std()),
      flag_nat=float(np.mean(natv>0)), flag_rm=float(np.mean(rmv>0)),
      flag_lcg=float(np.mean(np.array([S[i] for i in lg])>0)), miss_lcm=float(np.mean(np.array([S[i] for i in lm])<=0)),
      miss_lcomplete=float(np.mean(np.array([S[i] for i in cm])<=0)),
      fo_test=auc(S,ids("splice","test","S4_bg"),ids("splice","test","S0_bg")),
      fb_test=auc(S,ids("splice","test","R4_face"),ids("splice","test","R2w_face")),
      fo_dev=auc(S,ids("splice","dev","S4_bg"),ids("splice","dev","S0_bg")),
      DR0=float(np.mean(np.array([S[i] for i in ids("ladder","dev","R0")])>0)),
      DR0_61=float(np.mean(np.array([S[i] for i in ids("ladder","dev","R0","61")])>0)),
      DR0_112=float(np.mean(np.array([S[i] for i in ids("ladder","dev","R0","112")])>0)),
      Vphoto=float(np.mean(np.array([S[i] for i in ids("af0","dev","photo")])>0)),
      miss_DR4=float(np.mean(np.array([S[i] for i in ids("ladder","dev","R4","","")+ids("ladder","dev","R4")])<=0)) if False else float(np.mean(np.array([S[i] for i in [r["id"] for r in man if r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R4" and r["strength"]==""]])<=0)),
      miss_DS4=float(np.mean(np.array([S[i] for i in ids("splice","dev","S4")])<=0)),
      flag_DS0=float(np.mean(np.array([S[i] for i in ids("splice","dev","S0")])>0)),
      flag_DS3=float(np.mean(np.array([S[i] for i in ids("splice","dev","S3")])>0)),
      )
    out[f"{a}_{s}"]=o
json.dump(dict(out=out,floor=fd[j]),open("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/fs/recomp.json","w"),indent=1)
keysm=list(out["A_403"].keys())
for k in keysm:
    print(k.ljust(14)," ".join(f"{a}:"+",".join(f"{out[f'{a}_{s}'][k]:.3f}" for s in (403,404,405,406,407)) for a in ("A","B","Sb")), "rep401 %.3f"%out["Arep_401"][k])

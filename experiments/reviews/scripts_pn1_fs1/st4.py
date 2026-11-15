import csv, io, tarfile, pathlib, numpy as np
R=pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
man=list(csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")))
pool=[r["id"] for r in man if (r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R0" and r["strength"]=="") or (r["fam"]=="af0" and r["rung"]=="photo" and r["strength"]=="")]
lm=[r["id"] for r in man if r["rung"]=="landmark_combined_orig"]; nat=[r["id"] for r in man if r["rung"]=="ffhq_bona_orig"]; rm=[r["id"] for r in man if r["rung"]=="landmark_complete_resmatch"]
cm=[r["id"] for r in man if r["rung"]=="landmark_complete_orig"]
print("tau pool n",len(pool))
def load(n):
    with tarfile.open(R/f"{n}.tar") as t: q=np.load(io.BytesIO(t.extractfile(f"{n}/scores_eval.npz").read()))
    return dict(zip([str(i) for i in q["id"]],q["logit"].astype(float)))
for a in ("A","B","Sb"):
    row=[]
    for s in (403,404,405,406,407):
        S=load(f"PN1_{a}_s{s}"); t=np.quantile([S[i] for i in pool],0.95)
        f=lambda L:np.mean(np.array([S[i] for i in L])>t)
        row.append(f"tau {t:+.2f}: lcm miss {1-f(lm):.2f} lcomplete miss {1-f(cm):.2f} nat flag {f(nat):.2f} rm flag {f(rm):.2f}")
    print(a); [print("  ",x) for x in row]

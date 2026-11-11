import csv, collections, numpy as np, pathlib
EV="/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv"
rows=list(csv.DictReader(open(EV)))
print(len(rows), rows[0].keys())
c=collections.Counter((r["set"],r["family"],r["label"],r["variant"]) for r in rows)
for k,v in sorted(c.items()): print(k,v)
import os
for p in ["/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL"]:
    for d in sorted(os.listdir(p)):
        if any(t in d.lower() for t in ("fst","valx","a12sp")): continue
        fs=[f for f in sorted(os.listdir(os.path.join(p,d))) if not any(t in f.lower() for t in ("fst","valx","a12sp"))]
        print(d, fs)
z=np.load("/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz", allow_pickle=False)
print(z.files, z["id"].shape)
z=np.load("/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", allow_pickle=False)
print(z.files, z["id"].shape)

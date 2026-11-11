import csv, collections, numpy as np, pathlib
MC = pathlib.Path("/home/narolski/mambamorph-code")
rows = list(csv.DictReader(open(MC/"smadcvpr_data/manifests/eval.csv")))
c = collections.Counter((r["set"], r["family"], r["variant"], r["label"]) for r in rows)
for k, v in sorted(c.items()):
    if k[0] != "mad22": print(k, v)
# devbona composition
dv = [r for r in rows if r["set"] == "devbona"]
print(len(dv))
cc = collections.Counter(pathlib.PurePath(r["path"]).parts[2] if len(pathlib.PurePath(r["path"]).parts)>3 else "?" for r in dv)
print(cc)
print(dv[0]); print(dv[-1])
import statistics
for key in ("native_w","native_h","file_bytes","ied"):
    x = np.array([float(r[key]) for r in dv]); print(key, np.percentile(x,[0,5,25,50,75,95,100]))
fb = [r for r in rows if r["set"]=="frllm" and r["family"]=="frll_bona" and r["variant"]=="orig"]
for key in ("native_w","native_h","file_bytes","ied"):
    x = np.array([float(r[key]) for r in fb]); print("frll", key, np.percentile(x,[0,5,25,50,75,95,100]))
print(fb[0])
z = np.load(MC/"smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz", allow_pickle=False)
print(z.files, {k: z[k].shape for k in z.files if z[k].ndim})
z = np.load(MC/"experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", allow_pickle=False)
print(z.files, {k: z[k].shape for k in z.files if z[k].ndim})

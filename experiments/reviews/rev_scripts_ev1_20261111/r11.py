import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import spearmanr
R = rows_eval(); ids = [r["id"] for r in R]
z = np.load("/mnt/t7/smad_next/EV1/feat.npz", allow_pickle=False)
suf = {str(k)[str(k).find("eval/"):]: float(v) for k, v in zip(z["al_path"], z["al_zero"]) if "eval/" in str(k)}
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
nets = []
for ln in open(MC/"experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"):
    if ln.startswith("#"): continue
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 7 and f[3] == "primary" and f[4].split()[0] in ("M3","M3L"): nets.append((f[4].split()[0], int(f[6]), pathlib.PurePath(f[0]).name))
dets = {"ViT-L/14 rel": rel("madation_vitl14", ids), "ViT-B/16 rel": rel("madation_vitb16", ids), "FE ViT-L/14 rel": rel("madation_fe_vitl14", ids), "SelfMAD own": load(OWN, ids, "score")}
for meth, seed, run_ in sorted(nets):
    if seed <= 2: dets[f"{meth} s{seed}"] = load(A12BR/run_/"scores_eval_last.npz", ids, "score")
print("Within-family Spearman(score, zero-border fraction of our aligned frame) among morphs")
print(f"{'':16s}" + " ".join(f"{f[:9]:>9s}" for f in FAMS))
print(f"{'border IQR':16s}" + " ".join(f"{np.percentile([suf[R[i]['path']] for i in M[f]],25):.2f}-{np.percentile([suf[R[i]['path']] for i in M[f]],75):.2f}" for f in FAMS))
for nm, s in dets.items():
    out = []
    for f in FAMS:
        b = np.array([suf[R[i]["path"]] for i in M[f]]); x = s[M[f]]
        out.append(spearmanr(x, b).statistic if np.isfinite(x).all() and b.std() > 0 else np.nan)
    print(f"{nm:16s}" + " ".join(f"{v:+9.2f}" for v in out))

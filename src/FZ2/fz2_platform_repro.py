"""FZ2 / DG1: production set B vs add-on re-renders (REC, SAME, X, MIR at 20 steps), matched by list key and (host,
partner): byte identity of the PNGs and agreement of head s401, P_XS (clip_mad) and face-box Laplacian. Review F1.
Writes experiments/DG1_diffusion-generation-athena/platform_reproducibility_fz2.json."""
import csv, hashlib, json, collections
import numpy as np
from scipy.stats import spearmanr
B = "/mnt/t7/smad_next/FZ2"
def load(f):
    out = {}
    for r in csv.DictReader(open(f)):
        if r["key"] in ("REC20", "SAME20", "X20", "MIR20"):
            out[(r["key"], r["host"], r["partner"])] = r
    return out
P, A = load(f"{B}/read_prod_items.csv"), load(f"{B}/read_addon_items.csv")
plat = {r["id"]: r["platform"] for r in csv.DictReader(open(f"{B}/read_addon_items.csv"))}
keys = sorted(set(P) & set(A))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
same = collections.Counter(); tot = collections.Counter()
for k in keys:
    pa = "/mnt/t7/smad_next/DG1/gen/" + P[k]["list"] + "/" + P[k]["id"]
    pb = "/mnt/t7/smad_next/DG1/gen/" + A[k]["list"] + "/" + A[k]["id"]
    pl = plat[A[k]["id"]]; tot[pl] += 1; same[pl] += int(sha(pa) == sha(pb))
res = {"matched": len(keys), "per_rung": dict(collections.Counter(k[0] for k in keys)),
       "byte_identical": {pl: [same[pl], tot[pl]] for pl in tot}}
for col in ("smdd_s401", "clip_mad|P_XS", "lapvar_box"):
    a = np.array([float(P[k][col]) for k in keys]); b = np.array([float(A[k][col]) for k in keys])
    res[col] = {"spearman": float(spearmanr(a, b)[0]), "pearson": float(np.corrcoef(a, b)[0, 1]), "max_abs_diff": float(np.abs(a - b).max())}
print(json.dumps(res, indent=1))
json.dump(res, open("/home/narolski/smad-next/experiments/DG1_diffusion-generation-athena/platform_reproducibility_fz2.json", "w"), indent=1)

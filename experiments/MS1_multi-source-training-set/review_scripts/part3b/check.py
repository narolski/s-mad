import sys, json, csv, re
sys.path.insert(0, "/home/narolski/smad-next/src/MS1")
import numpy as np
from scipy.stats import mannwhitneyu
import ms1_part3 as P3
d = json.load(open("/home/narolski/smad-next/experiments/MS1_multi-source-training-set/ms1_part3b.json"))
M = list(csv.DictReader(open(P3.EVAL)))
maxdiff = 0; signs = {}
for arm in P3.ARMS:
    man = {r["path"]: r for r in csv.DictReader(open(P3.MAN[arm]))}
    for s in P3.SEEDS:
        tar = P3.RES / f"MS1_{arm}_s{s}.tar"
        z = P3.load_npz(tar, "scores_eval.npz"); E = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
        z = P3.load_npz(tar, "scores_train.npz")
        paths = [str(x) for x in z["path"]]
        keys = [p[p.index("train/"):] if "train/" in p else p for p in paths]
        nmatch = sum(k in man for k in keys)
        dup = len(keys) - len(set(keys))
        A = []
        for kind, sel in P3.HELD.items():
            t = [lg for k, lg in zip(keys, z["logit"].astype(float)) if k in man and man[k]["kind"] == kind and man[k]["db"] in ("frgc", "feret")]
            h = [E[r["id"]] for r in M if sel(r) and r["id"] in E]
            u = mannwhitneyu(t, h).statistic / (len(t) * len(h))
            au = u if kind in P3.ATTACK else 1 - u
            ref = d["rank_auc_memorisation"]["per_kind"][f"{arm}_s{s}"][kind]["rank_auc"]
            maxdiff = max(maxdiff, abs(au - ref)); A.append(au)
            signs.setdefault((kind, s), {})[arm] = au
            tt = len(set(np.round(t, 6))) < len(t)
        print(arm, s, "match", nmatch, "of", len(keys), "dupkeys", dup, "A", round(np.mean(A), 5), "ref", round(d["rank_auc_memorisation"]["A"][f"{arm}_s{s}"], 5))
print("max per-kind diff", maxdiff)
for kind in P3.HELD:
    print(kind, "SbM3<Sb seeds:", sum(signs[(kind, s)]["SbM3"] < signs[(kind, s)]["Sb"] for s in P3.SEEDS),
          "Sb", [round(signs[(kind, s)]["Sb"], 3) for s in P3.SEEDS], "SbM3", [round(signs[(kind, s)]["SbM3"], 3) for s in P3.SEEDS])
# sex coding check
norm = P3.norming()
pool = list(csv.DictReader(open(P3.CFD_POOL)))
mo = {}
for r in pool:
    mm = re.search(r"CFD-([ABLW][FM]-\d+)-\d+-N\.jpg$", r["raw"])
    if mm and r["aligned"] == "1" and "/CFD/" in r["raw"]:
        mo[r["id"]] = mm.group(1)
from collections import Counter
print("ids", len(mo), "unique models", len(set(mo.values())), Counter(Counter(mo.values()).values()))
print("GenderSelf vs code", Counter((m[1], norm[m]["GenderSelf"]) for m in set(mo.values()) if m in norm))
print("Feminine nonfloat", sum(1 for m in set(mo.values()) if m in norm and not isinstance(norm[m]["Feminine"], float)), "not in norm", sum(1 for m in set(mo.values()) if m not in norm))

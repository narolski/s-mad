"""CB1 amendment 7 (A), corrected after the review of 13 Nov (F3, F4): from border/border_mfn_rows.csv (no image read):
person bootstrap dropping resamples without weight in either class; border-matched subsets at border <= 0.005 and at
exactly 0; AUC by border quartile inside each morph family (all photos as negatives).
  python3 -I border_mfn_reread.py ROWS.csv OUT.json"""
import csv, json, sys
import numpy as np
from scipy.stats import rankdata
rec = list(csv.DictReader(open(sys.argv[1])))
for r in rec:
    r["border"] = float(r["border"]); r["logit"] = float(r["logit"]); r["label"] = int(r["label"])
per = sorted({x["pa"] for x in rec} | {x["pb"] for x in rec}); pi = {p: i for i, p in enumerate(per)}
C = np.random.default_rng(20261111).multinomial(len(per), [1 / len(per)] * len(per), size=2000).astype(float)
def auc_ci(pos, neg):
    if not pos or not neg:
        return None
    ps = np.array([x["logit"] for x in pos]); ns = np.array([x["logit"] for x in neg])
    r = rankdata(np.r_[ps, ns]); n1, n0 = len(ps), len(ns)
    a = (r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    gt = (ps[:, None] > ns[None, :]) + 0.5 * (ps[:, None] == ns[None, :])
    pa = np.array([pi[x["pa"]] for x in pos]); pb = np.array([pi[x["pb"]] for x in pos]); na = np.array([pi[x["pa"]] for x in neg])
    reps, dropped = [], 0
    for c in C:
        wp = c[pa] * c[pb]; wn = c[na]
        if wp.sum() == 0 or wn.sum() == 0:
            dropped += 1; continue
        W = wp[:, None] * wn[None, :]
        reps.append((gt * W).sum() / W.sum())
    return dict(auc=round(float(a), 3), ci95=[round(float(np.percentile(reps, 2.5)), 3), round(float(np.percentile(reps, 97.5)), 3)],
                n_pos=n1, n_neg=n0, persons_pos=len({x["pa"] for x in pos} | {x["pb"] for x in pos}), resamples_dropped=dropped)
gen = [x for x in rec if x["family"] == "frll_bona" and x["variant"] == "orig"]
out = {}
for fam in ("amsl", "facemorpher", "opencv", "stylegan", "webmorph"):
    m = [x for x in rec if x["family"] == fam and x["label"] == 1]
    q = np.quantile([x["border"] for x in m], [0.25, 0.5, 0.75])
    bins = [[x for x in m if x["border"] <= q[0]], [x for x in m if q[0] < x["border"] <= q[1]],
            [x for x in m if q[1] < x["border"] <= q[2]], [x for x in m if x["border"] > q[2]]]
    out[fam] = dict(border_quartile_edges=[round(float(v), 4) for v in q],
                    auc_by_border_quartile=[auc_ci(b, gen)["auc"] if b else None for b in bins],
                    border_le_0p005=auc_ci([x for x in m if x["border"] <= 0.005], gen),
                    border_exactly_0=auc_ci([x for x in m if x["border"] == 0.0], gen),
                    all=auc_ci(m, gen))
json.dump(out, open(sys.argv[2], "w"), indent=1)
for k, v in out.items():
    print(k, "quartiles", v["auc_by_border_quartile"], "| <=0.005", v["border_le_0p005"], "| ==0", v["border_exactly_0"])

"""AR1 gate G-c (readability, P2): probe on each detector's frozen features (feat_<tag>.npz from score.py; no score
file is opened). L2 logistic regression (StandardScaler + LogisticRegression C = 1), 5-fold GroupKFold by host person,
pooled out-of-fold AUC with the person bootstrap; main task R4 vs R3; negative control NC vs R3 (expected 0.5).
Writes experiments/AR1/gate_c.json.
  python3 -I gate_c.py --tags rel_madation_vitb16,... [--pools frgcferet,frll]
"""
import argparse
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import stats  # noqa: E402


def oof(X, y, g, seed=0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    p = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, g):
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=3000))
        m.fit(X[tr], y[tr])
        p[te] = m.decision_function(X[te])
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", required=True)
    ap.add_argument("--pools", default="frgcferet,frll")
    ap.add_argument("--dir", default=str(K.OUT / "scores"))
    a = ap.parse_args()
    man = {r["id"]: r for r in csv.DictReader(open(K.OUT / "manifest.csv"))}
    out = json.load(open(K.RES / "gate_c.json")) if (K.RES / "gate_c.json").exists() else {}
    for tag in a.tags.split(","):
        z = np.load(pathlib.Path(a.dir) / f"feat_{tag}.npz")
        F = dict(zip(z["id"].tolist(), z["feat"]))
        out[tag] = {}
        for pool in a.pools.split(","):
            pers = sorted({r["p1"] for r in man.values() if r["pool"] == pool} |
                          {r["p2"] for r in man.values() if r["pool"] == pool})
            D = stats.Draw(pers, 2000, [20261111, 3])
            for tool in ("opencv", "facemorpher"):
                res = {}
                tasks = [("morph_vs_twin", "R4", "R3"), ("negctrl_NC_vs_twin", "NC", "R3"),
                         ("morph_vs_mirror_twin", "R4", "R3m")]
                if pool == "frll":
                    tasks.append(("nn_morph_vs_mirror_twin (clean FRLL)", "R4nn", "R3m"))
                for name, pos, neg in tasks:
                    if pos == "R4nn":
                        rows = [r for r in man.values() if ((r["pool"] == "frll_bridge" and r["tool"] == tool)
                                or (r["pool"] == pool and r["tool"] == tool and r["rung"] == neg)) and r["id"] in F]
                        for r in rows:
                            if r["pool"] == "frll_bridge":
                                r = r.update(rung="R4nn") or r
                    else:
                        rows = [r for r in man.values() if r["pool"] == pool and r["tool"] == tool
                                and r["rung"] in (pos, neg) and r["id"] in F]
                    y = np.array([r["rung"] == pos for r in rows], int)
                    if y.sum() == 0 or (1 - y).sum() == 0:
                        res[name] = dict(auc=None, ci95=[None, None], note="no features for one class (not scored)")
                        continue
                    X = np.stack([F[r["id"]] for r in rows])
                    g = np.array([r["p1"] for r in rows])
                    s = oof(X, y, g)
                    P = [(r["p1"], r["p2"]) for r in rows if r["rung"] == pos]
                    N = [(r["p1"],) for r in rows if r["rung"] == neg]
                    au, c = stats.wauc_ci(D, s[y == 1], P, s[y == 0], N)
                    res[name] = dict(auc=au, ci95=c, n_pos=int(y.sum()), n_neg=int((1 - y).sum()), dim=int(X.shape[1]))
                res["G_c_readable"] = bool(res["morph_vs_twin"]["auc"] >= 0.65)
                res["G_c_readable_mirror_twin"] = bool(res["morph_vs_mirror_twin"]["auc"] >= 0.65)
                if pool == "frll":
                    res["note"] = "R3 / R4 of FRLL use a smiling file: confounded by capture detail and expression"
                out[tag][f"{pool}/{tool}"] = res
                print(tag, pool, tool, json.dumps(res), flush=True)
    json.dump(out, open(K.RES / "gate_c.json", "w"), indent=1)


if __name__ == "__main__":
    main()

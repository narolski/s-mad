"""PN1 amendment 15: 27-statistic baseline trained on the ladder TRAINING hosts (like the networks), scored on FFHQ
landmark_combined (development). Zero GPU. python3 -I baseline27.py -> experiments/PN1_.../tier1_a14/baseline27.json"""
import csv
import hashlib
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import splice as SP  # noqa: E402

FLOOR = K.PN1 / "cues" / "a14_lcomb.npz"
FLOOR_SHA = K.RES / "tier1_a14" / "a14_lcomb_floor.sha256"
MAN = K.PN1 / "a14_tree" / "pn14" / "data" / "manifests" / "pn1_a14.csv"


def fauc(p, n):
    from scipy.stats import rankdata
    r = rankdata(np.r_[p, n])[: len(p)]
    return (r.sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n))


def cues(f):
    z = np.load(f)
    return {str(i): c for i, c in zip(z["ids"], z["cues"])}, [str(n) for n in z["names"]]


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    assert hashlib.sha256(FLOOR.read_bytes()).hexdigest() == FLOOR_SHA.read_text().split()[0]
    lad, nl = cues(K.AF0 / "cues" / "ar1.npz")
    spl, ns = cues(K.PN1 / "cues" / "splice_nat.npz")
    lc, nc = cues(FLOOR)
    assert nl == ns == nc
    cat = [r for r in K.catalog() if r["fam"] == "ladder" and r["role"] == "train" and r["strength"] == ""]
    pos_b = [r["id"] for r in cat if r["rung"] == "R4" and r["tool"] == "opencv"]
    neg_b = [r["id"] for r in cat if r["rung"] in ("R0", "R2w") and r["tool"] in ("opencv", "none")]
    sp = SP.splice_rows()
    pos_s = [r["id"] for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and r["role"] == "train" and r["train_morph"] == "1"]
    neg_s = [r["id"] for r in sp if r["rung"] in ("S0", "S3") and r["tool"] == "opencv" and r["role"] == "train"]
    man = list(csv.DictReader(open(MAN)))
    lm = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lg = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    M = np.array([lc[i] for i in lm]); G = np.array([lc[i] for i in lg])
    rng = np.random.default_rng(20261120)
    draws = [(rng.integers(0, len(M), len(M)), rng.integers(0, len(G), len(G))) for _ in range(2000)]
    out = {"n_lcomb": (len(lm), len(lg))}
    for name, P, N in (("b_lad", [lad[i] for i in pos_b if i in lad], [lad[i] for i in neg_b if i in lad]),
                       ("s_lad", [lad[i] for i in pos_b if i in lad] + [spl[i] for i in pos_s if i in spl],
                        [lad[i] for i in neg_b if i in lad] + [spl[i] for i in neg_s if i in spl])):
        X = np.r_[np.array(P), np.array(N)]; y = np.r_[np.ones(len(P)), np.zeros(len(N))]
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced")).fit(X, y)
        sm, sg = mdl.decision_function(M), mdl.decision_function(G)
        bs = [fauc(sm[a], sg[b]) for a, b in draws]
        out[name] = dict(n_train_pos=len(P), n_train_neg=len(N), auc=float(fauc(sm, sg)),
                         ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                         train_auc=float(fauc(mdl.decision_function(np.array(P)), mdl.decision_function(np.array(N)))))
    sb = {401: 0.887, 402: 0.909}
    bb = {401: 0.754, 402: 0.716}
    def rule(net, base):
        if all(net[s] - base >= 0.05 for s in net):
            return "exceeds"
        if any(base >= net[s] for s in net):
            return "not beyond"
        return "inconclusive, no claim"
    out["Sb_vs_s_lad"] = rule(sb, out["s_lad"]["auc"])
    out["B_vs_b_lad"] = rule(bb, out["b_lad"]["auc"])
    out["note"] = "network AUCs from tier1_a14/a14.json (Sb 0.887/0.909, B 0.754/0.716; rounded to 3 decimals)"
    K.dump(out, K.RES / "tier1_a14" / "baseline27.json")
    print(out)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

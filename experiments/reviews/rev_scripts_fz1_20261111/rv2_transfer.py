"""Reviewer check rv2 (read-only, post hoc, point AUCs, fixed C=1, no inner CV): does a probe trained on one A43
contrast rank the arms of another? Person folds seed 401 (FZ1's), train rows with no person in the test fold,
test rows with host in the test fold. Also the P3 head's expression check on reconstructions."""
import sys, warnings, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
import fz1_common as K
from fz1_probe import person_folds, load
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
rows = K.a43_rows(); g = K.a43_groups(rows)
P = {i: K.pers_a43(rows[i]) for a in ["B","B20","C","C20","D","D20","E"] for i in g[a]}
fold = person_folds(sorted({p for t in P.values() for p in t}), 401)
def run(bb, tr_pos, tr_neg, tests):
    idx, X = load(bb, "a43")
    xi = lambda i: idx[rows[i]["id"]]
    out = {t: {} for t in tests}
    for k in range(5):
        tri = [i for i in g[tr_pos] + g[tr_neg] if all(fold[p] != k for p in P[i])]
        y = np.array([1 if i in set(g[tr_pos]) else 0 for i in tri])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X[[xi(i) for i in tri]], y)
        for t in tests:
            for arm in t:
                for i in g[arm]:
                    if fold[P[i][0]] == k:
                        out[t][i] = m.decision_function(X[[xi(i)]])[0]
    res = []
    for (a, b) in tests:
        pa = np.array([out[(a, b)][i] for i in g[a]]); pb = np.array([out[(a, b)][i] for i in g[b]])
        res.append(f"{a} vs {b} {K.auc(pa, pb):.3f}")
    print(f"{bb:9s} train {tr_pos} vs {tr_neg}: " + "; ".join(res), flush=True)
T = [("B20","D20"), ("C20","D20"), ("B20","C20"), ("B","D"), ("C","D"), ("B","C"), ("E","D20"), ("E","D")]
for bb in ["clip_mad", "dinov2"]:
    for tp, tn in [("C20","D20"), ("B20","D20"), ("B","D"), ("C","D")]:
        run(bb, tp, tn, T)
H = np.load(K.BIG / "heads/scores_a43.npz"); hid = {k: i for i, k in enumerate(H["id"].tolist())}
s = H["s401_a43"]
f = lambda ii: np.array([s[hid[rows[i]["id"]]] for i in ii])
for d in ["D20", "D"]:
    n3 = [i for i in g[d] if rows[i]["src_a"][4:6] == "03"]; n8 = [i for i in g[d] if rows[i]["src_a"][4:6] == "08"]
    c = "C20" if d == "D20" else "C"
    print(f"P3 head s401: {d} neutral vs {d} smiling {K.auc(f(n3), f(n8)):.3f}; {c} vs {d} neutral {K.auc(f(g[c]), f(n3)):.3f}; {c} vs {d} smiling {K.auc(f(g[c]), f(n8)):.3f}")

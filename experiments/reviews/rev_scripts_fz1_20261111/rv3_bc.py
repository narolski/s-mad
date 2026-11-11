"""Reviewer check rv3 (read-only, post hoc, point estimates): what separates B20 from C20?
(a) PNG-bytes floor for B20 vs C20 and B vs C; (b) does the clip_mad B20-vs-C20 probe direction carry expression
(test it on D20 neutral vs D20 smiling)? (c) P3 head s401 within B20 vs identity dilution (glint cosine of the stored
morph to its two sources, A43 manifest), and B20 vs C20 inside matched bands of that cosine."""
import sys, warnings, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
import fz1_common as K
from fz1_probe import person_folds, load
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
rows = K.a43_rows(); g = K.a43_groups(rows)
fb = lambda a: np.array([float(rows[i]["file_bytes"]) for i in g[a]])
for a, b in [("B20","C20"), ("B","C"), ("C20","D20"), ("C","D")]:
    x = K.auc(fb(a), fb(b)); print(f"PNG bytes {a} vs {b}: {x:.3f} (folded {max(x,1-x):.3f})")
P = {i: K.pers_a43(rows[i]) for a in ["B20","C20","D20","E"] for i in g[a]}
fold = person_folds(sorted({p for t in P.values() for p in t}), 401)
idx, X = load("clip_mad", "a43"); xi = lambda i: idx[rows[i]["id"]]
sc = {}
for k in range(5):
    tri = [i for i in g["B20"] + g["C20"] if all(fold[p] != k for p in P[i])]
    y = np.array([1 if rows[i]["arm"] == "B20" else 0 for i in tri])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(X[[xi(i) for i in tri]], y)
    for a in ["D20", "E", "B20", "C20"]:
        for i in g[a]:
            if fold[P[i][0]] == k: sc[i] = m.decision_function(X[[xi(i)]])[0]
s = lambda ii: np.array([sc[i] for i in ii])
for a in ["D20", "E"]:
    n3 = [i for i in g[a] if rows[i]["src_a"][4:6] == "03"]; n8 = [i for i in g[a] if rows[i]["src_a"][4:6] == "08"]
    print(f"B20-vs-C20 probe (clip_mad, C=1, person folds 401): {a} smiling vs {a} neutral AUC {K.auc(s(n8), s(n3)):.3f}")
print(f"  same probe: B20 vs C20 {K.auc(s(g['B20']), s(g['C20'])):.3f}; B20 neutral-pairs vs C20 {K.auc(s([i for i in g['B20'] if rows[i]['expr']=='03']), s(g['C20'])):.3f}; B20 smiling-pairs vs C20 {K.auc(s([i for i in g['B20'] if rows[i]['expr']=='08']), s(g['C20'])):.3f}")
H = np.load(K.BIG / "heads/scores_a43.npz"); hid = {k: i for i, k in enumerate(H["id"].tolist())}
h = H["s401_a43"]
def mc(i):
    r = rows[i]; v = [float(r[c]) for c in ("cos_stored_raw_a", "cos_stored_raw_b") if r[c] != ""]
    return min(v) if v else np.nan
for a in ["B20", "B", "C20", "C"]:
    cc = np.array([mc(i) for i in g[a]]); hh = np.array([h[hid[rows[i]["id"]]] for i in g[a]])
    ok = ~np.isnan(cc)
    print(f"{a}: n={ok.sum()} median min-cos to sources {np.median(cc[ok]):.3f}; rho(head, min-cos) = {spearmanr(hh[ok], cc[ok])[0]:+.3f}")
for big, small in [("B20", "C20"), ("B", "C")]:
    cb = np.array([mc(i) for i in g[big]]); cs = np.array([mc(i) for i in g[small]])
    hb = np.array([h[hid[rows[i]["id"]]] for i in g[big]]); hs = np.array([h[hid[rows[i]["id"]]] for i in g[small]])
    lo, hi = max(np.nanmin(cb), np.nanmin(cs)), min(np.nanmax(cb), np.nanmax(cs))
    mb = (cb >= lo) & (cb <= hi); ms = (cs >= lo) & (cs <= hi)
    print(f"{big} vs {small} min-cos AUC (lower = morph) {K.auc(-cb[~np.isnan(cb)], -cs[~np.isnan(cs)]):.3f}; head within common cos range [{lo:.3f},{hi:.3f}] nB={mb.sum()} nC={ms.sum()} AUC {K.auc(hb[mb], hs[ms]):.3f}")

"""SM1 A18 incremental read over a fixed trace floor (shared by hn2_read.py and a18_probe.py).

Rows: the test-shard X20 (attack) and SAME20 (genuine) of sm1_hn2_test.csv (shards 6-7). Floor F = logistic regression
of X20 vs SAME20 on (θ, face-box Laplacian, log PNG bytes, asymmetry, d); image-statistics floor F_img = the same
without θ. Cross-fit on test-shard folds: the 55 test partner cycles are split into 5 folds (numpy default_rng(20261111)
permutation of the sorted cycle ids, round-robin); for each fold, models are fit on the other 4 folds and predict the
held-out fold. ΔAUC = out-of-fold AUC of (F inputs + score) minus out-of-fold AUC of F. Bootstrap over partner cycles
(B = 10,000, seed 20261111; weights = cycle counts) of the out-of-fold predictions (models are not refit per draw).
"""
import csv
import pathlib

import numpy as np

import sm1_common as K
import sm1_stats as S

B = 10000


def test_rows(drop_flagged=False):
    test = list(csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv")))
    it = {f"hn2:{r['key']}:{r['host']}": r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv"))
          if r["key"] in ("X20", "SAME20")}
    th = {}
    for k in (6, 7):
        f = K.OUT.parent / "DG1/gen" / f"addon_s{k}" / f"out_addon_s{k}" / f"addon_s{k}" / "gen_rows.csv"
        for r in csv.DictReader(open(f)):
            th[(f"addon_s{k}", r["pool"], r["name"])] = float(r["theta_xT"])
    rows = []
    for r in test:
        if r["family"] not in ("X20", "SAME20"):
            continue
        a = it[r["id"]]
        if drop_flagged and a["flagged"] == "1":
            continue
        parts = a["id"].split("/")
        rows.append(dict(id=r["id"], y=1 if r["family"] == "X20" else 0, cycle=a["cycle"], item_id=a["id"],
                         f=[th[(a["list"], parts[-2], parts[-1])], np.log(float(a["lapvar_box"])),
                            np.log(float(a["png_bytes"])), float(a["asym_box"]), float(a["d"])]))
    return rows


def _lr(Xtr, ytr, Xte):
    from sklearn.linear_model import LogisticRegression
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12
    m = LogisticRegression(max_iter=5000).fit((Xtr - mu) / sd, ytr)
    return m.decision_function((Xte - mu) / sd)


def incremental(rows, score):
    """score: dict id -> network / probe score. Returns dict with AUCs, ΔAUC (vs F and vs F_img), bootstrap draws."""
    cyc = sorted({r["cycle"] for r in rows}, key=lambda c: int(c))
    perm = np.random.default_rng(K.SEED).permutation(len(cyc))
    fold = {cyc[j]: i % 5 for i, j in enumerate(perm)}
    y = np.array([r["y"] for r in rows])
    F = np.array([r["f"] for r in rows])
    s = np.array([score[r["id"]] for r in rows])[:, None]
    fo = np.array([fold[r["cycle"]] for r in rows])
    preds = {}
    for name, X in (("F", F), ("F_plus", np.hstack([F, s])), ("Fimg", F[:, 1:]), ("Fimg_plus", np.hstack([F[:, 1:], s])),
                    ("score_only", s)):
        p = np.zeros(len(y))
        for k in range(5):
            tr, te = fo != k, fo == k
            p[te] = _lr(X[tr], y[tr], X[te])
        preds[name] = p
    cp = {c: i for i, c in enumerate(cyc)}
    C = np.random.default_rng(K.SEED).multinomial(len(cyc), np.full(len(cyc), 1 / len(cyc)), size=B).astype(float)
    W = C[:, [cp[r["cycle"]] for r in rows]]
    out = {}
    for name, p in preds.items():
        pos, neg = p[y == 1], p[y == 0]
        out[name] = (float(S.wauc(pos, neg, np.ones((1, len(pos))), np.ones((1, len(neg))))[0]),
                     S.wauc(pos, neg, W[:, y == 1], W[:, y == 0]))
    raw = (float(S.wauc(s[y == 1, 0], s[y == 0, 0], np.ones((1, (y == 1).sum())), np.ones((1, (y == 0).sum())))[0]),
           S.wauc(s[y == 1, 0], s[y == 0, 0], W[:, y == 1], W[:, y == 0]))
    out["score_raw_auc"] = raw
    out["dAUC_over_F"] = (out["F_plus"][0] - out["F"][0], out["F_plus"][1] - out["F"][1])
    out["dAUC_over_Fimg"] = (out["Fimg_plus"][0] - out["Fimg"][0], out["Fimg_plus"][1] - out["Fimg"][1])
    out["_n"] = dict(n_X=int((y == 1).sum()), n_SAME=int((y == 0).sum()), n_cycles=len(cyc))
    return out


def summarise(results):
    """results: list of incremental() outputs (seeds) -> means of points and per-draw means."""
    o = {}
    for k in results[0]:
        if k.startswith("_"):
            o[k] = results[0][k]
            continue
        pts = [r[k][0] for r in results]
        dr = np.mean([r[k][1] for r in results], 0)
        o[k] = dict(mean=round(float(np.mean(pts)), 4), seeds=[round(x, 4) for x in pts], ci=[round(x, 4) for x in S.ci(dr)])
    return o


def verdict(d):
    lo, hi = d["ci"]
    if d["mean"] >= 0.05 and lo > 0:
        return "falsified: the network adds information beyond the measured traces"
    if hi < 0.03:
        return "supported: no X-vs-SAME information beyond simple statistics and θ"
    return "undecided"

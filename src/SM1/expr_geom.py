"""SM1 expression check (amendment A3 substitute; geometry only, no pixel is read).

Logistic probe (standardised, C = 0.1) on the 20 mouth points (106-point indices 52..71) relative to the eye midpoint
(means of points 33..42 and 87..96), divided by the inter-ocular distance. Trained on the AR1 FRLL frames' .tem files
(neutral _03 = 0, smiling _08 = 1; 5-fold by person accuracy printed), applied to the if106 points of the SMDD
genuine renders and, for morphs, to the mean of the two contributors' points. Smile rate = share with p > 0.5.

  python3 -I expr_geom.py -> RES/expr_geom.json
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FRLL = pathlib.Path("/mnt/t7/smad_next/AR1/frll_src")
MOUTH = list(range(52, 72))
EA, EB = list(range(33, 43)), list(range(87, 97))


def read_tem(p):
    lines = open(p).read().splitlines()
    n = int(lines[0])
    return np.array([list(map(float, lines[i].split())) for i in range(1, n + 1)], np.float64)


def feat(lm):
    lm = np.asarray(lm, np.float64)
    ea, eb = lm[EA].mean(0), lm[EB].mean(0)
    mid, iod = (ea + eb) / 2, np.hypot(*(eb - ea))
    return ((lm[MOUTH] - mid) / iod).ravel()


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    X, y, g = [], [], []
    for p in sorted(FRLL.glob("*.tem")):
        pid, ex = p.stem.split("_")
        X.append(feat(read_tem(p)))
        y.append(1 if ex == "08" else 0)
        g.append(pid)
    X, y, g = np.array(X), np.array(y), np.array(g)
    ug = np.array(sorted(set(g)))
    fold = {u: i % 5 for i, u in enumerate(np.random.default_rng(K.SEED).permutation(ug))}
    acc = []
    for f in range(5):
        te = np.array([fold[x] == f for x in g])
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X[~te], y[~te])
        acc.append(float((m.predict(X[te]) == y[te]).mean()))
    probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X, y)
    bf = K.load_if106()
    G = np.array([feat(v * 256) for v in bf.values() if np.isfinite(v).all()])
    pg = probe.predict_proba(G)[:, 1]
    lm = {}
    for st in ("pool", "contrib"):
        f = K.OUT / f"lm/srcm_if106_{st}.npz"
        if f.exists():
            z = np.load(f, allow_pickle=False)
            L = z["lms"]
            for i, n in enumerate(z["names"]):
                lm[str(n)] = L[i]
    out = dict(frll_cv_accuracy_by_person=[round(a, 3) for a in acc], frll_n=int(len(y)),
               genuine=dict(n=int(len(G)), smile_rate=float((pg > 0.5).mean()), mean_p=float(pg.mean())))
    pairs = [(a, b) for a, b in K.release_pairs() if a in lm and b in lm and np.isfinite(lm[a]).all()
             and np.isfinite(lm[b]).all()]
    if pairs:
        M = np.array([feat((lm[a] + lm[b]) / 2 * 256) for a, b in pairs])
        pm = probe.predict_proba(M)[:, 1]
        C = np.array([feat(lm[n] * 256) for n in sorted({x for p in pairs for x in p})])
        pc = probe.predict_proba(C)[:, 1]
        out["release_morphs_mean_shape"] = dict(n=len(pairs), smile_rate=float((pm > 0.5).mean()), mean_p=float(pm.mean()))
        out["contributor_renders"] = dict(n=len(C), smile_rate=float((pc > 0.5).mean()), mean_p=float(pc.mean()))
        for p in K.PARTNERS:
            out.setdefault("partners", {})[p] = round(float(probe.predict_proba(feat(lm[p] * 256)[None])[0, 1]), 4)
    json.dump(out, open(K.RES / "expr_geom.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

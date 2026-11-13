"""TB1 amendment 2 (post hoc, from REVIEW_TB1_PREMISE_20261113.md): energy and geometry controls for the premise, and
two descriptive reads. Zero GPU; reads the registered feature file, BD1's D, the AR1 pool and .tem files only.
- E = band-limited energy of the half-difference (P4_Etot / P3_Etot, the five bands B1..B5, hull); W = mean
  landmark displacement over the 106 points between the two source photos (H to B for two-person, H to S for
  same-person), from the .tem files.
- Folds and bootstrap by connected components of the person graph (host - partner edges).
- Reads: profile (cross-fitted logistic on ln p_1..p_5) within E quintiles; gain of the profile over [log D, log E,
  log W] and over [log E, log W] (component bootstrap of the gain); within W quintiles; joint D x W tertiles.
- Descriptive (a): two-person rows by host-partner capture-day gap (pool sessions; same day included) against
  same-person rows at matched gap bins, per database. (b): same-person pairs with W at or above the two-person 10th
  percentile against two-person pairs matched 1:1 on W.
  python -I tb1_amend2.py --out tb1_amend2.json
  python -I tb1_amend2.py --mock --ffile F --out mock.json"""
import argparse
import csv
import datetime
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
from bd1_read import auc, sha, strat_auc  # noqa: E402

FFILE = pathlib.Path("/mnt/t7/smad_next/TB1/tb1_feats.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
B = 2000


def tem(p):
    lines = open(p[:-4] + ".tem").read().splitlines()
    n = int(lines[0])
    return np.array([list(map(float, lines[i].split())) for i in range(1, n + 1)])


def date(s):
    s = s.strip()
    if "-" in s:
        return datetime.date.fromisoformat(s)
    y = int(s[:2])
    return datetime.date(1900 + y if y > 50 else 2000 + y, int(s[2:4]), int(s[4:6]))


def components(hosts, pool):
    par = {}

    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for h in hosts:
        a, b = find(h), find(pool[h]["B_pid"])
        par[a] = b
    return {h: find(h) for h in hosts}


def cf_scores(X1, X0, comp, seed=20261181, folds=5):
    """component-grouped cross-fitted standardised logistic scores for rows 1 (two-person) and 0 (same-person)"""
    from sklearn.linear_model import LogisticRegression
    cs = sorted(set(comp))
    rng = np.random.default_rng(seed)
    f = dict(zip(cs, rng.permutation(len(cs)) % folds))
    g = np.array([f[c] for c in comp] * 2)
    X = np.r_[X1, X0]
    y = np.r_[np.ones(len(X1)), np.zeros(len(X0))]
    s = np.zeros(len(y))
    for k in range(folds):
        tr, te = g != k, g == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=5000).fit((X[tr] - mu) / sd, y[tr])
        s[te] = m.decision_function((X[te] - mu) / sd)
    return s[: len(X1)], s[len(X1):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--ffile", default=str(FFILE))
    a = ap.parse_args()
    if not a.mock:
        for f in (a.ffile, str(DF)):
            assert sha(f) == pathlib.Path(f + ".sha256").read_text().split()[0]
    R = list(csv.DictReader(open(a.ffile)))
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    hosts = [r["host"] for r in R]
    comp = [components(hosts, pool)[h] for h in hosts]
    lp = lambda n: np.log(np.array([[float(r[f"{n}_p{k}"]) for k in range(1, 6)] for r in R]) + 1e-12)   # noqa: E731
    X4, X3 = lp("P4"), lp("P3")
    if a.mock:
        rng = np.random.default_rng(9)
        X4, X3 = rng.normal(size=X4.shape), rng.normal(size=X3.shape)
    E4 = np.log(np.array([float(r["P4_Etot"]) for r in R]))
    E3 = np.log(np.array([float(r["P3_Etot"]) for r in R]))
    D4 = np.log(np.array([float(D[r["S4_id"]]["D"]) for r in R]))
    D3 = np.log(np.array([float(D[r["S3_id"]]["D"]) for r in R]))
    W4 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["B"]), axis=1).mean() for h in hosts]))
    W3 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["S"]), axis=1).mean() for h in hosts]))
    db = np.array([pool[h]["db"] for h in hosts])
    out = dict(mock=a.mock, n=len(R), n_components=len(set(comp)))
    s4, s3 = cf_scores(X4, X3, comp)
    out["profile_auc"] = auc(s4, s3)
    for name, (x4, x3) in dict(E=(E4, E3), W=(W4, W3), D=(D4, D3)).items():
        sa, cov, strata = strat_auc(s4, s3, np.exp(x4), np.exp(x3))
        out[f"profile_within_{name}"] = dict(auc=sa, cover=cov, strata=[x["auc"] for x in strata])
        a0 = auc(x4, x3)
        out[f"{name}_alone_auc"] = max(a0, 1 - a0)
    # joint D x W tertiles
    tD, tW = np.quantile(np.r_[D4, D3], [1 / 3, 2 / 3]), np.quantile(np.r_[W4, W3], [1 / 3, 2 / 3])
    cut = lambda x, t: np.digitize(x, t)        # noqa: E731
    num = den = 0.0
    cells = []
    for i in range(3):
        for j in range(3):
            pm, nm = (cut(D4, tD) == i) & (cut(W4, tW) == j), (cut(D3, tD) == i) & (cut(W3, tW) == j)
            if pm.sum() >= 10 and nm.sum() >= 10:
                v = auc(s4[pm], s3[nm])
                w = pm.sum() * nm.sum()
                num, den = num + v * w, den + w
                cells.append(dict(D=i, W=j, n_pos=int(pm.sum()), n_neg=int(nm.sum()), auc=v))
    out["profile_within_DxW"] = dict(auc=num / den if den else None, cells=cells,
                                     cover=sum(c["n_pos"] + c["n_neg"] for c in cells) / (2 * len(R)))
    # gains
    def gain(base1, base0, seed=20261181, idx=None):
        b1, b0 = (base1, base0) if idx is None else (base1[idx], base0[idx])
        x4_, x3_ = (X4, X3) if idx is None else (X4[idx], X3[idx])
        cp = comp if idx is None else [comp[i] for i in idx]
        a_b = auc(*cf_scores(b1, b0, cp, seed))
        a_p = auc(*cf_scores(np.c_[b1, x4_], np.c_[b0, x3_], cp, seed))
        return a_p - a_b, a_b, a_p
    g1 = gain(np.c_[D4, E4, W4], np.c_[D3, E3, W3])
    g2 = gain(np.c_[E4, W4], np.c_[E3, W3])
    out["gain_over_logD_logE_logW"] = dict(gain=g1[0], base=g1[1], plus_profile=g1[2])
    out["gain_over_logE_logW"] = dict(gain=g2[0], base=g2[1], plus_profile=g2[2])
    cs = sorted(set(comp))
    members = {c: [i for i, x in enumerate(comp) if x == c] for c in cs}
    rng = np.random.default_rng(20261182)
    bs = []
    for _ in range(B if not a.mock else 50):
        pick = rng.choice(len(cs), len(cs))
        idx = np.array([i for p in pick for i in members[cs[p]]])
        try:
            bs.append(gain(np.c_[E4, W4], np.c_[E3, W3], idx=idx)[0])
        except Exception:
            pass
    lo = float(np.percentile(bs, 2.5))
    out["gain_over_logE_logW"]["component_ci"] = [lo, float(np.percentile(bs, 97.5))]
    gv = g2[0]
    out["verdict"] = ("falsified: the profile adds < +0.02 over band energy and geometry" if gv < 0.02 else
                      "supported: the profile adds >= +0.03 beyond band energy and geometry (component lower bound > 0)"
                      if gv >= 0.03 and lo > 0 else "inconclusive")
    out["H_new_1"] = "falsified" if (gv >= 0.03 and lo > 0) else "not falsified"
    # descriptive (a): capture-day gap
    gap4 = np.array([abs((date(pool[pool[h]["B_pid"]]["S_session"]) - date(pool[h]["H_session"])).days) for h in hosts])
    gap3 = np.array([abs((date(pool[h]["S_session"]) - date(pool[h]["H_session"])).days) for h in hosts])
    bins = [(0, 0), (1, 30), (31, 180), (181, 100000)]
    gaps = {}
    for d_ in ("frgc", "feret"):
        rows = []
        for lo_, hi_ in bins:
            pm = (db == d_) & (gap4 >= lo_) & (gap4 <= hi_)
            nm = (db == d_) & (gap3 >= lo_) & (gap3 <= hi_)
            rows.append(dict(bin=f"{lo_}-{hi_}", n_two=int(pm.sum()), n_same=int(nm.sum()),
                             auc=auc(s4[pm], s3[nm]) if pm.sum() >= 5 and nm.sum() >= 5 else None))
        gaps[d_] = rows
    out["descriptive_day_gap"] = gaps
    # descriptive (b): same-person high-W against two-person matched 1:1 on W
    q10 = np.quantile(W4, 0.10)
    hi3 = np.where(W3 >= q10)[0]
    used, pairs = set(), []
    for i in hi3[np.argsort(-W3[hi3])]:
        cand = [j for j in np.argsort(np.abs(W4 - W3[i])) if j not in used]
        if cand:
            used.add(cand[0])
            pairs.append((cand[0], i))
    if pairs:
        p4 = np.array([s4[j] for j, _ in pairs])
        p3 = np.array([s3[i] for _, i in pairs])
        out["descriptive_matched_W"] = dict(n=len(pairs), auc=auc(p4, p3),
                                            W_two_median=float(np.exp(np.median([W4[j] for j, _ in pairs]))),
                                            W_same_median=float(np.exp(np.median([W3[i] for _, i in pairs]))))
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=0, default=float)[:5000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

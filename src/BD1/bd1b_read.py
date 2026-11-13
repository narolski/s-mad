"""BD1 amendment 2 reader: BD1b (FR similarity and colour on development hosts), the session-gap read, and the
blanked-row addendum. Blocks FS1 (registered), AB1 and SE1 (replication), read separately. Zero GPU.
  python -I bd1b_read.py --out bd1b_read.json
  python -I bd1b_read.py --mock --dfile D.csv --ffile F.csv --out mock.json      (random logits; no tar opened)"""
import argparse
import csv
import datetime
import io
import json
import pathlib
import sys
import tarfile

import numpy as np
from scipy.stats import rankdata, spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bd1_read import BLOCKS, auc, sha, strat_auc  # noqa: E402

DFILE = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
FFILE = pathlib.Path("/mnt/t7/smad_next/BD1/d_feats.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
PROP = ("D", "D_Y", "D_int", "D_band", "D_dc", "D_lin", "D_grad")


def date(s):
    s = s.strip()
    if "-" in s:
        return datetime.date.fromisoformat(s)
    y = int(s[:2])
    return datetime.date(1900 + y if y > 50 else 2000 + y, int(s[2:4]), int(s[4:6]))


def partial_spearman(x, y, Z):
    rx, ry = rankdata(x), rankdata(y)
    Zr = np.c_[np.ones(len(x)), np.column_stack([rankdata(z) for z in Z.T])]
    ex = rx - Zr @ np.linalg.lstsq(Zr, rx, rcond=None)[0]
    ey = ry - Zr @ np.linalg.lstsq(Zr, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def crossfit_auc(Xp, Xn, hosts_p, hosts_n, seed=20261152, folds=5):
    """host-grouped 5-fold cross-fitted logistic score; returns AUC of out-of-fold scores (positives first)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    hs = sorted(set(hosts_p) | set(hosts_n))
    rng = np.random.default_rng(seed)
    f = dict(zip(hs, rng.permutation(len(hs)) % folds))
    X = np.r_[Xp, Xn]
    y = np.r_[np.ones(len(Xp)), np.zeros(len(Xn))]
    g = np.array([f[h] for h in list(hosts_p) + list(hosts_n)])
    s = np.zeros(len(y))
    for k in range(folds):
        tr, te = g != k, g == k
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(X[tr], y[tr])
        s[te] = m.decision_function(X[te])
    return auc(s[: len(Xp)], s[len(Xp):])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dfile", default=str(DFILE))
    ap.add_argument("--ffile", default=str(FFILE))
    a = ap.parse_args()
    if not a.mock:
        for f in (a.dfile, a.ffile):
            assert sha(f) == pathlib.Path(f + ".sha256").read_text().split()[0]
    D = {r["id"]: r for r in csv.DictReader(open(a.dfile))}
    for r in csv.DictReader(open(a.ffile)):
        D[r["id"]].update({k: r[k] for k in ("D_dc", "D_ac", "D_lin", "D_grad")})
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    man = {r["id"]: r for r in csv.DictReader(open(MAN)) if r["fam"] == "splice"}
    by = lambda role, rung: sorted([i for i, r in man.items() if r["role"] == role and r["rung"] == rung], key=lambda i: man[i]["host"])  # noqa: E731
    f = lambda L, k: np.array([float(D[i][k]) for i in L])   # noqa: E731
    cosHS = lambda L: np.array([float(pool[man[i]["host"]]["cos_HS"]) for i in L])   # noqa: E731
    gap = lambda L: np.array([abs((date(pool[man[i]["host"]]["S_session"]) - date(pool[man[i]["host"]]["H_session"])).days) for i in L])  # noqa: E731
    S3d, S4d, S3t = by("dev", "S3"), by("dev", "S4"), by("test", "S3")
    assert [man[i]["host"] for i in S3d] == [man[i]["host"] for i in S4d]
    S3all = S3d + S3t
    dbs = {db: [i for i in S3all if pool[man[i]["host"]]["db"] == db] for db in ("frgc", "feret")}
    out = dict(mock=a.mock, n=dict(dev_S3=len(S3d), dev_S4=len(S4d), S3_all=len(S3all), **{f"S3_{k}": len(v) for k, v in dbs.items()}))
    # references (no network): each statistic's own pure reference inside its quintiles, dev hosts
    refs = {k: strat_auc(f(S4d, k), f(S3d, k), f(S4d, k), f(S3d, k))[0] for k in ("D_dc", "D_lin")}
    out["refs_dev"] = refs
    out["prop_auc_dev"] = crossfit_auc(np.column_stack([f(S4d, k) for k in PROP]), np.column_stack([f(S3d, k) for k in PROP]),
                                       [man[i]["host"] for i in S4d], [man[i]["host"] for i in S3d])
    out["rho_gap_cosHS"] = {db: float(spearmanr(gap(L), cosHS(L)).correlation) for db, L in dbs.items()}
    out["gap_days_median"] = {db: float(np.median(gap(L))) for db, L in dbs.items()}
    blanks = {k: by(role, k) for role in ("dev",) for k in ("S4_bg", "S3_bg", "S4_face", "S3_face")}
    blanks_t = {k: by("test", k) for k in ("S4_bg", "S3_bg", "S4_face", "S3_face")}
    for blk, nets in BLOCKS.items():
        res = {}
        for path, name, arm, s in nets:
            if arm != "Sb":
                continue
            try:
                if a.mock:
                    rng = np.random.default_rng(s)
                    L = {i: float(rng.normal(-1, 2)) for i in man}
                else:
                    assert sha(path) == pathlib.Path(path + ".sha256").read_text().split()[0]
                    with tarfile.open(path) as tf:
                        z = np.load(io.BytesIO(tf.extractfile(f"{name}/scores_eval.npz").read()))
                    L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            except Exception as ex:
                res[f"Sb_s{s}"] = dict(error=repr(ex))
                continue
            v = lambda ids: np.array([L[i] for i in ids])   # noqa: E731
            n3, p4 = v(S3d), v(S4d)
            Z = np.column_stack([f(S3d, "D"), f(S3d, "D_lin"), f(S3d, "D_dc")])
            r = dict(rho_raw_cosHS=float(spearmanr(n3, cosHS(S3d)).correlation),
                     rho_partial_cosHS=partial_spearman(n3, cosHS(S3d), Z))
            for k in ("D_dc", "D_lin"):
                sa = strat_auc(p4, n3, f(S4d, k), f(S3d, k))
                r[f"strat_{k}"] = sa[0]
                r[f"strat_{k}_cover"] = sa[1]
                r[f"strat_{k}_minus_ref"] = (sa[0] - refs[k]) if (sa[0] is not None and sa[1] >= 0.5) else None
            Xp = np.column_stack([f(S4d, k) for k in PROP])
            Xn = np.column_stack([f(S3d, k) for k in PROP])
            hp, hn = [man[i]["host"] for i in S4d], [man[i]["host"] for i in S3d]
            r["prop_plus_logit_auc"] = crossfit_auc(np.c_[Xp, p4], np.c_[Xn, n3], hp, hn)
            r["gain_over_prop"] = r["prop_plus_logit_auc"] - out["prop_auc_dev"]
            r["auc_dev_S4_vs_S3"] = auc(p4, n3)
            g = {}
            for db, Ld in dbs.items():
                x = v(Ld)
                g[db] = dict(rho=float(spearmanr(x, gap(Ld)).correlation),
                             rho_partial_cosHS=partial_spearman(x, gap(Ld), cosHS(Ld)[:, None]))
            r["gap"] = g
            r["inside_dev"] = auc(v(blanks["S4_bg"]), v(blanks["S3_bg"]))
            r["outside_dev"] = auc(v(blanks["S4_face"]), v(blanks["S3_face"]))
            r["inside_test_seen"] = auc(v(blanks_t["S4_bg"]), v(blanks_t["S3_bg"]))
            r["outside_test_seen"] = auc(v(blanks_t["S4_face"]), v(blanks_t["S3_face"]))
            res[f"Sb_s{s}"] = r
        ok = [x for x in res.values() if "error" not in x]
        need = 4
        c = lambda fn: sum(1 for x in ok if fn(x))   # noqa: E731
        V = {}
        V["FR_partial"] = dict(values=[x["rho_partial_cosHS"] for x in ok],
                               verdict="supported" if c(lambda x: x["rho_partial_cosHS"] <= -0.10) >= need else
                               ("falsified" if c(lambda x: x["rho_partial_cosHS"] > -0.05) >= 3 else "weak"))
        for k in ("D_dc", "D_lin"):
            vals = [x[f"strat_{k}_minus_ref"] for x in ok]
            V[f"colour_{k}"] = dict(values=vals, verdict="residual beyond this colour statistic" if sum(1 for y in vals if y is not None and y >= 0.10) >= need
                                    else ("accounted for by this colour statistic" if sum(1 for y in vals if y is not None and y <= 0.03) >= need else "inconclusive"))
        V["adds_to_propensity"] = dict(values=[x["gain_over_prop"] for x in ok],
                                       verdict="supported" if c(lambda x: x["gain_over_prop"] >= 0.03) >= need else
                                       ("falsified" if c(lambda x: x["gain_over_prop"] < 0.01) >= need else "weak"))
        V["session_gap"] = dict(values={db: [x["gap"][db]["rho"] for x in ok] for db in dbs},
                                verdict="supported" if c(lambda x: all(x["gap"][db]["rho"] > 0.15 for db in dbs)) >= need else
                                ("falsified" if c(lambda x: all(x["gap"][db]["rho"] <= 0.05 for db in dbs)) >= need else "inconclusive"))
        V["blanked"] = dict(inside=[x["inside_dev"] for x in ok], outside=[x["outside_dev"] for x in ok],
                            verdict="residual inside the hull" if c(lambda x: x["inside_dev"] >= 0.65) >= need and c(lambda x: x["outside_dev"] <= 0.55) >= need
                            else ("outside contributes" if c(lambda x: x["outside_dev"] >= 0.60) >= need else "inconclusive"))
        out[blk] = dict(per_net=res, verdicts=V, n_seeds=len(ok))
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("n", "refs_dev", "prop_auc_dev", "rho_gap_cosHS", "gap_days_median")}, default=float))
    for blk in BLOCKS:
        print(blk, json.dumps(out[blk]["verdicts"], default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

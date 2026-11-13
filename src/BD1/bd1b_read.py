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


def db_ranked(x, db):
    """ranks within each database (amendment 3: database-stratified statistics)"""
    x, db = np.asarray(x, float), np.asarray(db)
    r = np.empty(len(x))
    for d in np.unique(db):
        m = db == d
        r[m] = rankdata(x[m]) / m.sum()
    return r


def boot_partial(x, y, Z, seed=20261153, B=2000):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        try:
            v.append(partial_spearman(x[i], y[i], Z[i]))
        except Exception:
            pass
    return [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]


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
        if r["rung"] in ("S3", "S4"):
            assert float(r["D_dc"]) > 0 and float(r["D_lin"]) > 0, r["id"]
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
    hp0, hn0 = [man[i]["host"] for i in S4d], [man[i]["host"] for i in S3d]
    Xp0, Xn0 = np.column_stack([f(S4d, k) for k in PROP]), np.column_stack([f(S3d, k) for k in PROP])
    FSEEDS = [20261152 + j for j in range(20)]                     # amendment 3: 20 fold splits
    prop = [crossfit_auc(Xp0, Xn0, hp0, hn0, seed=fs) for fs in FSEEDS]
    out["prop_auc_dev"] = float(np.mean(prop))
    out["prop_auc_dev_sd"] = float(np.std(prop))
    dbv = lambda L: np.array([pool[man[i]["host"]]["db"] for i in L])   # noqa: E731
    out["db_counts_dev"] = {d: int((dbv(S3d) == d).sum()) for d in ("frgc", "feret")}
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
                needed = S3d + S4d + S3t + [i for v_ in list(blanks.values()) + list(blanks_t.values()) for i in v_]
                assert all(i in L for i in needed), "missing rows"
            except Exception as ex:
                res[f"Sb_s{s}"] = dict(error=repr(ex))
                continue
            v = lambda ids: np.array([L[i] for i in ids])   # noqa: E731
            n3, p4 = v(S3d), v(S4d)
            dbi = (dbv(S3d) == "feret").astype(float)
            Z = np.column_stack([f(S3d, "D"), f(S3d, "D_lin"), f(S3d, "D_dc"), dbi])     # amendment 3: database covariate
            r = dict(rho_raw_cosHS=float(spearmanr(n3, cosHS(S3d)).correlation),
                     rho_partial_cosHS=partial_spearman(n3, cosHS(S3d), Z),
                     rho_partial_cosHS_ci=boot_partial(n3, cosHS(S3d), Z))
            for k in ("D_dc", "D_lin"):
                sa = strat_auc(p4, n3, f(S4d, k), f(S3d, k))
                r[f"strat_{k}"] = sa[0]
                r[f"strat_{k}_cover"] = sa[1]
                r[f"strat_{k}_minus_ref"] = (sa[0] - refs[k]) if (sa[0] is not None and sa[1] >= 0.5) else None
            Xp = np.column_stack([f(S4d, k) for k in PROP])
            Xn = np.column_stack([f(S3d, k) for k in PROP])
            hp, hn = [man[i]["host"] for i in S4d], [man[i]["host"] for i in S3d]
            gains = [crossfit_auc(np.c_[Xp, p4], np.c_[Xn, n3], hp, hn, seed=fs) - pa for fs, pa in zip(FSEEDS, prop)]
            r["gain_over_prop"] = float(np.mean(gains))
            r["gain_over_prop_sd"] = float(np.std(gains))
            r["auc_dev_S4_vs_S3"] = auc(p4, n3)
            g = {}
            for db, Ld in dbs.items():
                x = v(Ld)
                Zd = np.column_stack([cosHS(Ld), f(Ld, "D"), f(Ld, "D_dc")])
                g[db] = dict(rho_raw=float(spearmanr(x, gap(Ld)).correlation),
                             rho_partial=partial_spearman(x, gap(Ld), Zd), ci=boot_partial(x, gap(Ld), Zd))
            # amendment 3 primary: database-stratified partial (ranks within database, database indicator)
            xa, dba = v(S3all), dbv(S3all)
            Za = np.column_stack([db_ranked(cosHS(S3all), dba), db_ranked(f(S3all, "D"), dba), db_ranked(f(S3all, "D_dc"), dba),
                                  (dba == "feret").astype(float)])
            g["stratified_partial"] = partial_spearman(db_ranked(xa, dba), db_ranked(gap(S3all), dba), Za)
            g["stratified_partial_ci"] = boot_partial(db_ranked(xa, dba), db_ranked(gap(S3all), dba), Za)
            r["gap"] = g
            r["inside_dev"] = auc(v(blanks["S4_bg"]), v(blanks["S3_bg"]))
            r["outside_dev"] = auc(v(blanks["S4_face"]), v(blanks["S3_face"]))
            r["inside_test_seen"] = auc(v(blanks_t["S4_bg"]), v(blanks_t["S3_bg"]))
            r["outside_test_seen"] = auc(v(blanks_t["S4_face"]), v(blanks_t["S3_face"]))
            r["face_rows_flag"] = {k: float((v(blanks[k]) > 0).mean()) for k in ("S4_face", "S3_face", "S4_bg", "S3_bg")}
            r["face_rows_sd"] = {k: float(v(blanks[k]).std()) for k in ("S4_face", "S3_face", "S4_bg", "S3_bg")}
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
        V["session_gap"] = dict(values=[x["gap"]["stratified_partial"] for x in ok],
                                per_db={db: [x["gap"][db]["rho_partial"] for x in ok] for db in dbs},
                                verdict="supported" if c(lambda x: x["gap"]["stratified_partial"] > 0.15) >= need else
                                ("falsified" if c(lambda x: x["gap"]["stratified_partial"] <= 0.05) >= need else "inconclusive"),
                                note="colorFERET per-database values descriptive only (n=56)")
        nd = c(lambda x: x["face_rows_flag"]["S4_face"] <= 0.05 and x["face_rows_flag"]["S3_face"] <= 0.05)
        inside_ok = c(lambda x: x["inside_dev"] >= 0.65) >= need
        V["blanked"] = dict(inside=[x["inside_dev"] for x in ok], outside=[x["outside_dev"] for x in ok], n_outside_nondiagnostic=nd,
                            label="formalises values already seen (post hoc)",
                            verdict=("inside-only signal; outside-only read non-diagnostic (face-blanked rows ≤ 5% flagged in both classes)"
                                     if inside_ok and nd >= need else
                                     "residual inside the hull; no outside-only signal" if inside_ok and c(lambda x: x["outside_dev"] <= 0.55) >= need
                                     else ("outside contributes" if c(lambda x: x["outside_dev"] >= 0.60) >= need else "inconclusive")))
        out[blk] = dict(per_net=res, verdicts=V, n_seeds=len(ok))
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: out[k] for k in ("n", "refs_dev", "prop_auc_dev", "rho_gap_cosHS", "gap_days_median")}, default=float))
    for blk in BLOCKS:
        print(blk, json.dumps(out[blk]["verdicts"], default=lambda x: round(float(x), 3)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

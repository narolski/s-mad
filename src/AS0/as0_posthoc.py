"""Mirror-asymmetry test (AS0): POST HOC addendum requested by the lead after the independent review
(experiments/reviews/REVIEW_AS0_20261111.md, section 4 item 1). Not registered; descriptive only. Reads the merged
measurement file; no image is read.

(1) pool offset: genuine FRGC against genuine colorFERET photos (AR1 R0), AUC = P(L_FRGC < L_FERET) per band, raw and
    after OLS on |yaw|, yaw, nose offset and lighting index (and additionally log Laplacian variance);
(2) logistic ceiling: out-of-fold logistic regression on L(B1..B5) plus shape asymmetry (calculated from source
    landmark files, and detected on the built images), 5 strictly person-disjoint folds (test = items whose host is in
    the fold; training excludes every item that contains a person of the test items); same-person (R3) against
    two-person (R4) and warp-only (R2w) against two-person, both engines pooled;
(3) review F9: Spearman of partner similarity cos_HB with L_R4 - L_R2w per band and engine, host bootstrap;
(4) review F8: neutral (_03) against smiling (_08) FRLL photos (corrected MAD22 natives), AUC = P(L_03 < L_08).
  python3 -I as0_posthoc.py -> experiments/AS0_mirror-asymmetry/posthoc_addendum.json
"""
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_analyse as A  # noqa: E402
import as0_common as K  # noqa: E402
import as0_measure as M  # noqa: E402

BANDS5 = ["B1", "B2", "B3", "B4", "B5"]


def resid(D, ids, band, covs):
    y = D.val(ids, band=band)
    Z = np.stack([np.ones(len(ids))] + [D.cov(ids, c) for c in covs], 1)
    m = np.isfinite(y) & np.isfinite(Z).all(1)
    beta = np.linalg.lstsq(Z[m], y[m], rcond=None)[0]
    return y - Z @ beta, m


def main():
    D = A.Data()
    out = dict(label="POST HOC (lead's request after the independent review); not registered; descriptive")
    R0 = [i for i in D.items if D.items[i]["set"] == "L" and D.items[i]["role"] == "R0" and i in D.ix and D.ok(i)]
    Dr = A.draw_for(D, R0, 2000)
    fr = [i for i in R0 if D.items[i]["db"] == "frgc"]
    fe = [i for i in R0 if D.items[i]["db"] == "feret"]
    po = {}
    for b in BANDS5 + ["BB"]:
        row = dict(raw=A.auc_ci(Dr, D, fr, fe, band=b))
        for lab, cv in (("resid_pose_light", ["abs_yaw", "yaw", "nose_off", "light"]),
                        ("resid_pose_light_lapvar", ["abs_yaw", "yaw", "nose_off", "light", "lap_mask"])):
            r, m = resid(D, fr + fe, b, cv)
            n = len(fr)
            X = [i for i, k in zip(fr, m[:n]) if k]
            Y = [i for i, k in zip(fe, m[n:]) if k]
            row[lab] = A.auc_scores(Dr, D, X, Y, -r[:n][m[:n]], -r[n:][m[n:]])
        row["mean_L_gap_FRGC_minus_FERET"] = round(float(np.mean(D.val(fr, band=b)) - np.mean(D.val(fe, band=b))), 4)
        po[b] = row
    out["pool_offset_R0_FRGC_vs_FERET"] = po
    out["pool_offset_counts"] = dict(frgc=len(fr), feret=len(fe))

    # (2) logistic ceiling
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    det = {}
    lmz = np.load(K.OUT / "lm/landmarks.npz", allow_pickle=False)
    for i, l, n in zip(lmz["ids"].tolist(), lmz["lm"], lmz["n_faces"]):
        if i.endswith("|det") and n > 0:
            det[i[:-4]] = -M.shape_asym(l.astype(np.float64), 512)
    fold = lambda p: int(hashlib.sha1(p.encode()).hexdigest(), 16) % 5
    L = lambda role: [i for i in D.items if D.items[i]["set"] == "L" and D.items[i]["role"] == role and i in D.ix
                      and D.ok(i) and not D.isval(i)]
    ceil = {}
    for name, neg_role in (("R3 vs R4 (same- against two-person)", "R3"), ("R2w vs R4 (warp-only against two-person)", "R2w")):
        pos, neg = L("R4"), L(neg_role)
        ids = pos + neg
        yl = np.array([1] * len(pos) + [0] * len(neg))
        bands = np.stack([D.val(ids, band=b) for b in BANDS5], 1)
        feats = {"bands": bands,
                 "bands + shape (calculated from source files)": np.c_[bands, D.cov(ids, "shape_L")],
                 "bands + shape (detected)": np.c_[bands, [det.get(i, np.nan) for i in ids]],
                 "shape (detected) alone": np.array([[det.get(i, np.nan)] for i in ids])}
        res = {}
        for fn, F in feats.items():
            ok = np.isfinite(F).all(1)
            oof = np.full(len(ids), np.nan)
            pers = [set(D.items[i]["persons"].split("|")) for i in ids]
            for f in range(5):
                te = np.array([fold(D.items[i]["host"]) == f for i in ids]) & ok
                tp = set().union(*[pers[j] for j in np.where(te)[0]])
                tr = np.array([not (pers[j] & tp) for j in range(len(ids))]) & ok & ~te
                sc = StandardScaler().fit(F[tr])
                clf = LogisticRegression(C=1.0, max_iter=2000).fit(sc.transform(F[tr]), yl[tr])
                oof[te] = clf.decision_function(sc.transform(F[te]))
            m = np.isfinite(oof)
            Xi = [i for i, k, y in zip(ids, m, yl) if k and y == 1]
            Yi = [i for i, k, y in zip(ids, m, yl) if k and y == 0]
            sx = oof[m & (yl == 1)]
            sy = oof[m & (yl == 0)]
            DrC = A.draw_for(D, Xi + Yi, 2000)
            res[fn] = A.auc_scores(DrC, D, Xi, Yi, sx, sy)
        ceil[name] = res
    out["logistic_ceiling_person_disjoint_5fold"] = ceil

    # (3) F9: partner similarity
    from scipy.stats import spearmanr
    pool = {r["pid"]: r for r in K.read_csv(K.AR1 / "pool.csv")}
    f9 = {}
    rng = np.random.default_rng([20261111, 62])
    for tool in ("opencv", "facemorpher"):
        for b in BANDS5:
            hs, x, y = [], [], []
            for pid, r in pool.items():
                a4, a2 = f"L|{pid}|{tool}|R4", f"L|{pid}|{tool}|R2w"
                if D.ok(a4) and D.ok(a2):
                    hs.append(pid)
                    x.append(float(r["cos_HB"]))
                    y.append(D.val([a4], band=b)[0] - D.val([a2], band=b)[0])
            x, y = np.array(x), np.array(y)
            rho, p = spearmanr(x, y)
            reps = []
            for _ in range(2000):
                j = rng.integers(0, len(x), len(x))
                reps.append(spearmanr(x[j], y[j])[0])
            f9[f"{tool}|{b}"] = dict(rho=round(float(rho), 4), p=float(p), ci=[round(float(v), 4) for v in
                                                                              np.percentile(reps, [2.5, 97.5])], n=len(x))
    out["F9_spearman_cosHB_vs_L_R4_minus_L_R2w"] = f9

    # (4) F8: neutral against smiling FRLL photos (corrected MAD22 natives)
    nat = [i for i in D.items if D.items[i]["set"] == "Fm" and D.items[i]["role"] == "native" and i in D.ix and D.ok(i)]
    n03 = [i for i in nat if D.items[i]["expr_a"] == "03"]
    n08 = [i for i in nat if D.items[i]["expr_a"] == "08"]
    DrF = A.draw_for(D, nat, 2000)
    out["F8_FRLL_neutral_vs_smiling"] = {b: A.auc_ci(DrF, D, n03, n08, band=b) for b in BANDS5 + ["BB"]}
    json.dump(out, open(K.RES / "posthoc_addendum.json", "w"), indent=1)
    print(json.dumps({k: (v if k != "pool_offset_R0_FRGC_vs_FERET" else {b: (x["raw"]["auc"], x["resid_pose_light"]["auc"])
                                                                            for b, x in v.items()}) for k, v in out.items()
                      if k not in ("F9_spearman_cosHB_vs_L_R4_minus_L_R2w", "F8_FRLL_neutral_vs_smiling")}, indent=1)[:3000])


if __name__ == "__main__":
    main()

"""PN1 certificate (prereg section 9 (i), amendment 2) and matched-subsample test (section 9 (j)).
  python3 -I cert.py tier0     # certificates of A0, B0 and of the evaluation cells; matched-subsample test (CLIP)
  python3 -I cert.py tier1     # certificates of manifests A, B, C (needs the manifests and the cue files)
Cue files: /mnt/t7/smad_next/PN1/cues/cert_*.npz (cert_cues.py). Outputs in experiments/PN1_.../cert/.
"""
import collections
import csv
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402

PIX = ["lap_k1", "lap_k3", "lap_k5"] + [f"band{i}" for i in range(8)] + ["zero_frac"]
OUTD = K.RES / "cert"


def load_cues(size="c224"):
    c = {}
    for f in sorted((K.PN1 / "cues").glob("cert_*.npz")):
        if "_limit" in f.name:
            continue
        z = np.load(f)
        assert [str(n) for n in z["names"]] == PIX
        c.update({str(i): v for i, v in zip(z["ids"], z[size])})
    return c


def history(r):
    h = {"": "native", "61": "s61", "112": "s112"}[r.get("strength", "")]
    if r.get("jpeg"):
        h += "_" + r["jpeg"]
    return h


def engine(r):
    if r["fam"] == "af0":
        return "none" if r["rung"] == "photo" else "opencv_style"
    if r["fam"] == "ladder":
        return "none" if r["rung"] == "R0" else ("opencv_style" if r["tool"] == "opencv" else r["tool"])
    if r["fam"] == "h1":
        return "none" if r["klass"] == "genuine" else "poisson"
    return "none" if r["klass"] == "genuine" else r["tool"]


def components(rows):
    """union-find over persons: both persons of a morph (and of its halves) in one component."""
    par = {}

    def f(x):
        while par.setdefault(x, x) != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for r in rows:
        ps = list(r["persons"]) or [r["id"]]
        for p in ps[1:]:
            par[f(p)] = f(ps[0])
    return [f((list(r["persons"]) or [r["id"]])[0]) for r in rows]


def design(rows, cues, with_cat=True):
    pf = collections.Counter(p for r in rows for p in set(r["persons"]))
    X = np.array([cues[r["id"]] for r in rows], float)
    X[:, :3] = np.log10(X[:, :3] + 1e-6)
    cols = list(PIX)
    if with_cat:
        cats = {"history": [history(r) for r in rows], "engine": [engine(r) for r in rows],
                "pool": [r["pool"] for r in rows]}
        for k, v in cats.items():
            for lev in sorted(set(v)):
                X = np.c_[X, [1.0 if x == lev else 0.0 for x in v]]
                cols.append(f"{k}={lev}")
        X = np.c_[X, [max((pf[p] for p in set(r["persons"])), default=1) for r in rows]]
        cols.append("person_freq")
    return X, cols


def nuisance_design(rows, cues):
    """balanced (nuisance) cues only: history, engine, pool, border bin, person frequency."""
    pf = collections.Counter(p for r in rows for p in set(r["persons"]))
    cats = {"history": [history(r) for r in rows], "engine": [engine(r) for r in rows],
            "pool": [r["pool"] for r in rows], "border": ["0" if cues[r["id"]][-1] == 0 else ">0" for r in rows]}
    X = np.zeros((len(rows), 0))
    for k, v in cats.items():
        for lev in sorted(set(v)):
            X = np.c_[X, [1.0 if x == lev else 0.0 for x in v]]
    X = np.c_[X, [max((pf[p] for p in set(r["persons"])), default=1) for r in rows]]
    return X, cats


def oof_auc(X, y, persons, seed=401, folds=5):
    """amendment 4 item 6 (F7): persons dealt to folds at random; an image is tested in fold k only if all its persons
    are in k and trained on only if none is; straddling images are dropped (share printed). Two classifiers
    (logistic on standardised cues; histogram gradient boosting); bootstrap over the first person of each image."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    persons = [tuple(p) if p else ("img",) for p in persons]
    f, fo, ndrop = K.person_folds(persons, seed, folds)
    if len(np.unique(y)) < 2:
        return dict(note="one class", n=len(y))
    res = dict(n=len(y), n_dropped_straddling=ndrop, share_dropped=ndrop / len(y))
    keep = f >= 0
    for name in ("logistic", "hgb"):
        s = np.full(len(y), np.nan)
        for k in range(folds):
            te = f == k
            tr = np.array([all(fo[p] != k for p in ps) for ps in persons])
            if te.sum() == 0 or len(np.unique(y[tr])) < 2:
                continue
            if name == "logistic":
                sc = StandardScaler().fit(X[tr])
                m = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(X[tr]), y[tr])
                s[te] = m.decision_function(sc.transform(X[te]))
            else:
                m = HistGradientBoostingClassifier(random_state=seed).fit(X[tr], y[tr])
                s[te] = m.predict_proba(X[te])[:, 1]
        ok = keep & np.isfinite(s)
        if len(np.unique(y[ok])) < 2:
            res[name] = dict(note="one class among tested images")
            continue
        a = K.auc(s[ok & (y == 1)], s[ok & (y == 0)])
        units = [persons[i][0] for i in np.where(ok)[0]]
        w, u = K.boot_weights(units, 500, 20261111)
        ui = {x: i for i, x in enumerate(u)}
        gi = np.array([ui[x] for x in units])
        yy, ss = y[ok], s[ok]
        M = K.cmp_matrix(ss[yy == 1], ss[yy == 0])
        d = K.wauc_draws(M, w[:, gi[yy == 1]], w[:, gi[yy == 0]])
        res[name] = dict(auc=a, lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)), n_tested=int(ok.sum()))
    res["auc_max"] = max(res[n]["auc"] for n in ("logistic", "hgb") if "auc" in res.get(n, {})) \
        if any("auc" in res.get(n, {}) for n in ("logistic", "hgb")) else None
    res.update(n_attack=int(y.sum()), n_negative=int((y == 0).sum()))
    return res


def certify(rows, cues, with_cat=True):
    """THE certificate (amendment 4): the nuisance-only classifier; the classifier with softness cues beside it."""
    rows = [r for r in rows if r["id"] in cues]
    y = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
    persons = [r["persons"] for r in rows]
    Xn, cats = nuisance_design(rows, cues)
    out = dict(certificate_nuisance_only=oof_auc(Xn, y, persons), nuisance_cues=list(cats) + ["person_freq"])
    if with_cat:
        X, cols = design(rows, cues, True)
        out["with_softness_and_pixel_cues"] = oof_auc(X, y, persons)
        out["all_cues"] = cols
    X0, cols0 = design(rows, cues, False)
    out["pixel_cues_only"] = oof_auc(X0, y, persons)
    return out


def cells(P):
    """evaluation cells read in prereg section 6: (attack pool, negative pool)."""
    c = [("T_R4_opencv", "T_R2w_opencv"), ("T_R4_opencv", "T_R2w4_opencv"), ("T_R4_opencv", "T_R0"),
         ("T_R4_opencv", "T_R0_61"), ("T_R4_opencv", "T_R2w_opencv_61"), ("T_R4_opencv", "T_R3_opencv"),
         ("T_R4_opencv_61", "T_R2w_opencv"), ("H1_morph", "H1_bona")]
    for fam in ("OpenCV", "Webmorph", "FaceMorpher"):
        c += [(f"MAD22_{fam}_morph", "MAD22_bona_native"), (f"MAD22_{fam}_morph", f"MAD22_{fam}_e7")]
    for fam in ("amsl", "facemorpher", "opencv", "webmorph"):
        c += [(f"FRLL_{fam}_morph", "FRLL_bona_native"), (f"FRLL_{fam}_morph", f"FRLL_{fam}_e7")]
    return [(a, b) for a, b in c if P.get(a) and P.get(b)]


def matched_test(cat, cues, sets):
    """section 9 (j) on CLIP features; pool = B0's unique images (the matching itself balances the strata)."""
    B0 = [r for r in sets["B0"] if r["id"] in cues]
    y = np.array([1 if r["klass"] == "attack" else 0 for r in B0])
    Xn, cats = nuisance_design(B0, cues)
    strata = list(zip(*cats.values()))
    rng = np.random.default_rng(20261111)
    keep = []
    for s in sorted(set(strata)):
        i0 = [i for i, t in enumerate(strata) if t == s and y[i] == 0]
        i1 = [i for i, t in enumerate(strata) if t == s and y[i] == 1]
        k = min(len(i0), len(i1))
        keep += list(rng.permutation(i0)[:k]) + list(rng.permutation(i1)[:k])
    keep = sorted(keep)
    share = len(keep) / len(B0)
    n1 = int(y[keep].sum())
    n0 = len(keep) - n1
    r0 = rng.permutation(np.where(y == 0)[0])[:n0]
    r1 = rng.permutation(np.where(y == 1)[0])[:n1]
    rand = sorted(list(r0) + list(r1))
    G = [B0[i]["persons"] for i in range(len(B0))]
    res = dict(n_full=len(B0), n_matched=len(keep), share_kept=share, strata={str(s): (int(sum(1 for i, t in enumerate(strata) if t == s and y[i] == 0)), int(sum(1 for i, t in enumerate(strata) if t == s and y[i] == 1))) for s in sorted(set(strata))})
    for name, idx in (("full", list(range(len(B0)))), ("matched", keep), ("random", rand)):
        idx = np.array(idx)
        res[f"nuisance_auc_{name}"] = oof_auc(Xn[idx], y[idx], [G[i] for i in idx])
        Xf, _ = design([B0[i] for i in idx], cues, True)
        res[f"full_cue_auc_{name}"] = oof_auc(Xf, y[idx], [G[i] for i in idx])
    # heads on CLIP features
    fidx, F, _ = K.load_features("clip224")
    have = [r for r in cat if r["id"] in fidx]
    P = RD.pools(have)
    heads = {}
    for name, idx in (("full", list(range(len(B0)))), ("matched", keep), ("random", rand)):
        rows = [B0[i] for i in idx if B0[i]["id"] in fidx]
        yy = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
        h = K.fit_head(F[[fidx[r["id"]] for r in rows]], yy, [r["persons"] for r in rows], 401)
        ids = list(fidx)
        S = dict(zip(ids, K.head_score(h, F[[fidx[i] for i in ids]]).tolist()))
        cam = [S[r["id"]] for p in RD.CAMERA for r in P.get(p, [])]
        t5 = K.thr_at(cam)
        fr = {p: float(np.mean([S[r["id"]] > t5 for r in P[p]])) for p in ("T_R0", "T_R0_61", "T_R0_112") if P.get(p)}
        heads[name] = dict(n_train=len(rows), C=h["C"], thr5=t5, flag=fr,
                           dflag_61=fr.get("T_R0_61", np.nan) - fr.get("T_R0", np.nan),
                           dflag_112=fr.get("T_R0_112", np.nan) - fr.get("T_R0", np.nan),
                           auc_R4_vs_R3=RD.paired(S, P, "T_R4_opencv", "T_R3_opencv").get("auc"),
                           eer_R4_vs_R0=K.eer(RD.scores_of(S, P["T_R4_opencv"]), RD.scores_of(S, P["T_R0"])))
    res["heads"] = heads
    na = res["nuisance_auc_matched"]
    na_val = na.get("auc_max") or 1.0
    full_d = heads["full"]["dflag_61"]
    res["kill"] = dict(
        k1=bool(not (na_val <= 0.60 and share >= 0.30)),
        k2=("no flag-rate change to remove" if not full_d > 0 else
            bool((heads["random"]["dflag_61"] - heads["matched"]["dflag_61"]) < 0.5 * full_d)),
        k3=bool(heads["matched"]["eer_R4_vs_R0"] - heads["random"]["eer_R4_vs_R0"] > 2.0))
    return res


def main(which):
    OUTD.mkdir(parents=True, exist_ok=True)
    import tier0 as T0
    cat = K.catalog()
    cat += T0.soft_cat_rows({r["id"] for r in cat})
    cues = load_cues("c224")
    out = {}
    if which == "tier0":
        sets = T0.train_sets(cat)
        for arm, rows in sets.items():
            rows, _ = T0.balance_rows([r for r in rows if r["id"] in cues])
            out[f"train_{arm}"] = certify(rows, cues)
            out[f"train_{arm}"]["missing_cues"] = sum(1 for r in rows if r["id"] not in cues)
        P = RD.pools([r for r in cat if r["id"] in cues])
        for a, b in cells(P):
            rows = P[a] + P[b]
            out[f"cell {a} vs {b}"] = dict(with_categorical=certify(rows, cues, True),
                                           pixel_only=certify(rows, cues, False))
        out["matched_subsample"] = matched_test(cat, cues, sets)
        K.dump(out, OUTD / "cert_tier0.json")
    else:
        import mkmanifests as MM  # noqa: F401
        byid = {r["id"]: r for r in cat}
        for name in ("A", "B", "Bn", "C"):
            f = K.PN1 / "manifests" / f"train_{name}.csv"
            if not f.exists():
                continue
            rows = []
            for r in csv.DictReader(open(f)):       # rows as trained (with the balance repetition)
                base = r["id"]
                jp = ""
                for q in ("jpeg90", "jpeg70"):
                    if base.endswith("_" + q):
                        base, jp = base[: -len(q) - 1], q
                src = byid.get(base)
                if src is None and base.startswith("sm1h_"):
                    pid = base[5:].rsplit("_", 1)[0].replace("_", ":", 1)
                    lad, _ = K.split_tables()
                    src = dict(id=base, fam="ladder", klass="single", rung="halfA", tool="opencv", strength="",
                               pool="ladder_" + pid.split(":")[0], persons=(pid, lad[pid]["partner_B"]))
                x = dict(src, id=r["id"], jpeg=jp, klass="attack" if r["label"] == "1" else "negative")
                rows.append(x)
            out[f"manifest_{name}"] = certify(rows, cues)
            out[f"manifest_{name}"]["missing_cues"] = sum(1 for r in rows if r["id"] not in cues)
        K.dump(out, OUTD / "cert_tier1.json")
    print("DONE", which)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main(sys.argv[1])

"""FZ1 P2 (gate G-c): cross-validated logistic probes on frozen features; also the probe routine reused by P4.

  fz1_probe.py [--smoke] [--jobs 5]
Reads /mnt/t7/smad_next/FZ1/feats/<backbone>/{a43,sg3}.npz; writes experiments/FZ1/p2_probe.json (+ .csv) and the
out-of-fold probabilities to /mnt/t7/smad_next/FZ1/probe_oof.npz.
Run: OMP_NUM_THREADS=1 .../python -I src/FZ1/fz1_probe.py --run <backbone> [--jobs N]  (per backbone), then --aggregate
"""
import csv, json, pathlib, sys, warnings
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz1_common as K

CGRID = (1e-3, 1e-2, 1e-1, 1.0, 10.0)
BACKBONES = ("clip_mad", "clip_native", "dinov3", "dinov2")
A43_C = (("B20", "D20"), ("B", "D"), ("C20", "D20"), ("B20", "C20"))
SG3_C = (("morph", "render"), ("morph", "spread"))
L2 = {"clip_mad": True, "clip_native": True, "dinov3": False, "dinov2": False}


def _auc(p, y):
    return K.auc(p[y == 1], p[y == 0])


def fit_predict(Xtr, ytr, gtr, Xte):
    """StandardScaler + L2 logistic; C by 3-fold grouped CV inside the training part (max AUC, ties -> smaller C)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    mk = lambda c: make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=5000))  # noqa: E731
    best, bestc = -1, None
    gkf = GroupKFold(n_splits=3)
    for c in CGRID:
        oof = np.zeros(len(ytr))
        for tr, va in gkf.split(Xtr, ytr, gtr):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                oof[va] = mk(c).fit(Xtr[tr], ytr[tr]).predict_proba(Xtr[va])[:, 1]
        a = _auc(oof, ytr)
        if a > best + 1e-12:
            best, bestc = a, c
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return mk(bestc).fit(Xtr, ytr).predict_proba(Xte)[:, 1], bestc


def person_folds(persons, seed, k=5):
    per = sorted(set(persons))
    perm = np.random.default_rng(seed).permutation(len(per))
    return {per[j]: int(r % k) for r, j in enumerate(perm)}


def cv_a43(X, y, P, seed):
    """P: person tuples (host first). Test = host in fold; train = no person in fold. -> oof probs, chosen Cs."""
    fold = person_folds([p for t in P for p in t], seed)
    oof = np.full(len(y), np.nan)
    cs = []
    host = np.array([fold[t[0]] for t in P])
    for k in range(5):
        te = np.where(host == k)[0]
        if len(te) == 0:
            continue
        tr = np.array([i for i, t in enumerate(P) if all(fold[p] != k for p in t)])
        oof[te], c = fit_predict(X[tr], y[tr], np.array([P[i][0] for i in tr]), X[te])
        cs.append(c)
    assert not np.isnan(oof).any()
    return oof, cs


def cv_pairs(X, y, pairs, seed):
    fold = person_folds(list(pairs), seed)
    f = np.array([fold[p] for p in pairs])
    oof = np.full(len(y), np.nan)
    cs = []
    for k in range(5):
        te, tr = np.where(f == k)[0], np.where(f != k)[0]
        if len(te) == 0:
            continue
        oof[te], c = fit_predict(X[tr], y[tr], np.array(pairs)[tr], X[te])
        cs.append(c)
    return oof, cs


def load(backbone, set_name):
    z = np.load(K.BIG / "feats" / backbone / f"{set_name}.npz", allow_pickle=False)
    X = z["feat"].astype(np.float64)
    if L2[backbone]:
        X = X / np.linalg.norm(X, axis=1, keepdims=True)
    return dict(zip(z["id"].tolist(), range(len(X)))), X


def reading(a, lo):
    if a >= 0.75 and lo > 0.65:
        r = "readable from frozen features"
    elif a < 0.60:
        r = "not readable by this probe"
    else:
        r = "intermediate"
    gc = "below the G-c 0.65 bar" if a < 0.65 else "at or above the G-c 0.65 bar"
    return r, gc


def job(args):
    kind, backbone, a, b, seed, smoke = args
    import fz1_eval as E  # noqa: F401
    if kind == "a43":
        rows = K.a43_rows()
        g = K.a43_groups(rows)
        idx, X = load(backbone, "a43")
        ii = g[a] + g[b]
        if smoke:
            ii = g[a][:20] + g[b][:20]
        y = np.r_[np.ones(len(g[a][:20] if smoke else g[a])), np.zeros(len(g[b][:20] if smoke else g[b]))].astype(int)
        P = [K.pers_a43(rows[i]) for i in ii]
        Xs = X[[idx[rows[i]["id"]] for i in ii]]
        oof, cs = cv_a43(Xs, y, P, seed)
        return dict(kind=kind, backbone=backbone, contrast=f"{a} vs {b}", seed=seed, oof=oof.tolist(), y=y.tolist(),
                    persons=[list(t) for t in P], cs=cs, ids=[rows[i]["id"] for i in ii])
    R4, R2, RX = K.sg3_rows()
    grp = {"morph": R4, "render": R2, "spread": RX}
    idx, X = load(backbone, "sg3")
    ra, rb = grp[a], grp[b]
    if smoke:
        ra, rb = ra[:20], rb[:20]
    rr = ra + rb
    y = np.r_[np.ones(len(ra)), np.zeros(len(rb))].astype(int)
    pairs = [int(r["pair"]) for r in rr]
    oof, cs = cv_pairs(X[[idx[r["id"]] for r in rr]], y, pairs, seed)
    return dict(kind=kind, backbone=backbone, contrast=f"{a} vs {b}", seed=seed, oof=oof.tolist(), y=y.tolist(),
                pairs=pairs, cs=cs, ids=[r["id"] for r in rr])


def main():
    smoke = "--smoke" in sys.argv
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 5
    seeds = (401,) if smoke else (401, 402, 403, 404, 405)
    if "--run" in sys.argv:                    # compute one backbone's probes and cache the raw out-of-fold results
        bb = sys.argv[sys.argv.index("--run") + 1]
        tasks = [("a43", bb, a, b, s, smoke) for a, b in A43_C for s in seeds] + \
                [("sg3", bb, a, b, s, smoke) for a, b in SG3_C for s in seeds]
        if jobs == 1:                          # inline: one process in total
            res = [job(t) for t in tasks]
        else:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=jobs) as ex:
                res = list(ex.map(job, tasks))
        if not smoke:
            json.dump(res, open(K.BIG / f"probe_raw_{bb}.json", "w"))
            return
    else:                                      # --aggregate: every cached backbone
        res = [r for bb in BACKBONES if (K.BIG / f"probe_raw_{bb}.json").exists()
               for r in json.load(open(K.BIG / f"probe_raw_{bb}.json"))]
    rows = K.a43_rows()
    allp = sorted({p for r in rows for p in K.pers_a43(r)})
    D = K.Draw(allp, 200 if smoke else 10000, K.SEED_A43)
    R4, R2, RX = K.sg3_rows()
    pairs_all = sorted({int(r["pair"]) for r in R4 + R2 + RX})
    ppos = {p: i for i, p in enumerate(pairs_all)}
    Wp = np.random.default_rng(K.SEED_SG3).multinomial(len(pairs_all), np.full(len(pairs_all), 1 / len(pairs_all)),
                                                       size=200 if smoke else 10000).astype(float)
    out, table, oofs = {}, [], {}
    for r in res:
        oof, y = np.array(r["oof"]), np.array(r["y"])
        key = f"{r['backbone']}|{r['contrast']}"
        if r["kind"] == "a43":
            w = D.w([tuple(t) for t in r["persons"]])
        else:
            w = Wp[:, [ppos[p] for p in r["pairs"]]]
        point = _auc(oof, y)
        d = out.setdefault(key, {"backbone": r["backbone"], "contrast": r["contrast"], "set": r["kind"], "seeds": {}})
        d["seeds"][r["seed"]] = {"auc": point, "Cs": r["cs"]}
        if r["seed"] == 401:
            rep = K.wauc(oof[y == 1], oof[y == 0], w[:, y == 1], w[:, y == 0])
            lo, hi = K.ci(rep)
            d.update(auc=point, ci=[lo, hi], n=[int(y.sum()), int((1 - y).sum())])
            d["reading"], d["gc_audit_plan"] = reading(point, lo)
            oofs[key] = np.c_[oof, y]
            oofs[key + "|ids"] = np.array(r["ids"])
            if r["kind"] == "a43":
                d["_rep"] = rep  # kept for P4 paired differences (dropped before json)
    for key, d in out.items():
        sa = [v["auc"] for v in d["seeds"].values()]
        d["fold_seed_range"] = [min(sa), max(sa)]
        table.append([d["backbone"], d["contrast"], f"{d['auc']:.3f}", f"{d['ci'][0]:.3f}", f"{d['ci'][1]:.3f}",
                      f"{min(sa):.3f}", f"{max(sa):.3f}", d["reading"], d["gc_audit_plan"]])
        print(f"{d['backbone']:12s} {d['contrast']:18s} {d['auc']:.3f} [{d['ci'][0]:.3f}, {d['ci'][1]:.3f}] "
              f"fold seeds {min(sa):.3f}-{max(sa):.3f}  {d['reading']}  Cs(401)={d['seeds'][401]['Cs']}")
    if smoke:
        return
    np.savez(K.BIG / "probe_oof.npz", **{k.replace("|", "__").replace(" ", "_"): v for k, v in oofs.items()})
    reps = {k: d.pop("_rep") for k, d in out.items() if "_rep" in d}
    np.savez(K.BIG / "probe_reps_a43.npz", **{k.replace("|", "__").replace(" ", "_"): v for k, v in reps.items()})
    json.dump(out, open(K.OUT / "p2_probe.json", "w"), indent=1)
    with open(K.OUT / "p2_probe.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["backbone", "contrast", "auc_seed401", "ci_lo", "ci_hi", "fold_seed_min", "fold_seed_max", "reading", "gc_audit_plan"])
        w.writerows(table)


if __name__ == "__main__":
    main()

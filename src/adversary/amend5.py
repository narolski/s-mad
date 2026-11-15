"""ADV amendment 5: lcomb_smatch, sel360 within-D floor, per-row same-data learner scores (train_Sb, train_SbFM).
No network score is read. python3 -I amend5.py"""
import csv
import json
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import feats as F  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

CLEAN = "/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv"
CLEAN_SHA = "814c44861d706553bd827e5dd5634817ee289c0b12bc45a553c5d759b8362358"


def heldout(name):
    return list(csv.DictReader(open(RF.FDIR / f"{name}_heldout.csv")))


def smatch():
    R = list(csv.DictReader(open(RF.FDIR / "lcomb_regional_heldout.csv")))
    ids = [r["id"] for r in R]
    y = np.array([int(r["label"]) for r in R])
    s = np.clip(np.array([float(r["surround_gbt"]) for r in R]), 1e-6, 1 - 1e-6)
    z = np.log(s / (1 - s))
    sd = z.std()
    rng = np.random.default_rng(20261117)
    free = set(np.where(y == 0)[0].tolist())
    pairs = []
    for i in rng.permutation(np.where(y == 1)[0]):
        if not free:
            break
        cand = np.array(sorted(free))
        d = np.abs(z[cand] - z[i]) / sd
        j = int(np.argmin(d))
        if d[j] <= 0.1:
            pairs.append((int(i), int(cand[j])))
            free.discard(int(cand[j]))
    rows = [(ids[a], 1, q) for q, (a, b) in enumerate(pairs)] + [(ids[b], 0, q) for q, (a, b) in enumerate(pairs)]
    with open(RF.FDIR / "lcomb_smatch_rows.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "label", "pair"])
        w.writerows(rows)
    want = {i for i, _, _ in rows}
    rl = [r for r in C.build("lcomb") if r[0] in want]
    yy = np.array([l for _, _, l, _ in rl])
    pers = [p for *_, p in rl]
    X, nm = RF.X_of(rl)
    rg = RF.regmap()
    Rg = np.stack([rg[p] for _, p, _, _ in rl])
    sets = {"surround": Rg[:, [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("SURR:")]],
            "face": Rg[:, [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("FACE:")]],
            "file": X[:, [i for i, n in enumerate(nm) if n in RF.FILE_SIZE]], "all_cue": X}
    g = FL.components(pers)
    fl = FL.folds(yy, g)
    diag = {}
    for k, Xs in sets.items():
        diag[k] = {m: FL.auc(FL.crossfit(Xs, yy, g, m, fl)[0], yy) for m in ("single", "logreg", "gbt")}
    rep = dict(product="lcomb_smatch", n_pairs=len(pairs), rule="1:1 greedy on logit(surround_gbt), caliper 0.1 SD, "
               "default_rng(20261117)", known_limit="surround-balanced only", balance_refit=diag)
    (RF.FDIR / "lcomb_smatch_build.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep), flush=True)
    return want


def sel360():
    import hashlib
    assert hashlib.sha256(open(CLEAN, "rb").read()).hexdigest() == CLEAN_SHA
    clean = {r["host"] for r in csv.DictReader(open(CLEAN))}
    man = {r["id"]: r for r in C.rows(C.AB1X)}
    R = heldout("ri_R4_vs_R3")
    keep = [r for r in R if man[r["id"]]["role"] == "dev" or man[r["id"]]["host"] in clean]
    ids = [r["id"] for r in keep]
    y = np.array([int(r["label"]) for r in keep])
    g = np.array([int(r["component"]) for r in keep])
    sc = {m: np.array([float(r[m]) for r in keep]) for m in ("single", "logreg", "gbt")}
    with open(RF.FDIR / "sel360_rows.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "label", "component", "host", "role"])
        for r in keep:
            w.writerow([r["id"], r["label"], r["component"], man[r["id"]]["host"], man[r["id"]]["role"]])
    point = RF.within_d(ids, y, sc, rows_d=True)
    rng = np.random.default_rng(20261119)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    draws = {m: [] for m in sc}
    for _ in range(2000):
        ii = np.concatenate([idx[k] for k in rng.choice(ug, len(ug), replace=True)])
        b = RF.within_d([ids[i] for i in ii], y[ii], {m: v[ii] for m, v in sc.items()}, rows_d=True)
        for m in sc:
            if b and b.get(m) is not None:
                draws[m].append(b[m])
    ci = {m: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for m, v in draws.items() if v}
    rep = dict(product="sel360", n_rows=len(keep), n_pos=int(y.sum()), n_components=int(len(ug)),
               within_D=point, ci=ci, note="quintile edges over these rows; bootstrap unit = component column; "
               "edges are recomputed in each draw (BD1's rule applied to the drawn rows)")
    (RF.FDIR / "sel360_withinD.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep), flush=True)
    return ids


def transfer_rows(arms, smatch_ids, sel_ids):
    lc = {r["id"]: int(r["component"]) for r in heldout("lcomb")}
    ri = {r["id"]: int(r["component"]) for r in heldout("ri_R4_vs_R3")}
    sets = {"lcomb": [r for r in C.build("lcomb")],
            "sel360": [r for r in C.build("ri_R4_vs_R3") if r[0] in set(sel_ids)],
            "lcomb_smatch": [r for r in C.build("lcomb") if r[0] in smatch_ids]}
    comp = {"lcomb": lc, "sel360": ri, "lcomb_smatch": lc}
    for arm in arms:
        T = C.train_rows(arm)
        rl = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.train_persons(r)) for r in T]
        X, nm = RF.X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        Xc, _, keep = FL._clean(X, X[:1])
        med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0)
        models = {k: FL._model(k).fit(Xc, y) for k in ("logreg", "gbt")}
        out = []
        summ = {}
        for sname, rows_ in sets.items():
            Z, _ = RF.X_of(rows_)
            Z = np.where(np.isfinite(Z), Z, med)[:, keep]
            lr = models["logreg"].decision_function(Z)
            gb = models["gbt"].predict_proba(Z)[:, 1]
            yy = np.array([l for _, _, l, _ in rows_])
            summ[sname] = dict(n=len(rows_), logreg=FL.auc(lr, yy), gbt=FL.auc(gb, yy))
            for k, (i, _, l, _) in enumerate(rows_):
                out.append([sname, i, l, comp[sname][i], repr(float(lr[k])), repr(float(gb[k]))])
        with open(RF.FDIR / f"transfer_{arm}_rows.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["set", "id", "label", "component", "logreg", "gbt"])
            w.writerows(out)
        print(arm, json.dumps(summ), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    sm = smatch()
    sel = sel360()
    transfer_rows(["Sb", "SbFM"], sm, sel)

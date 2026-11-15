"""FZ1 post hoc addendum A1 (a) and (b): the reviewer's checks with the registered person bootstrap, and simple-statistic
floors for B20 vs C20 and C20 vs D20. Registered in experiments/FZ1/prereg.md ("Post hoc addendum A1").

Run: OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_addendum.py [--smoke]
Writes experiments/FZ1/addendum_a1.json and /mnt/t7/smad_next/FZ1/addendum_a1_stats_CC20.npz.
"""
import json, os, pathlib, sys, warnings
import numpy as np
from scipy.stats import rankdata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
import fz1_common as K
import fz1_probe as PR
import fz1_stats as ST

SMOKE = "--smoke" in sys.argv
B, BR = (200, 100) if SMOKE else (10000, 2000)
SEEDS = ("401", "402", "403", "404", "405")


def ci(x):
    return K.ci(x)


def fmt(p, c):
    return f"{p:.3f} [{c[0]:.3f}, {c[1]:.3f}]"


def wspearman(x, y, w):
    """Spearman on the sample in which each item is repeated w times (integer person-bootstrap weights)."""
    k = np.round(w).astype(int)
    if k.sum() < 3:
        return np.nan
    xx, yy = np.repeat(x, k), np.repeat(y, k)
    rx, ry = rankdata(xx), rankdata(yy)
    if rx.std() == 0 or ry.std() == 0:
        return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])


def fit_model(Xtr, ytr, gtr):
    """The registered P2 routine (fz1_probe.fit_predict) returning the fitted pipeline."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    mk = lambda c: make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=5000))  # noqa: E731
    best, bestc = -1, None
    for c in PR.CGRID:
        oof = np.zeros(len(ytr))
        for tr, va in GroupKFold(n_splits=3).split(Xtr, ytr, gtr):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                oof[va] = mk(c).fit(Xtr[tr], ytr[tr]).predict_proba(Xtr[va])[:, 1]
        a = K.auc(oof[ytr == 1], oof[ytr == 0])
        if a > best + 1e-12:
            best, bestc = a, c
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return mk(bestc).fit(Xtr, ytr), bestc


def main():
    rows = K.a43_rows()
    g = K.a43_groups(rows)
    allp = sorted({p for r in rows for p in K.pers_a43(r)})
    D = K.Draw(allp, B, K.SEED_A43)
    P = {i: K.pers_a43(rows[i]) for a in ("B", "B20", "C", "C20", "D", "D20", "E") for i in g[a]}
    W = lambda ii: D.w([P[i] for i in ii])  # noqa: E731
    H = np.load(K.BIG / "heads/scores_a43.npz")
    hid = {k: i for i, k in enumerate(H["id"].tolist())}
    head = {s: np.array([H[f"s{s}_a43"][hid[r["id"]]] for r in rows]) for s in SEEDS}
    out = {"B": B, "B_corr": BR, "smoke": SMOKE}

    def auc_ci(ia, ib, s):
        rep = K.wauc(s[ia], s[ib], W(ia), W(ib))
        return K.auc(s[ia], s[ib]), ci(rep), rep

    # ---------------- (a1) within-arm Spearman with PNG bytes and centre-256 Laplacian variance
    S4 = np.load(K.BIG / "p4_stats_values.npz")
    sid = {k: i for i, k in enumerate(S4["ids"].tolist())}
    a1 = {}
    for a in ("B", "D", "B20", "D20"):
        ii = g[a]
        png = np.array([float(rows[i]["file_bytes"]) for i in ii])
        lap = np.array([S4["center256"][sid[rows[i]["id"]], 1] for i in ii])
        w = W(ii)[:BR]
        d = {}
        for nm, x in (("png_bytes", png), ("lap_center256", lap)):
            pts = {s: wspearman(head[s][ii], x, np.ones(len(ii))) for s in SEEDS}
            rep = np.array([wspearman(head["401"][ii], x, w[b]) for b in range(w.shape[0])])
            d[nm] = {"rho_s401": pts["401"], "ci_s401": ci(rep[~np.isnan(rep)]), "rho_range_5_seeds": [min(pts.values()), max(pts.values())]}
        a1[a] = d
        print(f"(a1) {a}: rho(head,png) {fmt(d['png_bytes']['rho_s401'], d['png_bytes']['ci_s401'])}; rho(head,lap) {fmt(d['lap_center256']['rho_s401'], d['lap_center256']['ci_s401'])}", flush=True)
    out["a1_within_arm_spearman"] = a1

    # ---------------- (a2) PNG-size-stratified AUC
    a2 = {}
    for x, y in (("B", "D"), ("B20", "D20")):
        ia, ib = np.array(g[x]), np.array(g[y])
        pa = np.array([float(rows[i]["file_bytes"]) for i in ia])
        pb = np.array([float(rows[i]["file_bytes"]) for i in ib])
        edges = np.quantile(np.r_[pa, pb], [0, .2, .4, .6, .8, 1])
        wa, wb = W(list(ia)), W(list(ib))
        res = {"png_auc_morph_higher": K.auc(pa, pb), "strata": []}
        for s in SEEDS:
            num = np.zeros(wa.shape[0]); den = np.zeros(wa.shape[0]); num1 = den1 = 0.0
            for q in range(5):
                lo, hi = edges[q], edges[q + 1] + (1 if q == 4 else 0)
                ma, mb = (pa >= lo) & (pa < hi), (pb >= lo) & (pb < hi)
                if ma.sum() == 0 or mb.sum() == 0:
                    continue
                sa, sb = head[s][ia[ma]], head[s][ib[mb]]
                r = K.wauc(sa, sb, wa[:, ma], wb[:, mb])
                mass = wa[:, ma].sum(1) * wb[:, mb].sum(1)
                num += r * mass; den += mass
                a_pt = K.auc(sa, sb); num1 += a_pt * ma.sum() * mb.sum(); den1 += ma.sum() * mb.sum()
                if s == "401":
                    res["strata"].append({"q": q, "nB": int(ma.sum()), "nD": int(mb.sum()), "auc_s401": a_pt})
            rep = num / np.maximum(den, 1e-12)
            res[f"stratified_auc_s{s}"] = num1 / den1
            if s == "401":
                res["stratified_ci_s401"] = ci(rep)
                res["overall_s401"] = K.auc(head[s][ia], head[s][ib])
        a2[f"{x} vs {y}"] = res
        print(f"(a2) {x} vs {y}: png AUC {res['png_auc_morph_higher']:.3f}; head s401 overall {res['overall_s401']:.3f}, within PNG fifths {fmt(res['stratified_auc_s401'], res['stratified_ci_s401'])}", flush=True)
    out["a2_png_stratified"] = a2

    # ---------------- (a3) partner split of the clip_mad P2 probe (fold seed 401)
    O = np.load(K.BIG / "probe_oof.npz")
    byid = {r["id"]: i for i, r in enumerate(rows)}
    a3 = {}
    for c in ("B20_vs_D20", "B_vs_D", "B20_vs_C20"):
        oo = O[f"clip_mad__{c}"]
        ids = O[f"clip_mad__{c}__ids"].tolist()
        ii = [byid[i] for i in ids]
        pp = [P[i] for i in ii]
        fold = PR.person_folds([p for t in pp for p in t], 401)
        p, y = oo[:, 0], oo[:, 1].astype(int)
        two = np.array([len(t) == 2 and t[0] != t[1] for t in pp])
        same = np.array([two[k] and fold[pp[k][0]] == fold[pp[k][1]] for k in range(len(pp))])
        w = D.w(pp)
        neg = y == 0
        m1, m2 = (y == 1) & same, (y == 1) & two & ~same
        r1 = K.wauc(p[m1], p[neg], w[:, m1], w[:, neg]); r2 = K.wauc(p[m2], p[neg], w[:, m2], w[:, neg])
        a3[c] = {"partner_same_fold": {"n": int(m1.sum()), "auc": K.auc(p[m1], p[neg]), "ci": ci(r1)},
                 "partner_in_training": {"n": int(m2.sum()), "auc": K.auc(p[m2], p[neg]), "ci": ci(r2)},
                 "difference_same_minus_training": {"point": K.auc(p[m1], p[neg]) - K.auc(p[m2], p[neg]), "ci": ci(r1 - r2)}}
        print(f"(a3) {c}: same fold n={m1.sum()} {fmt(a3[c]['partner_same_fold']['auc'], a3[c]['partner_same_fold']['ci'])} | partner in training n={m2.sum()} {fmt(a3[c]['partner_in_training']['auc'], a3[c]['partner_in_training']['ci'])}", flush=True)
    out["a3_partner_split"] = a3

    # ---------------- (a4) transfer matrix (registered P2 routine), clip_mad and dinov2; (a5-probe) expression on B20-vs-C20 probe
    TRAIN = [("B20", "D20"), ("C20", "D20"), ("B20", "C20"), ("B", "D"), ("C", "D")]
    TEST = [("B20", "D20"), ("C20", "D20"), ("B20", "C20"), ("B", "D"), ("C", "D"), ("B", "C"), ("E", "D20"), ("E", "D")]
    arms = sorted({a for t in TEST for a in t})
    fold = PR.person_folds(sorted({p for i in P for p in P[i]}), 401)
    a4, probe_scores = {}, {}
    for bb in ("clip_mad", "dinov2"):
        idx, X = PR.load(bb, "a43")
        xi = lambda i: idx[rows[i]["id"]]  # noqa: E731
        for tp, tn in TRAIN:
            sc, cs = {}, []
            for k in range(5):
                tri = [i for i in g[tp] + g[tn] if all(fold[p] != k for p in P[i])]
                y = np.array([1 if i in set(g[tp]) else 0 for i in tri])
                m, c = fit_model(X[[xi(i) for i in tri]], y, np.array([P[i][0] for i in tri]))
                cs.append(c)
                for a in arms:
                    te = [i for i in g[a] if fold[P[i][0]] == k]
                    if te:
                        dfun = m.decision_function(X[[xi(i) for i in te]])
                        for i, v in zip(te, dfun):
                            sc[i] = v
            s = np.full(len(rows), np.nan)
            for i, v in sc.items():
                s[i] = v
            key = f"{bb}|train {tp} vs {tn}"
            a4[key] = {"Cs": cs}
            line = []
            for a, b2 in TEST:
                pt, cc, _ = auc_ci(g[a], g[b2], s)
                a4[key][f"{a} vs {b2}"] = {"auc": pt, "ci": cc}
                line.append(f"{a} vs {b2} {pt:.3f}")
            print(f"(a4) {key}: " + "; ".join(line), flush=True)
            probe_scores[key] = s
    out["a4_transfer"] = a4

    # ---------------- (a5) expression split: heads and the clip_mad B20-vs-C20 probe direction
    ex = lambda a, e: [i for i in g[a] if rows[i]["expr"] == e]  # noqa: E731
    a5 = {"heads": {}, "probe_clip_mad_B20_vs_C20": {}}
    pairs = [("B20[03]", ex("B20", "03"), "C20", g["C20"]), ("B20[08]", ex("B20", "08"), "C20", g["C20"]),
             ("B[03]", ex("B", "03"), "C", g["C"]), ("B[08]", ex("B", "08"), "C", g["C"]),
             ("C20", g["C20"], "D20[03]", ex("D20", "03")), ("C20", g["C20"], "D20[08]", ex("D20", "08")),
             ("C", g["C"], "D[03]", ex("D", "03")), ("C", g["C"], "D[08]", ex("D", "08")),
             ("D20[03]", ex("D20", "03"), "D20[08]", ex("D20", "08")), ("D[03]", ex("D", "03"), "D[08]", ex("D", "08"))]
    for la, ia, lb, ib in pairs:
        pt, cc, _ = auc_ci(ia, ib, head["401"])
        rng = [K.auc(head[s][ia], head[s][ib]) for s in SEEDS]
        a5["heads"][f"{la} vs {lb}"] = {"auc_s401": pt, "ci": cc, "range_5_seeds": [min(rng), max(rng)], "n": [len(ia), len(ib)]}
        print(f"(a5) head {la} vs {lb}: {fmt(pt, cc)}", flush=True)
    sp = probe_scores["clip_mad|train B20 vs C20"]
    # E needs scores from that probe: E was scored (arm list) only as part of TEST arms -> yes ("E" in arms)
    for la, ia, lb, ib in [("B20[03]", ex("B20", "03"), "C20", g["C20"]), ("B20[08]", ex("B20", "08"), "C20", g["C20"]),
                           ("D20[08]", ex("D20", "08"), "D20[03]", ex("D20", "03")), ("E[08]", ex("E", "08"), "E[03]", ex("E", "03"))]:
        pt, cc, _ = auc_ci(ia, ib, sp)
        a5["probe_clip_mad_B20_vs_C20"][f"{la} vs {lb}"] = {"auc": pt, "ci": cc, "n": [len(ia), len(ib)]}
        print(f"(a5) probe B20-vs-C20 direction {la} vs {lb}: {fmt(pt, cc)}", flush=True)
    out["a5_expression"] = a5

    # ---------------- (b) floors for B20 vs C20, C20 vs D20 (B vs C, C vs D descriptive)
    from common import ImageItems  # noqa: E402
    need = [i for a in ("C", "C20") for i in g[a]]
    ds224 = ImageItems([(str(K.a43_path(rows[i])), 0) for i in need], res=224, root="/")
    ds512 = ImageItems([(str(K.a43_path(rows[i])), 0) for i in need], res=512, root="/")
    stat = {"view224": {}, "center256": {}}
    for k, i in enumerate(need):
        r = rows[i]
        sz = os.path.getsize(K.A43_ROOT / r["stored_path"])
        assert sz == int(r["file_bytes"])
        stat["view224"][i] = ST.stats(ds224[k][0].permute(1, 2, 0).numpy() * 255.0, sz)
        stat["center256"][i] = ST.stats((ds512[k][0].permute(1, 2, 0).numpy() * 255.0)[128:384, 128:384], sz)
    for a in ("B", "B20", "D", "D20"):
        for i in g[a]:
            stat["view224"][i] = list(S4["view224"][sid[rows[i]["id"]]])
            stat["center256"][i] = list(S4["center256"][sid[rows[i]["id"]]])
    np.savez(K.BIG / ("addendum_a1_stats_CC20_smoke.npz" if SMOKE else "addendum_a1_stats_CC20.npz"),
             ids=np.array([rows[i]["id"] for i in need]), view224=np.array([stat["view224"][i] for i in need]),
             center256=np.array([stat["center256"][i] for i in need]))
    preps = np.load(K.BIG / "probe_reps_a43.npz")
    p2 = json.load(open(K.OUT / "p2_probe.json"))
    bres = {}
    for a, b2 in (("B20", "C20"), ("C20", "D20"), ("B", "C"), ("C", "D")):
        ia, ib = g[a], g[b2]
        wa, wb = W(ia), W(ib)
        hp, hc, hrep = auc_ci(ia, ib, head["401"])
        res = {"head_s401": {"auc": hp, "ci": hc, "range_5_seeds": [min(K.auc(head[s][ia], head[s][ib]) for s in SEEDS), max(K.auc(head[s][ia], head[s][ib]) for s in SEEDS)]}}
        pkey = f"clip_mad__{a}_vs_{b2}"
        if pkey in preps.files and not SMOKE:
            res["probe_clip_mad"] = {"auc": p2[f"clip_mad|{a} vs {b2}"]["auc"], "ci": p2[f"clip_mad|{a} vs {b2}"]["ci"]}
        for view in ("view224", "center256"):
            Xa = np.array([stat[view][i] for i in ia]); Xb = np.array([stat[view][i] for i in ib])
            vres, best = {}, (None, -1, None)
            for j, nm in enumerate(ST.NAMES):
                raw = K.auc(Xa[:, j], Xb[:, j]); rep = K.wauc(Xa[:, j], Xb[:, j], wa, wb)
                flip = raw < 0.5
                fa, frep = (1 - raw, 1 - rep) if flip else (raw, rep)
                vres[nm] = {"auc_folded": fa, "ci_folded": ci(frep), "direction": f"{a} lower" if flip else f"{a} higher"}
                if fa > best[1]:
                    best = (nm, fa, frep)
            Xall = np.r_[Xa, Xb]; y = np.r_[np.ones(len(ia)), np.zeros(len(ib))].astype(int)
            oof, cs = PR.cv_a43(Xall, y, [P[i] for i in ia + ib], 401)
            lrep = K.wauc(oof[y == 1], oof[y == 0], wa, wb)
            vres["logistic_all7"] = {"auc": K.auc(oof[y == 1], oof[y == 0]), "ci": ci(lrep), "Cs": cs}
            vres["best_single"] = best[0]
            vres["head_minus_best_single"] = {"point": hp - best[1], "ci": ci(hrep - best[2])}
            vres["head_exceeds_floor"] = bool(ci(hrep - best[2])[0] > 0)
            vres["head_minus_logistic"] = {"point": hp - vres["logistic_all7"]["auc"], "ci": ci(hrep - lrep)}
            if pkey in preps.files and not SMOKE:
                vres["probe_minus_best_single"] = {"point": res["probe_clip_mad"]["auc"] - best[1], "ci": ci(preps[pkey] - best[2])}
            res[view] = vres
            print(f"(b) {view} {a} vs {b2}: head {fmt(hp, hc)}; best single {best[0]} {best[1]:.3f}; head-minus-best "
                  f"{vres['head_minus_best_single']['point']:+.3f} [{vres['head_minus_best_single']['ci'][0]:+.3f}, {vres['head_minus_best_single']['ci'][1]:+.3f}]; "
                  f"logistic7 {fmt(vres['logistic_all7']['auc'], vres['logistic_all7']['ci'])}", flush=True)
        bres[f"{a} vs {b2}"] = res
    out["b_floors"] = bres
    if not SMOKE:
        json.dump(out, open(K.OUT / "addendum_a1.json", "w"), indent=1)


if __name__ == "__main__":
    main()

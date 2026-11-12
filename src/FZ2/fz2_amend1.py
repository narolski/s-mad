"""FZ2 amendment 1 (registered in commit dbc151d before this ran; post hoc in substance). Measurement only.
(i) H-A transfer + theta / Laplacian strata; (ii) H-B residual + simple floors for every add-on contrast; (iii) H-C on
FZ1's A43 frames; (iv) P_XS trained on DG1 applied to A43 frames. -> experiments/FZ2_.../amend1.json
Run: OMP_NUM_THREADS=2 nice -n 10 .venv-spark/bin/python -I src/FZ2/fz2_amend1.py [--smoke]
"""
import csv, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz2_read as R2  # noqa: E402  (also puts src/AR1 and src/FZ1 on the path)
import fz1_common as K1  # noqa: E402

SMOKE = "--smoke" in sys.argv
OUT = R2.OUTX / ("amend1_smoke.json" if SMOKE else "amend1.json")
ci = R2.ci


def fmt(x):
    return f"{x['auc']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}]"


def theta_map():
    th = {}
    for k in range(8):
        f = R2.DG1 / "gen" / f"addon_s{k}" / f"out_addon_s{k}" / f"addon_s{k}" / "gen_rows.csv"
        for r in csv.DictReader(open(f)):
            th[(f"addon_s{k}", r["pool"], r["name"])] = float(r["theta_xT"]) if r["theta_xT"] not in ("", "nan") else float("nan")
    return th


def hb_feats(path):
    import cv2
    import stats as ST
    import swap as SWM
    img = cv2.imread(path)
    m = np.zeros(img.shape[:2], bool)
    m[R2.BOX] = True
    Y = ST.M.luminance(img[..., ::-1])
    L = cv2.Laplacian(Y, cv2.CV_64F)
    simple = [float(L[m].var() / max(L[~m].var(), 1e-12)), float(L[m].var())] + list(SWM.seam(img, m))[:3]
    simple += [float(b) for b in ST.M.band_shares(ST.M.power_profile(Y)[0])]
    dx, dy = np.diff(Y, axis=1), np.diff(Y, axis=0)
    mx, my = m[:, 1:] & m[:, :-1], m[1:, :] & m[:-1, :]
    nr = []
    for d, mm in ((dx, mx), (dy, my)):
        for reg in (mm, ~mm):
            v = d[reg]
            v0 = v - v.mean(); var = (v0 ** 2).mean()
            nr += [float(v.std()), float(np.abs(v).mean()), float((v0 ** 4).mean() / max(var * var, 1e-12))]
    return np.array(simple, np.float64), np.array(nr, np.float64)


def strat_auc(Rd, s, ix, isame, cov):
    """Pooled-fifth stratified pair-weighted AUC of s on X (ix) vs SAME (isame) by covariate cov; bootstrap."""
    ix, isame = np.array(ix), np.array(isame)
    pooled = np.r_[cov[ix], cov[isame]]
    edges = np.quantile(pooled, [0, .2, .4, .6, .8, 1])
    wx, ws = Rd.W(list(ix)), Rd.W(list(isame))
    num = np.zeros(wx.shape[0]); den = np.zeros(wx.shape[0]); n1 = d1 = 0.0; strata = []
    for q in range(5):
        lo, hi = edges[q], edges[q + 1] + (1e-9 if q == 4 else 0)
        mx, ms = (cov[ix] >= lo) & (cov[ix] < hi), (cov[isame] >= lo) & (cov[isame] < hi)
        st = {"q": q, "nX": int(mx.sum()), "nSAME": int(ms.sum())}
        if mx.sum() and ms.sum():
            r = K1.wauc(s[ix[mx]], s[isame[ms]], wx[:, mx], ws[:, ms]); mass = wx[:, mx].sum(1) * ws[:, ms].sum(1)
            num += r * mass; den += mass
            a = K1.auc(s[ix[mx]], s[isame[ms]]); n1 += a * mx.sum() * ms.sum(); d1 += mx.sum() * ms.sum(); st["auc"] = a
        strata.append(st)
    rep = num / np.maximum(den, 1e-12)
    a0, rep0 = Rd.auc(s, list(ix), list(isame))
    ok = den > 0
    return {"A0": a0, "A_s": n1 / d1, "A_s_ci": ci(rep[ok]), "delta": a0 - n1 / d1, "delta_ci": ci((rep0 - rep)[ok]),
            "usable_strata": int(sum("auc" in t for t in strata)), "strata": strata}


def main():
    from scipy.stats import spearmanr
    B = 300 if SMOKE else 10000
    items, F, pool = R2.load_items("addon", pathlib.Path("/mnt/t7/smad_next/FZ2/results/dgx/out"), SMOKE)
    R2.add_input_columns(items, pool)
    R2.add_baselines(items, 1)
    th = theta_map()
    for it in items:
        it["theta"] = th.get((it["list"], it["pool"], it["id"].split("/")[-1]), float("nan"))
    Rd = R2.Reader(items, F, B)
    H = R2.heads(F["clip_mad"])
    have = lambda *ks: all(k in Rd.byk for k in ks)  # noqa: E731
    lap = np.array([it["lapvar_box"] for it in items]); theta = np.array([it["theta"] for it in items])
    out = {"B": B, "smoke": SMOKE, "registered_in": "dbc151d"}
    # ---------------- (i)
    ia = {}
    ix, isame = Rd.idx("X20"), Rd.idx("SAME20")
    for b in R2.BB:
        X = F[b]
        p_xs, cs = Rd.probe(X, "X20", "SAME20", ["NOISEX20", "NOISES20", "SEMX20", "SEMS20", "REC20", "FRESH1_20", "MIR20"])
        d_sr, _ = Rd.probe(X, "SAME20", "REC20", ["NOISEX20", "NOISES20", "SEMX20", "SEMS20", "X20"])
        d = {"Cs_P_XS": cs}
        for nm, s in (("P_XS", p_xs), ("D_SR", d_sr)):
            for pos, neg in (("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20"), ("X20", "SAME20"), ("NOISES20", "REC20"),
                             ("NOISEX20", "REC20"), ("SEMS20", "REC20"), ("SEMX20", "REC20")):
                pt, rep = Rd.auc(s, Rd.idx(pos), Rd.idx(neg))
                d[f"{nm} {pos} vs {neg}"] = {"auc": pt, "ci": ci(rep)}
            d[f"{nm} mean score"] = {k: float(np.mean(s[Rd.idx(k)])) for k in
                                     ("X20", "SAME20", "NOISEX20", "NOISES20", "SEMX20", "SEMS20", "REC20", "FRESH1_20", "MIR20") if have(k)}
        d["P_XS strat theta"] = strat_auc(Rd, p_xs, ix, isame, theta)
        d["P_XS strat laplacian"] = strat_auc(Rd, p_xs, ix, isame, lap)
        d["spearman P_XS vs theta"] = {k: float(spearmanr(p_xs[Rd.idx(k)], theta[Rd.idx(k)])[0]) for k in ("X20", "SAME20")}
        d["spearman P_XS vs laplacian"] = {k: float(spearmanr(p_xs[Rd.idx(k)], lap[Rd.idx(k)])[0]) for k in ("X20", "SAME20")}
        ia[b] = d
        print(b, "P_XS NOISEX vs NOISES", fmt(d["P_XS NOISEX20 vs NOISES20"]), "SEMX vs SEMS", fmt(d["P_XS SEMX20 vs SEMS20"]),
              "theta strat", round(d["P_XS strat theta"]["A_s"], 3), "lap strat", round(d["P_XS strat laplacian"]["A_s"], 3), flush=True)
    pt, rep = Rd.auc(theta, ix, isame)
    ia["theta alone X vs SAME"] = {"auc": pt, "ci": ci(rep), "median": {"X20": float(np.nanmedian(theta[ix])), "SAME20": float(np.nanmedian(theta[isame]))}}
    for k in ("NOISEX20", "NOISES20", "SEMX20", "SEMS20"):
        if have(k):
            ia[f"theta median {k}"] = float(np.nanmedian(theta[Rd.idx(k)]))
    ia["spearman theta vs laplacian"] = {k: float(spearmanr(theta[Rd.idx(k)], lap[Rd.idx(k)])[0]) for k in ("X20", "SAME20", "NOISEX20", "NOISES20", "SEMX20", "SEMS20") if have(k)}
    c = ia["clip_mad"]; nx, sx = c["P_XS NOISEX20 vs NOISES20"], c["P_XS SEMX20 vs SEMS20"]
    sup = nx["auc"] >= 0.90 and nx["ci"][0] >= 0.85 and sx["auc"] <= 0.65 and sx["ci"][1] <= 0.70
    fal = nx["auc"] <= 0.65 or sx["auc"] >= 0.85
    ia["reading_HA_transfer"] = "supported" if sup else ("falsified" if fal else "not decided")
    out["i_HA"] = ia
    print("H-A transfer:", ia["reading_HA_transfer"], "theta alone", fmt(ia["theta alone X vs SAME"]), flush=True)
    # ---------------- (ii) H-B floors
    from multiprocessing import Pool
    with Pool(2) as pl:
        hb = pl.map(hb_feats, [it["path"] for it in items], chunksize=32)
    S10 = np.array([h[0] for h in hb]); R12 = np.array([h[1] for h in hb])
    contrasts = [("SAME20", "REC20"), ("FRESH1_20", "REC20"), ("FRESH2_20", "REC20"), ("X20", "REC20"), ("X20", "SAME20"),
                 ("SAME20", "FRESH1_20"), ("X20", "FRESH1_20"), ("NOISES20", "REC20"), ("SEMS20", "REC20"), ("NOISEX20", "REC20"),
                 ("SEMX20", "REC20"), ("NOISES20", "SEMS20"), ("MIR20", "REC20"), ("FRESH1_20", "FRESH2_20"),
                 ("SAME100", "REC100"), ("FRESH1_100", "REC100"), ("SAME100", "FRESH1_100"), ("X100", "SAME100")]
    hbres = {}
    for pos, neg in contrasts:
        if not have(pos, neg):
            continue
        ipos, ineg = Rd.idx(pos), Rd.idx(neg)
        fl, reps = {}, {}
        for j in range(S10.shape[1]):
            pt, rep = Rd.auc(S10[:, j], ipos, ineg)
            if pt < 0.5:
                pt, rep = 1 - pt, 1 - rep
            fl[f"simple{j}"] = pt; reps[f"simple{j}"] = rep
        bs = max(fl, key=fl.get)
        row = {"best_single": {"name": bs, "auc": fl[bs], "ci": ci(reps[bs])}}
        for nm, Xf in (("residual12", R12), ("simple10", S10), ("combined22", np.c_[S10, R12])):
            s, cs = Rd.probe(Xf, pos, neg)
            pt, rep = Rd.auc(s, ipos, ineg)
            row[nm] = {"auc": pt, "ci": ci(rep)}; reps[nm] = rep
        cand = {"best_single": (fl[bs], reps[bs]), **{nm: (row[nm]["auc"], reps[nm]) for nm in ("residual12", "simple10", "combined22")}}
        fname = max(cand, key=lambda k: cand[k][0])
        row["floor"] = {"name": fname, "auc": cand[fname][0]}
        exc = {}
        for b in R2.BB:
            s, _ = Rd.probe(F[b], pos, neg)
            pt, rep = Rd.auc(s, ipos, ineg)
            exc[f"probe_{b}"] = {"auc": pt, "ci": ci(rep), "excess": pt - cand[fname][0], "excess_ci": ci(rep - cand[fname][1])}
        pt, rep = Rd.auc(H["smdd_s401"], ipos, ineg)
        exc["head_s401"] = {"auc": pt, "ci": ci(rep), "excess": pt - cand[fname][0], "excess_ci": ci(rep - cand[fname][1])}
        row["excess"] = exc
        hbres[f"{pos} vs {neg}"] = row
        print("H-B", pos, neg, "residual12", fmt(row["residual12"]), "floor", fname, round(cand[fname][0], 3),
              "clip excess", round(exc["probe_clip_mad"]["excess"], 3), flush=True)
    r1, r2 = hbres["NOISES20 vs REC20"]["residual12"]["auc"], hbres["FRESH1_20 vs REC20"]["residual12"]["auc"]
    hbres["reading_HB"] = "supported" if (r1 >= 0.95 and r2 >= 0.95) else ("falsified" if (r1 <= 0.85 and r2 <= 0.85) else "not decided")
    out["ii_HB"] = hbres
    print("H-B:", hbres["reading_HB"], flush=True)
    # ---------------- (iii) H-C on A43 frames, (iv) P_XS on A43
    rows = K1.a43_rows(); g = K1.a43_groups(rows)
    allp = sorted({p for r in rows for p in K1.pers_a43(r)})
    D = K1.Draw(allp, B, K1.SEED_A43)
    Hz = np.load(K1.BIG / "heads/scores_a43.npz"); hid = {k: i for i, k in enumerate(Hz["id"].tolist())}
    h = np.array([Hz["s401_a43"][hid[r["id"]]] for r in rows])
    lapA = np.full(len(rows), np.nan)
    for f in ("p4_stats_values.npz", "addendum_a1_stats_CC20.npz"):
        z = np.load(K1.BIG / f); idl = z["ids"].tolist()
        pos_ = {r["id"]: i for i, r in enumerate(rows)}
        for j, i in enumerate(idl):
            lapA[pos_[i]] = z["center256"][j, 1]
    ixa, isa = np.array(g["B20"]), np.array(g["C20"])
    wx, ws = D.w([K1.pers_a43(rows[i]) for i in ixa]), D.w([K1.pers_a43(rows[i]) for i in isa])
    pooled = np.r_[lapA[ixa], lapA[isa]]; edges = np.quantile(pooled, [0, .2, .4, .6, .8, 1])
    num = np.zeros(B); den = np.zeros(B); n1 = d1 = 0.0; strata = []
    for q in range(5):
        lo, hi = edges[q], edges[q + 1] + (1e-9 if q == 4 else 0)
        mx, ms = (lapA[ixa] >= lo) & (lapA[ixa] < hi), (lapA[isa] >= lo) & (lapA[isa] < hi)
        st = {"q": q, "nB20": int(mx.sum()), "nC20": int(ms.sum())}
        if mx.sum() and ms.sum():
            r = K1.wauc(h[ixa[mx]], h[isa[ms]], wx[:, mx], ws[:, ms]); mass = wx[:, mx].sum(1) * ws[:, ms].sum(1)
            num += r * mass; den += mass; a = K1.auc(h[ixa[mx]], h[isa[ms]]); n1 += a * mx.sum() * ms.sum(); d1 += mx.sum() * ms.sum()
            st["auc"] = a
        strata.append(st)
    As = n1 / d1; ok = den > 0
    hc = {"A0": K1.auc(h[ixa], h[isa]), "A_s": As, "A_s_ci": ci((num / np.maximum(den, 1e-12))[ok]), "strata": strata,
          "usable_strata": int(sum("auc" in t for t in strata))}
    hc["reading_HC"] = "supported" if As <= 0.62 else ("falsified" if As >= 0.65 else "not decided")
    out["iii_HC"] = hc
    print("H-C:", round(hc["A0"], 3), "->", round(As, 3), hc["reading_HC"], flush=True)
    iv = {}
    tr = np.array(ix + isame); y = np.r_[np.ones(len(ix)), np.zeros(len(isame))].astype(int)
    for b in R2.BB:
        model, c = R2.fit_model(F[b][tr], y, Rd.cyc[tr])
        z = np.load(K1.BIG / "feats" / b / "a43.npz"); fid = {k: i for i, k in enumerate(z["id"].tolist())}
        XA = z["feat"].astype(np.float64)[[fid[r["id"]] for r in rows]]
        s = model.decision_function(XA)
        d = {"C": c}
        for pa, na in (("B20", "C20"), ("B", "C"), ("C20", "D20"), ("B20", "D20"), ("B", "D")):
            ia_, ib_ = g[pa], g[na]
            rep = K1.wauc(s[ia_], s[ib_], D.w([K1.pers_a43(rows[i]) for i in ia_]), D.w([K1.pers_a43(rows[i]) for i in ib_]))
            d[f"{pa} vs {na}"] = {"auc": K1.auc(s[ia_], s[ib_]), "ci": ci(rep)}
        d["mean score"] = {a: float(np.mean(s[g[a]])) for a in ("A", "B", "B20", "C", "C20", "D", "D20", "E", "R0")}
        iv[b] = d
        print("iv", b, {k: round(v["auc"], 3) for k, v in d.items() if isinstance(v, dict) and "auc" in v}, flush=True)
    out["iv_PXS_on_A43"] = iv
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()

"""Fixed-threshold re-read (EV1), Part A: false alarms on processed genuine photos at one fixed threshold, misses at
the native and worst-pool thresholds, the crossed morph-variant x genuine-variant table, and the ranking check.
Run: python3 -I src/EV1/ev1_partA.py [--smoke]
"""
import csv, json, sys, time, pathlib
import numpy as np
from scipy.stats import kendalltau

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
ALPHAS = (0.05, 0.10)
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def cell_label(mv, gv):
    if mv == "orig" and gv == "orig":
        return "native"
    if mv == gv:
        return "matched"
    if mv == "orig" and gv == "resmatch":
        return "E7-matched"
    q = lambda v: int(v[4:]) if v.startswith("jpeg") else None  # noqa: E731
    if mv == "orig":
        return "G>M (genuine more processed)"
    if gv in ("orig", "resmatch"):
        return "M>G (morph more processed)"
    if q(mv) is not None and q(gv) is not None:
        return "G>M (genuine more processed)" if q(gv) < q(mv) else "M>G (morph more processed)"
    return "mixed"


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    cut = (lambda a: a[:8]) if SMOKE else (lambda a: a)
    # ------------------------------------------------------------------ pools (FRLL genuine) and families
    pools = {f"FRLL {v}": I.bona("frll_bona", v) for v in K.GVARS}
    pools["FRLL orig, DiM copy"] = I.bona("dim_bona")
    pools["FRLL orig, MorDIFF alignment"] = I.bona("mordiff_bona")
    for f in K.FAMS:
        pools[f"resmatch {f}"] = I.resmatch(f)
    pools = {k: cut(v) for k, v in pools.items()}
    gated = ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL resample50", "FRLL orig, DiM copy",
             "FRLL orig, MorDIFF alignment"] + [f"resmatch {f}" for f in K.FAMS]
    fams = {f: cut(I.morph(f)) for f in K.FAMS}
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    assert len(allp) == 102, len(allp)
    D = K.Draw(allp, B, K.SEED)
    Wp0 = {k: D.w([rows[i]["pers"] for i in v]) for k, v in pools.items()}
    Wf0 = {f: D.w([rows[i]["pers"] for i in v]) for f, v in fams.items()}
    # crossed table: the 300 morphs present in every variant (FRLL-Morphs), matched by stem
    cross_m = {}
    for f in K.FRLLM:
        by = {v: {rows[i]["stem"]: i for i in I.morph(f, v)} for v in K.GVARS}
        common = sorted(set.intersection(*[set(by[v]) for v in K.GVARS if v != "orig"]))
        assert len(common) == 300 and set(common) <= set(by["orig"])
        common = cut(common)
        cross_m[f] = {v: np.array([by[v][s] for s in common]) for v in K.GVARS}
    Wc0 = {f: D.w([rows[i]["pers"] for i in cross_m[f]["orig"]]) for f in K.FRLLM}
    # other photo sources
    G = K.gtest_rows()
    gid = [r["id"] for r in G]
    fei = {"FEI neutral": [i for i, r in enumerate(G) if r["family"] == "fei_bona_neutral"],
           "FEI smiling": [i for i, r in enumerate(G) if r["family"] == "fei_bona_smiling"]}
    fei["FEI all"] = fei["FEI neutral"] + fei["FEI smiling"]
    fei = {k: np.array(cut(v)) for k, v in fei.items()}
    DF = K.Draw(sorted({G[i]["subj"] for v in fei.values() for i in v}), B, K.SEED)
    Wfei0 = {k: DF.w([(G[i]["subj"],) for i in v]) for k, v in fei.items()}
    FQ = K.ffhqm_rows()
    fid = [r["id"] for r in FQ]
    ffq = {"FFHQ orig": [i for i, r in enumerate(FQ) if r["family"] == "ffhq_bona"]}
    for fam in ("landmark_complete", "landmark_combined", "stylegan_w", "stylegan_wplus", "diffae"):
        ffq[f"FFHQ resmatch {fam}"] = [i for i, r in enumerate(FQ) if r["family"] == fam and r["label"] == "0"]
    ffq = {k: np.array(cut(v)) for k, v in ffq.items()}

    dets = K.detectors()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing",
                                                 "MADation ViT-B/16 dnorm (diagnostic variant)")] + \
               [d for d in dets if d.get("method") == "M3L"][:1] + [d for d in dets if d["block"] == "other recipe"][:1]
    FA, MISS, FM, CROSS, META = [], [], [], [], {}
    for det in dets:
        boot = det["block"] != "other recipe"          # descriptive block: point estimates only
        one = lambda Wd: Wd if boot else {k: v[:1] for k, v in Wd.items()}  # noqa: E731
        Wp, Wf, Wc, Wfei = one(Wp0), one(Wf0), one(Wc0), one(Wfei0)
        Bd = next(iter(Wp.values())).shape[0]
        cif = K.ci if boot else (lambda r: ["", ""])  # noqa: E731
        s, key = K.load_scores(det, "eval", ids)
        sg, _ = K.load_scores(det, "gtest", gid)
        sf, _ = K.load_scores(det, "ffhqm", fid)
        dev = s[I.devbona()]
        dev = dev[np.isfinite(dev)]
        fallback = len(dev) == 0
        meta = {"block": det["block"], "key": key, "n_devbona": int(len(dev)),
                "threshold_source": "frll_bona orig (test-fitted fallback: no devbona row)" if fallback else "devbona"}
        # native D-EER per family (cell's own genuine pool)
        meta["native_eer"] = {}
        for f in K.FAMS:
            b = s[cut(I.bona(K.NATIVE_BONA[f]))]
            m = s[fams[f]]
            meta["native_eer"][f] = K.eer_fast(b, m)[0] if np.isfinite(b).all() and np.isfinite(m).all() else None
        meta["auc_native"] = {f: K.auc(s[fams[f]], s[cut(I.bona(K.NATIVE_BONA[f]))]) for f in K.FAMS}
        for a in ALPHAS:
            t = K.thr_at(s[pools["FRLL orig"]], a) if fallback else K.thr_at(dev, a)
            src_pool = s[pools["FRLL orig"]] if fallback else dev
            meta[f"t_{a}"] = t
            meta[f"dev_fa_{a}"] = K.flag_rate(src_pool, t)
            meta[f"n_tied_at_t_{a}"] = int((src_pool == t).sum())
            # (1) false alarms
            for k, ix in pools.items():
                x = s[ix]
                if not np.isfinite(x).all():
                    FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), "not scored", "", ""])
                    continue
                pt = K.flag_rate(x, t)
                lo, hi = cif(K.flag_rate(x, t, Wp[k]))
                FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), pt, lo, hi])
            for k, ix in fei.items():
                if sg is None:
                    FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), "not scored", "", ""])
                    continue
                x = sg[ix]
                pt = K.flag_rate(x, t)
                lo, hi = cif(K.flag_rate(x, t, Wfei[k]))
                FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), pt, lo, hi])
            for k, ix in ffq.items():
                if sf is None:
                    FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), "not scored", "", ""])
                    continue
                x = sf[ix]
                kk = int((x > t).sum())
                lo, hi = K.cp(kk, len(x))
                FA.append([det["name"], det["block"], a, meta["threshold_source"], key, t, k, len(ix), kk / len(x), lo, hi])
            # (2) worst-pool threshold (recomputed per replicate)
            avail = [k for k in gated if np.isfinite(s[pools[k]]).all()]
            meta[f"gated_available_{a}"] = avail
            tp = {k: K.thr_at(s[pools[k]], a) for k in avail}
            tpr = {k: K.thr_at(s[pools[k]], a, Wp[k]) for k in avail}
            t_wp = max([t] + list(tp.values()))
            t_wpr = np.max(np.vstack([np.full(Bd, t)] + [tpr[k] for k in avail]), 0)
            meta[f"t_wp_{a}"] = t_wp
            meta[f"wp_binding_pool_{a}"] = max(tp, key=tp.get) if tp and max(tp.values()) > t else "devbona / fit pool"
            meta[f"fa_at_wp_{a}"] = {k: K.flag_rate(s[pools[k]], t_wp) for k in pools if np.isfinite(s[pools[k]]).all()}
            nat, wpm, fwm = {}, {}, {}
            for f in K.FAMS:
                m = s[fams[f]]
                for lab, tt, ttr in (("native", t, None), ("worst-pool", t_wp, t_wpr)):
                    pt = float((m <= tt).mean())
                    rep = 1 - K.flag_rate(m, ttr if ttr is not None else tt, Wf[f])
                    MISS.append([det["name"], det["block"], a, lab, tt, f, len(m), pt, *cif(rep)])
                    (nat if lab == "native" else wpm)[f] = pt
                # per-family worst-pool (secondary)
                own = [k for k in ("FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL resample50", f"resmatch {f}") if k in avail]
                if f == "mordiff" and "FRLL orig, MorDIFF alignment" in avail:
                    own.append("FRLL orig, MorDIFF alignment")
                tf = max([t] + [tp[k] for k in own])
                tfr = np.max(np.vstack([np.full(Bd, t)] + [tpr[k] for k in own]), 0)
                pt = float((m <= tf).mean())
                MISS.append([det["name"], det["block"], a, "family worst-pool", tf, f, len(m), pt, *cif(1 - K.flag_rate(m, tfr, Wf[f]))])
                fwm[f] = pt
            grp = lambda d, fs: float(np.mean([d[x] for x in fs]))  # noqa: E731
            eers = [meta["native_eer"][f] for f in K.FAMS]
            FM.append([det["name"], det["block"], a, t, t_wp, meta[f"wp_binding_pool_{a}"],
                       float(np.mean(eers)) if None not in eers else "",
                       grp(nat, K.FAMS), grp(wpm, K.FAMS), grp(wpm, K.FAMS) - grp(nat, K.FAMS), grp(fwm, K.FAMS),
                       grp(nat, K.LANDMARK), grp(wpm, K.LANDMARK), nat["stylegan"], wpm["stylegan"],
                       grp(nat, ("mordiff",) + K.DIM), grp(wpm, ("mordiff",) + K.DIM)])
        # (3) crossed table at 5%
        for f in K.FAMS:
            gvs = list(K.GVARS) + ["resmatch"] + (["MorDIFF alignment"] if f == "mordiff" else [])
            mvs = list(K.GVARS) if f in K.FRLLM else ["orig"]
            t5 = meta["t_0.05"]
            for gv in gvs:
                gk = f"FRLL {gv}" if gv in K.GVARS else f"resmatch {f}" if gv == "resmatch" else "FRLL orig, MorDIFF alignment"
                g = s[pools[gk]]
                if not np.isfinite(g).all():
                    continue
                tc, tcr = K.thr_at(g, 0.05), K.thr_at(g, 0.05, Wp[gk])
                for mv in mvs:
                    if f in K.FRLLM:
                        mi, Wm = cross_m[f][mv], Wc[f]
                    else:
                        mi, Wm = fams[f], Wf[f]
                    m = s[mi]
                    if not np.isfinite(m).all():
                        continue
                    pt = K.auc(m, g)
                    rep = K.wauc(m, g, Wm, Wp[gk])
                    mc = float((m <= tc).mean())
                    mcr = 1 - K.flag_rate(m, tcr, Wm)
                    CROSS.append([det["name"], det["block"], f, mv, gv, cell_label(mv, "orig" if gv == "MorDIFF alignment" else gv),
                                  len(m), len(g), pt, *cif(rep), mc, *cif(mcr), float((m <= t5).mean()), K.flag_rate(g, t5)])
        META[det["name"]] = meta
        log(det["name"], key, "t5", round(meta["t_0.05"], 4), "FA jpeg70",
            [round(x[8], 3) for x in FA if x[0] == det["name"] and x[2] == 0.05 and x[6] == "FRLL jpeg70" and x[8] != "not scored"])
    # ------------------------------------------------------------------ (4) ranking
    rank = {}
    rel = [d["name"] for d in dets if d["kind"] == "rel"]
    for a in ALPHAS:
        fm = {r[0]: r for r in FM if r[2] == a}
        rows12, x, y = [], [], []
        for n in rel:
            if fm[n][6] != "":
                rows12.append(n); x.append(fm[n][6]); y.append(fm[n][8])
        for meth in ("M3", "M3L"):
            ns = [d["name"] for d in dets if d.get("method") == meth]
            if ns:
                rows12.append(f"{meth} (seed mean of {len(ns)})")
                x.append(float(np.mean([fm[n][6] for n in ns]))); y.append(float(np.mean([fm[n][8] for n in ns])))
        tau = kendalltau(x, y)
        n23 = rel + [d["name"] for d in dets if d.get("method") in ("M3", "M3L")]
        x23 = [fm[n][6] for n in n23 if fm[n][6] != ""]
        y23 = [fm[n][8] for n in n23 if fm[n][6] != ""]
        tau23 = kendalltau(x23, y23)
        rises = {n: fm[n][9] for n in n23}
        rank[str(a)] = {"rows": rows12, "native_family_mean_eer": x, "worst_pool_family_mean_miss": y,
                        "kendall_tau_b": float(tau.statistic), "p": float(tau.pvalue),
                        "kendall_tau_b_23rows": float(tau23.statistic), "p_23rows": float(tau23.pvalue),
                        "rise_native_to_worst_pool_points": {n: 100 * v for n, v in rises.items()},
                        "max_rise_points": 100 * max(rises.values()),
                        "n_rise_ge_20_points": int(sum(v >= 0.20 for v in rises.values()))}
        cond_tau, cond_rise = tau.statistic >= 0.8, all(v < 0.20 for v in rises.values())
        rank[str(a)]["falsifier"] = ("metric dropped" if (cond_tau and cond_rise) else "metric kept") + \
            f" (tau {tau.statistic:.3f} {'>=' if cond_tau else '<'} 0.8; max rise {100 * max(rises.values()):.1f} points)"
    # networks that would fail the 'own detector' bar (FA > 10% on any gated pool at the native 5% threshold)
    bar = {}
    for det in dets:
        bad = [r[6] for r in FA if r[0] == det["name"] and r[2] == 0.05 and r[6] in gated and r[8] != "not scored" and r[8] > 0.10]
        bar[det["name"]] = bad
    rank["own_detector_bar_failures"] = {k: v for k, v in bar.items() if v}
    log("ranking", {a: rank[a]["falsifier"] for a in ("0.05", "0.1")})
    if SMOKE:
        print("smoke ok")
        return
    out = K.OUT
    with open(out / "A1_false_alarms.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "block", "alpha", "threshold_source", "score_key", "threshold", "pool", "n", "false_alarm", "lo95", "hi95"])
        w.writerows(FA)
    with open(out / "A2_miss.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "block", "alpha", "threshold_type", "threshold", "family", "n", "miss", "lo95", "hi95"])
        w.writerows(MISS)
    with open(out / "A2_family_means.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "block", "alpha", "t_native", "t_worst_pool", "binding_pool", "native_family_mean_eer_pct",
                    "native_family_mean_miss", "worst_pool_family_mean_miss", "rise", "family_worst_pool_mean_miss",
                    "landmark_native", "landmark_worst_pool", "stylegan_native", "stylegan_worst_pool",
                    "diffusion_native", "diffusion_worst_pool"])
        w.writerows(FM)
    with open(out / "A3_crossed.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "block", "family", "morph_variant", "genuine_variant", "cell_label", "n_morph", "n_genuine",
                    "auc", "auc_lo95", "auc_hi95", "miss_at_cell_5pct", "miss_lo95", "miss_hi95",
                    "margin_miss_at_t5_native", "margin_fa_at_t5_native"])
        w.writerows(CROSS)
    json.dump({"B": B, "seed": K.SEED, "meta": META, "ranking": rank, "gated_pools": gated}, open(out / "A_partA.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()

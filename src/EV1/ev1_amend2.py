"""Fixed-threshold re-read (EV1), Amendment 2 (independent review of 11 Nov): B1 flag rates at each release's own 0.5
rule; B2 paired logit shifts and a saturation descriptor; B3 miss rate with the threshold pool as a column; B4 the
border-matched pairing for the MorDIFF frame; B5 the paired FFHQ block. Existing scores only; needs
/mnt/t7/smad_next/EV1/border_e5e7.npz (ev1_border.py) for B4. Run: nice -n 10 python3 -I src/EV1/ev1_amend2.py [--smoke]
"""
import csv, json, re, sys, time, pathlib
import numpy as np
from scipy.stats import binomtest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ev1_common as K  # noqa: E402
import ev1_amend as AM  # noqa: E402  (paths and loaders of amendment 1)

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
FULL100 = ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL resample50"] + [f"E7 {f}" for f in K.FRLLM]
FFQ = ("landmark_complete", "landmark_combined", "stylegan_w", "stylegan_wplus", "diffae")


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def lg(p):
    p = np.clip(np.asarray(p, float), 1e-7, 1 - 1e-7)
    return np.log(p / (1 - p))


def wquant(x, W, q):
    """weighted quantile per replicate row of W."""
    o = np.argsort(x)
    xs, Ws = x[o], W[:, o]
    c = np.cumsum(Ws, 1)
    j = (c < q * c[:, -1:]).sum(1)
    return xs[np.minimum(j, len(x) - 1)]


def cpr(k, n):
    return K.cp(int(k), int(n)) if n else [None, None]


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    meta = json.load(open(K.OUT / "A_partA.json"))["meta"]
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    pidx = {p: j for j, p in enumerate(D.per)}
    stem6 = lambda i: rows[i]["name"][:6]  # noqa: E731
    pools = {f"FRLL {v}": I.bona("frll_bona", v) for v in K.GVARS}
    pools["FRLL orig, MorDIFF alignment"] = I.bona("mordiff_bona")
    pools["FRLL orig, DiM copy"] = I.bona("dim_bona")
    for f in K.FAMS:
        pools[f"E7 {f}"] = I.resmatch(f)
    gated = ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL resample50", "FRLL orig, DiM copy",
             "FRLL orig, MorDIFF alignment"] + [f"E7 {f}" for f in K.FAMS]
    pstem = {k: [stem6(i) for i in v] for k, v in pools.items()}
    pied = {k: float(np.median([float(rows[i]["ied"]) for i in v])) for k, v in pools.items()}
    pied["devbona"] = float(np.median([float(rows[i]["ied"]) for i in I.devbona()]))
    fams = {f: I.morph(f) for f in K.FAMS}
    fied = {f: float(np.median([float(rows[i]["ied"]) for i in v])) for f, v in fams.items()}
    # effective inter-eye distance of the history: eval.csv keeps the photo's native IED for every FRLL-derived pool, so
    # E7 pools take their morph family's median native IED (the prep_eval resmatch target) and resample50 half the original
    for f in K.FAMS:
        pied[f"E7 {f}"] = fied[f]
    pied["FRLL resample50"] = 0.5 * pied["FRLL orig"]
    Wf = {f: D.w([rows[i]["pers"] for i in v]) for f, v in fams.items()}
    Wp = {k: D.w([rows[i]["pers"] for i in v]) for k, v in pools.items()}
    # external sets
    a43 = list(csv.DictReader(open(AM.A43MAN)))
    a43_sha = K.sha(AM.A43MAN)
    a43ids = [r["id"] for r in a43]
    ARMS = {a: [i for i, r in enumerate(a43) if r["source"] == "a43" and r["arm"] == a] for a in ("E", "D", "D20", "C", "C20", "A", "B", "B20")}
    E_st = [a43[i]["src_a"] for i in ARMS["E"]]
    E_border = float(np.median([float(a43[i]["border_frac"]) for i in ARMS["E"]]))
    E_ied = float(np.median([float(a43[i]["ied"]) for i in ARMS["E"]]))
    h3 = list(csv.DictReader(open(AM.H3MAN))); h3ids = [r["id"] for r in h3]; h3_sha = K.sha(AM.H3MAN)
    h3m = [i for i, r in enumerate(h3) if r["family"] == "h3_sg3" and r["variant"] == "orig"]
    h3b = [i for i, r in enumerate(h3) if r["family"] == "h3_bona" and r["variant"] == "orig"]
    sp = list(csv.DictReader(open(AM.SPMAN))); spids = [r["id"] for r in sp]; sp_sha = K.sha(AM.SPMAN)
    spr = [i for i, r in enumerate(sp) if r["variant"] == "orig"]
    G = K.gtest_rows(); gid = [r["id"] for r in G]
    FQ = K.ffhqm_rows(); fid = [r["id"] for r in FQ]
    fqst = lambda r: re.sub(r"_(orig|resmatch.*)$", "", pathlib.PurePath(r["path"]).stem)  # noqa: E731
    fq_o = {fqst(r): i for i, r in enumerate(FQ) if r["family"] == "ffhq_bona"}
    fq_e = {fam: [(i, fq_o[fqst(r)]) for i, r in enumerate(FQ) if r["family"] == fam and r["label"] == "0"] for fam in FFQ}
    fq_mied = {fam: float(np.median([float(r["ied"]) for r in FQ if r["family"] == fam and r["label"] == "1"])) for fam in FFQ}
    # border of the E5 / E7 frames (B4)
    bz = np.load(K.BIG / ("border_e5e7_smoke.npz" if SMOKE else "border_e5e7.npz"), allow_pickle=False)
    bmap = dict(zip(bz["id"].tolist(), bz["zero_frac"].astype(float)))
    F = np.load(K.BIG / "feat.npz", allow_pickle=False)
    fz = {str(p)[str(p).find("eval/"):]: float(v) for p, v in zip(F["al_path"], F["al_zero"]) if "eval/" in str(p)}
    pborder = {k: (float(np.median([bmap[rows[i]["id"]] for i in v if rows[i]["id"] in bmap])) if any(rows[i]["id"] in bmap for i in v) else None)
               for k, v in pools.items()}
    fborder = {f: float(np.median([fz[rows[i]["path"]] for i in v])) for f, v in fams.items()}
    log("pool IED", {k: round(v, 1) for k, v in pied.items()}, "border", {k: v if v is None else round(v, 3) for k, v in pborder.items()})
    dets = [d for d in K.detectors() if d["block"] in ("release", "M3", "M3L")]
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "MADation ViT-B/16 release", "SelfMAD release, own preprocessing")] + \
               [d for d in dets if d.get("method") == "M3"][:1]
    R1, R2, RS, R3, R3S, R4, R4A, R5 = [], [], [], [], [], [], [], []
    for det in dets:
        nm, blk = det["name"], det["block"]
        rel = det["kind"] == "rel"
        own = det["kind"] == "own"
        s, key = K.load_scores(det, "eval", ids)                       # Part A key (logit for releases)
        # probability for the 0.5 rule
        if rel:
            z = K.load_npz(det["dir"] / "scores_eval.npz")
            pm = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(float)))
            prob = np.array([pm.get(i, np.nan) for i in ids])
            lgt = s
            ok = np.isfinite(prob)
            agree = float(np.mean((prob[ok] > 0.5) == (lgt[ok] > 0)))
        else:
            prob = s
            lgt = lg(s)
            agree = None
        pkey = "score_noTTA" if rel else "score"
        t5 = meta[nm]["t_0.05"]
        tl5 = t5 if rel else float(lg(t5))                              # devbona (or fallback) threshold on the logit scale
        # external probabilities and logits
        pa, ph, px = AM.ext_paths(nm) if blk == "release" else (None, None, None)
        ea = AM.load_ext(pa, a43ids, pkey, a43_sha) if pa else None
        eal = (AM.load_ext(pa, a43ids, "logit_noTTA", a43_sha) if rel else (lg(ea) if ea is not None else None)) if pa else None
        eh = AM.load_ext(ph, h3ids, pkey, h3_sha) if ph else None
        ex = AM.load_ext(px, spids, pkey, sp_sha) if px else None
        sgp = None
        if det["kind"] != "own":
            pth = det["dir"] / ("scores_gtest.npz" if rel else "scores_gtest_last.npz")
            if pth.exists():
                z = K.load_npz(pth); m_ = dict(zip(z["id"].tolist(), z["score_noTTA" if rel else "score"].astype(float)))
                sgp = np.array([m_.get(i, np.nan) for i in gid])
        sfp = sfl = None
        if rel and (det["dir"] / "scores_ffhqm.npz").exists():
            z = K.load_npz(det["dir"] / "scores_ffhqm.npz")
            mp_, ml_ = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(float))), dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
            sfp = np.array([mp_[i] for i in fid])
            sfl = np.array([ml_[i] for i in fid])
        # ---------------- B1: 0.5 rule
        def b1(pool, x, kind, stems=None, ied=None, border=None):
            x = np.asarray(x, float)
            if not np.isfinite(x).all():
                R1.append([nm, blk, pool, kind, "all", len(x), "", "not scored", "", "", ied, border]); return
            for sub in ("all", "neutral-only"):
                if sub == "neutral-only" and stems is None:
                    continue
                sel = np.ones(len(x), bool) if sub == "all" else np.array([q[4:6] == "03" for q in stems])
                k = int((x[sel] > 0.5).sum())
                R1.append([nm, blk, pool, kind, sub, int(sel.sum()), k, k / sel.sum(), *cpr(k, sel.sum()), ied, border])
        b1("devbona", prob[I.devbona()], "genuine", ied=pied["devbona"])
        for k_, v in pools.items():
            b1(k_, prob[v], "genuine", pstem[k_], pied[k_], pborder.get(k_))
        if ea is not None:
            for a, lab in (("E", "stored-small (arm E)"), ("D20", "one-photo reconstruction, 20 steps"), ("D", "one-photo reconstruction, 100 steps"),
                           ("C20", "same-person mix, 20 steps"), ("C", "same-person mix, 100 steps")):
                b1(lab, ea[ARMS[a]], "genuine-side control", [a43[i]["src_a"] for i in ARMS[a]] if a in ("E", "D", "D20") else None,
                   float(np.median([float(a43[i]["ied"]) for i in ARMS[a]])), float(np.median([float(a43[i]["border_frac"]) for i in ARMS[a]])))
            for a, lab in (("A", "published MorDIFF morphs (200)"), ("B20", "our same-pair morphs, 20 steps"), ("B", "our same-pair morphs, 100 steps")):
                b1(lab, ea[ARMS[a]], "morph")
        if sgp is not None:
            b1("FEI neutral", sgp[[i for i, r in enumerate(G) if r["family"] == "fei_bona_neutral"]], "genuine")
            b1("FEI smiling", sgp[[i for i, r in enumerate(G) if r["family"] == "fei_bona_smiling"]], "genuine")
        if sfp is not None:
            b1("FFHQ orig", sfp[[i for i, r in enumerate(FQ) if r["family"] == "ffhq_bona"]], "genuine")
            for fam in FFQ:
                b1(f"FFHQ E7 {fam}", sfp[[i for i, _ in fq_e[fam]]], "genuine", ied=fq_mied[fam])
        if eh is not None:
            b1("H3 one-identity renders", eh[h3b], "genuine-side control")
            b1("H3 two-identity morphs", eh[h3m], "morph")
        if ex is not None:
            b1("spread-matched renders", ex[spr], "genuine-side control")
        for f in K.FAMS:
            b1(f"morph {f}", prob[fams[f]], "morph", ied=fied[f], border=fborder[f])
            if f in K.FRLLM:
                for v in K.GVARS[1:]:
                    b1(f"morph {f} {v}", prob[I.morph(f, v)], "morph")
        # ---------------- B2: paired logit shifts (releases and SelfMAD own only)
        if blk == "release":
            o = dict(zip(pstem["FRLL orig"], lgt[pools["FRLL orig"]]))
            targets = [(k_, lgt[pools[k_]], pstem[k_], pied[k_]) for k_ in pools if k_ not in ("FRLL orig", "FRLL orig, DiM copy")]
            if eal is not None:
                targets.insert(0, ("stored-small (arm E)", eal[ARMS["E"]], E_st, E_ied))
            for lab, x, st, ied in targets:
                if not np.isfinite(x).all():
                    R2.append([nm, lab, "", "not scored"] + [""] * 13); continue
                ref = np.array([o[q] for q in st])
                d = x - ref
                Wd = D.C[:, [pidx[q[:3]] for q in st]]
                mrep = (Wd * d[None, :]).sum(1) / Wd.sum(1)
                medrep = wquant(d, Wd, 0.5)
                up = int((d > 0).sum())
                fl, fo = x > tl5, ref > tl5
                hl, ho = x > 0, ref > 0
                R2.append([nm, lab, len(d), float(np.median(d)), *K.ci(medrep), float(d.mean()), *K.ci(mrep), up / len(d), *cpr(up, len(d)),
                           int((fl & ~fo).sum()), int((~fl & fo).sum()), int((hl & ~ho).sum()), int((~hl & ho).sum()), ied])
            for lab, x in [("devbona", lgt[I.devbona()]), ("FRLL orig", lgt[pools["FRLL orig"]])] + [(f"morph {f}", lgt[fams[f]]) for f in K.FAMS]:
                if np.isfinite(x).all():
                    RS.append([nm, lab, len(x), *[float(np.percentile(x, q)) for q in (1, 50, 99)], float(np.percentile(x, 99) - np.percentile(x, 1))])
        # ---------------- B3: miss rate with the threshold pool as a column
        for a in (0.05, 0.10):
            tdev = meta[nm][f"t_{a}"]
            avail = [k_ for k_ in pools if np.isfinite(s[pools[k_]]).all()]
            tp = {k_: K.thr_at(s[pools[k_]], a) for k_ in avail}
            neu = np.array([q[4:6] == "03" for q in pstem["FRLL orig"]])
            rules = {"devbona (Part A native)": tdev,
                     "unprocessed FRLL photos (all 204)": tp["FRLL orig"],
                     "unprocessed FRLL photos (neutral-only 102)": K.thr_at(s[pools["FRLL orig"]][neu], a),
                     "every history-matched pool (Part A gated set, with devbona)": max([tdev] + [tp[k_] for k_ in gated if k_ in tp]),
                     "full-frame pools, inter-eye distance >= 100 px": max(tp[k_] for k_ in FULL100 if k_ in tp),
                     "full-frame pools >= 100 px, with devbona": max([tdev] + [tp[k_] for k_ in FULL100 if k_ in tp])}
            for k_ in avail:
                rules[f"single pool: {k_}"] = tp[k_]
            for rn, tt in rules.items():
                mm = {f: float((s[fams[f]] <= tt).mean()) for f in K.FAMS}
                R3.append([nm, blk, a, rn, tt, float(np.mean(list(mm.values()))), *[mm[f] for f in K.FAMS]])
            if blk == "release":
                # bootstrap of the family-mean miss with the threshold refit per replicate
                Wo = Wp["FRLL orig"]
                tr = {"unprocessed FRLL photos (all 204)": K.thr_at(s[pools["FRLL orig"]], a, Wo),
                      "every history-matched pool (Part A gated set, with devbona)": np.max(np.vstack([np.full(B, tdev)] + [K.thr_at(s[pools[k_]], a, Wp[k_]) for k_ in gated if k_ in tp]), 0),
                      "full-frame pools, inter-eye distance >= 100 px": np.max(np.vstack([K.thr_at(s[pools[k_]], a, Wp[k_]) for k_ in FULL100 if k_ in tp]), 0)}
                for rn, ttr in tr.items():
                    rep = np.mean(np.vstack([1 - K.flag_rate(s[fams[f]], ttr, Wf[f]) for f in K.FAMS]), 0)
                    R3S.append([nm, a, rn, [r for r in R3 if r[0] == nm and r[2] == a and r[3] == rn][0][5], *K.ci(rep)])
        # ---------------- B4: border-matched pairing for the MorDIFF frame (releases)
        if blk == "release":
            def pair(lab, x, st, ref_pool, xb, rb, xi, ri):
                rf = dict(zip(pstem[ref_pool], lgt[pools[ref_pool]]))
                ref = np.array([rf[q] for q in st])
                d = x - ref
                Wd = D.C[:, [pidx[q[:3]] for q in st]]
                fl, fo = x > tl5, ref > tl5
                hl, ho = x > 0, ref > 0
                R4.append([nm, lab, ref_pool, len(d), xb, rb, xi, ri, float(np.median(d)), *K.ci(wquant(d, Wd, 0.5)), float(np.mean(d > 0)),
                           int((fl & ~fo).sum()), int((~fl & fo).sum()), int((hl & ~ho).sum()), int((~hl & ho).sum())])
            e7m = "E7 mordiff"; al = "FRLL orig, MorDIFF alignment"
            pair("E7 MorDIFF", lgt[pools[e7m]], pstem[e7m], al, pborder[e7m], pborder[al], pied[e7m], pied[al])
            pair("MorDIFF alignment", lgt[pools[al]], pstem[al], "FRLL orig", pborder[al], pborder["FRLL orig"], pied[al], pied["FRLL orig"])
            pair("E7 MorDIFF", lgt[pools[e7m]], pstem[e7m], "FRLL orig", pborder[e7m], pborder["FRLL orig"], pied[e7m], pied["FRLL orig"])
            if eal is not None:
                pair("stored-small (arm E)", eal[ARMS["E"]], E_st, al, E_border, pborder[al], E_ied, pied[al])
                pair("stored-small (arm E)", eal[ARMS["E"]], E_st, "FRLL orig", E_border, pborder["FRLL orig"], E_ied, pied["FRLL orig"])
            m = lgt[fams["mordiff"]]
            for gp in (al, e7m):
                g = lgt[pools[gp]]
                R4A.append([nm, "MorDIFF morphs (1,000)", gp, fborder["mordiff"], pborder[gp], K.auc(m, g), *K.ci(K.wauc(m, g, Wf["mordiff"], Wp[gp]))])
        # ---------------- B5: paired FFHQ block (releases with FFHQ scores)
        if sfl is not None:
            for fam in FFQ:
                ii = np.array([i for i, _ in fq_e[fam]]); jj = np.array([j for _, j in fq_e[fam]])
                x, ref = sfl[ii], sfl[jj]
                d = x - ref
                rng = np.random.default_rng(K.SEED)
                Wb = rng.multinomial(len(d), np.full(len(d), 1 / len(d)), size=B).astype(float)
                up = int((d > 0).sum())
                fl, fo = x > tl5, ref > tl5
                hl, ho = x > 0, ref > 0
                u1, d1, u2, d2 = int((fl & ~fo).sum()), int((~fl & fo).sum()), int((hl & ~ho).sum()), int((~hl & ho).sum())
                R5.append([nm, fam, len(d), fq_mied[fam], float(fo.mean()), float(fl.mean()), u1, d1, binomtest(min(u1, d1), u1 + d1, 0.5).pvalue if u1 + d1 else 1.0,
                           float(ho.mean()), float(hl.mean()), u2, d2, binomtest(min(u2, d2), u2 + d2, 0.5).pvalue if u2 + d2 else 1.0,
                           float(np.median(d)), *K.ci(wquant(d, Wb, 0.5)), float(d.mean()), *K.ci((Wb * d).sum(1) / Wb.sum(1)), up / len(d)])
        log(nm, "0.5-rule/logit agreement", agree)
    if SMOKE:
        print("smoke ok", len(R1), len(R2), len(RS), len(R3), len(R3S), len(R4), len(R4A), len(R5))
        return
    W_ = lambda fn_, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(K.OUT / fn_, "w", newline=""))  # noqa: E731
    W_("AM2_B1_rule05.csv", ["detector", "block", "pool", "kind", "subset", "n", "k_flagged", "flag_rate", "cp_lo", "cp_hi", "median_ied_px", "median_zero_border"], R1)
    W_("AM2_B2_logit_shift.csv", ["detector", "pool", "n", "median_shift", "median_lo95", "median_hi95", "mean_shift", "mean_lo95", "mean_hi95",
                                  "share_up", "share_up_cp_lo", "share_up_cp_hi", "devthr_up", "devthr_down", "rule05_up", "rule05_down", "median_ied_px"], R2)
    W_("AM2_B2_saturation.csv", ["detector", "pool", "n", "logit_p1", "logit_p50", "logit_p99", "range_p1_p99"], RS)
    W_("AM2_B3_miss_by_threshold_pool.csv", ["detector", "block", "alpha", "threshold_pool", "threshold", "family_mean_miss"] + [f"miss_{f}" for f in K.FAMS], R3)
    W_("AM2_B3_summary_ci.csv", ["detector", "alpha", "threshold_pool", "family_mean_miss", "lo95", "hi95"], R3S)
    W_("AM2_B4_border_pairing.csv", ["detector", "pool", "reference_pool", "n", "median_border_pool", "median_border_ref", "median_ied_pool", "median_ied_ref",
                                    "median_logit_shift", "lo95", "hi95", "share_up", "devthr_up", "devthr_down", "rule05_up", "rule05_down"], R4)
    W_("AM2_B4_mordiff_auc.csv", ["detector", "morphs", "genuine_pool", "median_border_morph", "median_border_genuine", "auc", "lo95", "hi95"], R4A)
    W_("AM2_B5_ffhq_paired.csv", ["detector", "ffhq_e7_pool", "n_pairs", "history_ied_px", "fa_devthr_orig", "fa_devthr_e7", "devthr_up", "devthr_down", "devthr_mcnemar_p",
                                 "rule05_orig", "rule05_e7", "rule05_up", "rule05_down", "rule05_mcnemar_p", "median_logit_shift", "median_lo95", "median_hi95",
                                 "mean_logit_shift", "mean_lo95", "mean_hi95", "share_up"], R5)
    json.dump({"B": B, "seed": K.SEED, "pool_median_ied": pied, "pool_median_border": pborder, "family_median_ied": fied, "family_median_border": fborder,
               "stored_small": {"median_ied": E_ied, "median_border": E_border}, "ffhq_family_morph_ied": fq_mied}, open(K.OUT / "AM2.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()

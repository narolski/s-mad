"""Fixed-threshold re-read (EV1), amendment 1 (Part A side): A1 both class policies for the MorDIFF control images and
the StyleGAN3 renders; A2 the per-pool false-alarm block with paired side changes; A3 the FEI / FRLL backdrop corner
check (computed first), the within-person neutral-above-smiling share, and the neutral-only headline of Part A (worst-pool
threshold from neutral photos, crossed-table AUC on neutral genuine photos). Thresholds are the Part A devbona thresholds.
Run: python3 -I src/EV1/ev1_amend.py [--smoke]
"""
import csv, json, sys, time, pathlib
import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
A43MAN = A43 / "data/manifests/a43.csv"
H3MAN = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv")
SPMAN = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv")
X4 = pathlib.Path("/mnt/t7/smad_heldout/a41g/a41g_out/x4")
X4M = pathlib.Path("/mnt/t7/smad_heldout/a46/a41g_out/a46x4")
FEI = pathlib.Path("/mnt/t7/Datasety/downloads/FEI/extracted")
FRLL = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")
SCOPE = ("Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted); published release numbers are not "
         "reproduced there (released MADation ViT-L/14, FRLL-Morphs AMSL: 17.7% EER here, 7.26% published); the own-crop "
         "re-score of the audit rows (RS1) redoes the key rows.")
DIRS = {lab: d for d, lab in K.RELEASES}


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def ext_paths(name):
    """(a43 file, h3 file, x4 file) for a release label; None where not scored."""
    if name == "SelfMAD release, own preprocessing":
        return (A43 / "a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz", K.MC / "smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz",
                X4 / "selfmad_hrnet_w18/own/scores_a37spread.npz")
    d = DIRS.get(name)
    if d is None:
        return (None, None, None)
    a = A43 / f"a43_out/a43/{d}/rel/scores_a43.npz"
    h = K.A12REL / d / "scores_h3sg3.npz"
    x = X4 / d / "rel/scores_a37spread.npz"
    if not x.exists():
        x = X4M / d / "rel/scores_a37spread.npz"
    return tuple(p if p.exists() else None for p in (a, h, x))


def load_ext(p, ids, key, sha_need=None):
    if p is None:
        return None
    z = K.load_npz(p)
    if sha_need is not None:
        assert str(z["manifest_sha256"]) == sha_need, p
    if key not in z.files:
        return None
    m = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    v = np.array([m.get(i, np.nan) for i in ids])
    return v


def cpr(k, n):
    return K.cp(int(k), int(n)) if n else [None, None]


def corner_noise(path):
    from PIL import Image
    with Image.open(path) as im:
        g = np.asarray(im.convert("RGB"), dtype=np.float64).mean(2)
    H, W = g.shape
    s = max(8, int(round(0.10 * min(H, W))))
    vals = []
    for y0, x0 in ((0, 0), (0, W - s), (H - s, 0), (H - s, W - s)):
        q = g[y0:y0 + s, x0:x0 + s]
        vals.append(np.diff(q, axis=1).std() / np.sqrt(2))
    return float(np.median(vals))


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    PA = json.load(open(K.OUT / "A_partA.json"))
    meta = PA["meta"]
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    G = K.gtest_rows()
    gid = [r["id"] for r in G]
    FQ = K.ffhqm_rows()
    fid = [r["id"] for r in FQ]
    stem6 = lambda i: rows[i]["name"][:6]  # noqa: E731  (NNN_EE of a FRLL photo row)
    # ------------------------------------------------------------------ FRLL photo pools keyed by photo stem
    pools = {f"FRLL {v}": I.bona("frll_bona", v) for v in K.GVARS}
    pools["FRLL orig, MorDIFF alignment"] = I.bona("mordiff_bona")
    pools["FRLL orig, DiM copy"] = I.bona("dim_bona")
    for f in K.FAMS:
        pools[f"E7 {f}"] = I.resmatch(f)
    gated = ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL resample50", "FRLL orig, DiM copy",
             "FRLL orig, MorDIFF alignment"] + [f"E7 {f}" for f in K.FAMS]
    pstem = {k: [stem6(i) for i in v] for k, v in pools.items()}
    orig_stems = pstem["FRLL orig"]
    # ------------------------------------------------------------------ external sets
    a43 = list(csv.DictReader(open(A43MAN)))
    assert K.sha(A43MAN).startswith("ce3a264a")
    a43_sha = K.sha(A43MAN)
    a43ids = [r["id"] for r in a43]
    arm = lambda a: [i for i, r in enumerate(a43) if r["source"] == "a43" and r["arm"] == a]  # noqa: E731
    A43ARMS = {k: arm(k) for k in ("E", "D", "D20", "C", "C20", "A", "B", "B20")}
    a43_R0 = [i for i, r in enumerate(a43) if r["source"] == "eval" and r["family"] == "mordiff_bona"]
    E_stems = [a43[i]["src_a"] for i in A43ARMS["E"]]
    h3 = list(csv.DictReader(open(H3MAN)))
    h3_sha = K.sha(H3MAN)
    h3ids = [r["id"] for r in h3]
    h3m = [i for i, r in enumerate(h3) if r["family"] == "h3_sg3" and r["variant"] == "orig"]
    h3b = [i for i, r in enumerate(h3) if r["family"] == "h3_bona" and r["variant"] == "orig"]
    sp = list(csv.DictReader(open(SPMAN)))
    sp_sha = K.sha(SPMAN)
    spids = [r["id"] for r in sp]
    spr = [i for i, r in enumerate(sp) if r["variant"] == "orig"]
    # ------------------------------------------------------------------ A3 step 1: backdrop corner check (before any FEI share)
    fei_pairs = sorted({r["subj"] for r in G if r["family"] == "fei_bona_neutral"} & {r["subj"] for r in G if r["family"] == "fei_bona_smiling"}, key=int)
    frll_p = sorted({s[:3] for s in orig_stems})
    if SMOKE:
        fei_pairs, frll_p = fei_pairs[:8], frll_p[:8]
    cn = {}
    for lab, items in (("FEI", [(FEI / f"{s}-11.jpg", FEI / f"{s}-12.jpg") for s in fei_pairs]),
                       ("FRLL", [(FRLL / f"neutral_front/{p}_03.jpg", FRLL / f"smiling_front/{p}_08.jpg") for p in frll_p])):
        nn = np.array([corner_noise(a) for a, _ in items])
        ss = np.array([corner_noise(b) for _, b in items])
        ratio = ss / np.maximum(nn, 1e-9)
        med, share = float(np.median(ratio)), float(np.mean(ss > nn))
        cn[lab] = {"n_persons": len(items), "median_noise_neutral": float(np.median(nn)), "median_noise_smiling": float(np.median(ss)),
                   "median_ratio_smiling_over_neutral": med, "share_smiling_noisier": share,
                   "equal_backdrop_noise": bool(0.8 <= med <= 1.25 and 0.3 <= share <= 0.7)}
        log("corner check", lab, cn[lab])
    if not SMOKE:
        json.dump(cn, open(K.OUT / "AM_corner_check.json", "w"), indent=1)
    fei_label = "equal backdrop noise" if cn["FEI"]["equal_backdrop_noise"] else "backdrop noise NOT equal (check failed)"
    # FEI subject index
    fn = {r["subj"]: i for i, r in enumerate(G) if r["family"] == "fei_bona_neutral"}
    fs = {r["subj"]: i for i, r in enumerate(G) if r["family"] == "fei_bona_smiling"}
    DF = K.Draw(fei_pairs, B, K.SEED)
    # ------------------------------------------------------------------ detectors
    dets = K.detectors()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing")] + \
               [d for d in dets if d.get("method") == "M3L"][:1]
    BLK, POL, SHR, NEU, CRN = [], [], [], [], []
    persW = D.C  # B x 102 person counts
    pidx = {p: j for j, p in enumerate(D.per)}
    for det in dets:
        nm = det["name"]
        boot = det["block"] != "other recipe"
        s, key = K.load_scores(det, "eval", ids)
        assert key == meta[nm]["key"], (nm, key)
        sg, _ = K.load_scores(det, "gtest", gid)
        sf, _ = K.load_scores(det, "ffhqm", fid)
        pa, ph, px = ext_paths(nm)
        sa = load_ext(pa, a43ids, key, a43_sha) if pa else None
        cons = None
        if sa is not None:
            cons = float(np.nanmax(np.abs(sa[a43_R0] - s[[ids.index(a43[i]["id"]) for i in a43_R0]])))
        sh = load_ext(ph, h3ids, key, h3_sha) if ph else None
        sx = load_ext(px, spids, key, sp_sha) if px else None
        for a in (0.05, 0.10):
            t = meta[nm][f"t_{a}"]
            # ---------------- A2 per-pool block
            def pool_line(lab, x, stems=None, neutral=None):
                ok = np.isfinite(x)
                if not ok.all():
                    BLK.append([nm, det["block"], a, t, lab, "all", len(x), "not scored"] + [""] * 8)
                    return
                for sub in ("all", "neutral-only"):
                    if sub == "neutral-only" and stems is None:
                        continue
                    sel = np.ones(len(x), bool) if sub == "all" else np.array([st[4:6] == "03" for st in stems])
                    xx = x[sel]
                    k = int((xx > t).sum())
                    row = [nm, det["block"], a, t, lab, sub, len(xx), k / len(xx), *cpr(k, len(xx))]
                    if stems is not None and lab != "FRLL orig":
                        o = dict(zip(orig_stems, s[pools["FRLL orig"]] > t))
                        st_sel = [st for st, q in zip(stems, sel) if q]
                        fl = xx > t
                        up = sum(1 for st, f_ in zip(st_sel, fl) if f_ and not o[st])
                        dn = sum(1 for st, f_ in zip(st_sel, fl) if (not f_) and o[st])
                        pch = len({st[:3] for st, f_ in zip(st_sel, fl) if f_ != o[st]})
                        p = binomtest(min(up, dn), up + dn, 0.5).pvalue if up + dn else 1.0
                        row += [up, dn, pch, p]
                    else:
                        row += ["", "", "", ""]
                    BLK.append(row)
            if sa is not None:
                pool_line("stored-small (MorDIFF published size), arm E", sa[A43ARMS["E"]], E_stems)
            for k_ in ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL jpeg50", "FRLL blur1", "FRLL resample50",
                       "FRLL orig, MorDIFF alignment"] + [f"E7 {f}" for f in K.FAMS]:
                pool_line(k_, s[pools[k_]], pstem[k_])
            for k_, fam in (("FEI neutral", "fei_bona_neutral"), ("FEI smiling", "fei_bona_smiling")):
                if sg is not None:
                    pool_line(k_, sg[[i for i, r in enumerate(G) if r["family"] == fam]])
            if sf is not None:
                pool_line("FFHQ orig", sf[[i for i, r in enumerate(FQ) if r["family"] == "ffhq_bona"]])
                for fam in ("landmark_complete", "landmark_combined", "stylegan_w", "stylegan_wplus", "diffae"):
                    pool_line(f"FFHQ E7 {fam}", sf[[i for i, r in enumerate(FQ) if r["family"] == fam and r["label"] == "0"]])
            # ---------------- worst-pool thresholds (point), camera pools
            tp = {k_: K.thr_at(s[pools[k_]], a) for k_ in gated if np.isfinite(s[pools[k_]]).all()}
            t_cam = max([t] + list(tp.values()))
            # neutral-only gated pools (A3 headline)
            tpn = {}
            for k_ in gated:
                x = s[pools[k_]]
                if not np.isfinite(x).all():
                    continue
                sel = np.array([st[4:6] == "03" for st in pstem[k_]])
                tpn[k_] = K.thr_at(x[sel], a)
            t_neu = max([t] + list(tpn.values()))
            # ---------------- A1 policies: MorDIFF controls
            if sa is not None:
                tE = K.thr_at(sa[A43ARMS["E"]], a)
                tX = max(t_cam, tE)
                tG = max(tX, K.thr_at(sa[A43ARMS["D20"]], a), K.thr_at(sa[A43ARMS["D"]], a))
                for lab, ix in (("arm E stored-small (genuine under both policies)", A43ARMS["E"]),
                                ("D20 one-photo reconstruction, 20 steps", A43ARMS["D20"]),
                                ("D one-photo reconstruction, 100 steps", A43ARMS["D"]),
                                ("C20 same-person mix, 20 steps (own row)", A43ARMS["C20"]),
                                ("C same-person mix, 100 steps (own row)", A43ARMS["C"])):
                    x = sa[ix]
                    for pol, tt in (("native threshold", t), ("worst-pool, policy X (inadmissible)", tX), ("worst-pool, policy G (genuine)", tG)):
                        k = int((x > tt).sum())
                        POL.append([nm, "MorDIFF", a, pol, tt, lab, "flag rate", len(x), k / len(x), *cpr(k, len(x)), cons])
                for lab, x in (("A published MorDIFF morphs (200)", sa[A43ARMS["A"]]), ("B20 our same-pair morphs, 20 steps", sa[A43ARMS["B20"]]),
                               ("B our same-pair morphs, 100 steps", sa[A43ARMS["B"]]), ("eval MorDIFF morphs (1,000)", s[I.morph("mordiff")])):
                    for pol, tt in (("native threshold", t), ("worst-pool, policy X (inadmissible)", tX), ("worst-pool, policy G (genuine)", tG)):
                        k = int((x <= tt).sum())
                        POL.append([nm, "MorDIFF", a, pol, tt, lab, "miss", len(x), k / len(x), *cpr(k, len(x)), cons])
            # ---------------- A1 policies: StyleGAN3
            if sh is not None:
                rend = sh[h3b]
                tGs = max(t_cam, K.thr_at(rend, a), K.thr_at(sx[spr], a) if sx is not None else -np.inf)
                for lab, x in (("H3 one-identity renders (423)", rend), ("spread-matched renders (423)", sx[spr] if sx is not None else None)):
                    if x is None:
                        continue
                    for pol, tt in (("native threshold", t), ("worst-pool, policy X (inadmissible)", t_cam), ("worst-pool, policy G (genuine)", tGs)):
                        k = int((x > tt).sum())
                        POL.append([nm, "StyleGAN3", a, pol, tt, lab, "flag rate", len(x), k / len(x), *cpr(k, len(x)), ""])
                x = sh[h3m]
                for pol, tt in (("native threshold", t), ("worst-pool, policy X (inadmissible)", t_cam), ("worst-pool, policy G (genuine)", tGs)):
                    k = int((x <= tt).sum())
                    POL.append([nm, "StyleGAN3", a, pol, tt, "H3 two-identity morphs (423)", "miss", len(x), k / len(x), *cpr(k, len(x)), ""])
            # ---------------- A3 neutral-only worst-pool misses (headline for imbalanced families)
            for f in K.FAMS:
                m = s[I.morph(f)]
                Wm = D.w([rows[i]["pers"] for i in I.morph(f)])
                for lab, tt in (("worst-pool, neutral-only gated pools", t_neu), ("worst-pool, all photos (Part A)", t_cam)):
                    pt = float((m <= tt).mean())
                    lo, hi = K.ci(1 - K.flag_rate(m, tt, Wm)) if boot else ("", "")
                    NEU.append([nm, det["block"], a, lab, tt, f, len(m), pt, lo, hi])
        # ---------------- A3 within-person neutral-above-smiling share
        def share(x, stems, Wcnt):
            d = {}
            for v, st in zip(x, stems):
                d.setdefault(st[:3], {})[st[4:6]] = v
            ps = [p for p in sorted(d) if "03" in d[p] and "08" in d[p]]
            ind = np.array([1.0 if d[p]["03"] > d[p]["08"] else 0.5 if d[p]["03"] == d[p]["08"] else 0.0 for p in ps])
            pt = float(ind.mean())
            if Wcnt is None:
                return pt, ["", ""], len(ps)
            Wc = Wcnt(ps)
            rep = (Wc * ind[None, :]).sum(1) / np.maximum(Wc.sum(1), 1e-12)
            return pt, K.ci(rep), len(ps)
        wfr = (lambda ps: persW[:, [pidx[p] for p in ps]]) if boot else None
        targets = [(k_, s[pools[k_]], pstem[k_]) for k_ in ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL jpeg50", "FRLL blur1",
                                                            "FRLL resample50", "FRLL orig, MorDIFF alignment"] + [f"E7 {f}" for f in K.FAMS]]
        if sa is not None:
            targets.insert(1, ("stored-small arm E", sa[A43ARMS["E"]], E_stems))
        for lab, x, st in targets:
            if not np.isfinite(x).all():
                SHR.append([nm, det["block"], lab, "", "not scored", "", "", ""])
                continue
            pt, (lo, hi), n = share(x, st, wfr)
            SHR.append([nm, det["block"], lab, n, pt, lo, hi, ""])
        if sg is not None:
            xs = np.array([sg[fn[p]] for p in fei_pairs]); xm = np.array([sg[fs[p]] for p in fei_pairs])
            ind = np.where(xs > xm, 1.0, np.where(xs == xm, 0.5, 0.0))
            lo, hi = K.ci((DF.C * ind[None, :]).sum(1) / DF.C.sum(1)) if boot else ("", "")
            SHR.append([nm, det["block"], "FEI neutral vs smiling frontal", len(ind), float(ind.mean()), lo, hi, fei_label])
        # ---------------- A3 crossed-table AUC with neutral-only genuine (imbalanced families)
        if boot:
            for f in K.FRLLM + K.DIM:
                mvs = list(K.GVARS) if f in K.FRLLM else ["orig"]
                for gv in list(K.GVARS) + ["resmatch"]:
                    gk = f"FRLL {gv}" if gv != "resmatch" else f"E7 {f}"
                    gi = pools[gk]
                    g = s[gi]
                    if not np.isfinite(g).all():
                        continue
                    seln = np.array([st[4:6] == "03" for st in pstem[gk]])
                    Wg = D.w([rows[i]["pers"] for i in gi])
                    for mv in mvs:
                        if f in K.FRLLM:
                            by = {rows[i]["stem"]: i for i in I.morph(f, mv)}
                            ref = sorted({rows[i]["stem"] for i in I.morph(f, "jpeg90")})
                            mi = np.array([by[st] for st in ref])
                        else:
                            mi = I.morph(f)
                        m = s[mi]
                        if not np.isfinite(m).all():
                            continue
                        Wm = D.w([rows[i]["pers"] for i in mi])
                        an = K.auc(m, g[seln])
                        rn = K.wauc(m, g[seln], Wm, Wg[:, seln])
                        aa = K.auc(m, g)
                        tc = K.thr_at(g[seln], 0.05)
                        CRN.append([nm, det["block"], f, mv, gv, an, *K.ci(rn), aa, float((m <= tc).mean())])
        log(nm, "a43 cons", cons, "| h3", sh is not None, "| x4", sx is not None)
    if SMOKE:
        print("smoke ok", len(BLK), len(POL), len(SHR), len(NEU), len(CRN))
        return
    W_ = lambda fn_, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(K.OUT / fn_, "w", newline=""))  # noqa: E731
    W_("AM_A2_pool_block.csv", ["detector", "block", "alpha", "threshold", "pool", "subset", "n", "false_alarm", "cp_lo", "cp_hi",
                               "n_flagged_only_in_variant", "n_flagged_only_in_orig", "n_persons_changing_side", "mcnemar_exact_p"], BLK)
    W_("AM_A1_class_policies.csv", ["detector", "set", "alpha", "threshold_rule", "threshold", "pool", "rate_type", "n", "rate",
                                   "cp_lo", "cp_hi", "a43_consistency_maxabs"], POL)
    W_("AM_A3_neutral_above_smiling.csv", ["detector", "block", "pool", "n_persons", "share_neutral_above_smiling", "lo95", "hi95", "note"], SHR)
    W_("AM_A3_worstpool_neutral.csv", ["detector", "block", "alpha", "threshold_rule", "threshold", "family", "n", "miss", "lo95", "hi95"], NEU)
    W_("AM_A3_crossed_neutral.csv", ["detector", "block", "family", "morph_variant", "genuine_variant", "auc_neutral_only", "lo95", "hi95",
                                    "auc_all_photos", "miss_at_5pct_on_neutral_genuine"], CRN)
    json.dump({"scope": SCOPE, "corner_check": cn, "B": B, "seed": K.SEED}, open(K.OUT / "AM_partA.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()

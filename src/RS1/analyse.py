"""Own-crop re-score of the audit rows (RS1): tables. CPU only. Reads the RS1 score files (MADation ViT-B/16,
ViT-L/14, FE ViT-L/14, FE ViT-B/16, MixFaceNet-MAD through their own crop) and the EXISTING SelfMAD own-preprocessing
score files (A41 x7 raw files, A32-RSX our frames, A43 own our frames). No score is recomputed for SelfMAD.

  python3 -I analyse.py [--B 2000] [--smoke]
Writes experiments/RS1_own-crop-rescore/rs1_*.csv and rs1_results.json.

Statistics reuse the record's code (imported unchanged from the frozen A46 runtime): a41_read.Draw (pigeonhole person
bootstrap), a36_read.wauc, analyze.eer / eer_weighted. Thresholds per replicate are computed here (t5, t_eer; see
prereg.md).
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ar1_common as K  # noqa: E402

K.add_paths(K.MC, K.W46 / "smadcvpr")
import a41_read as M  # noqa: E402
import a36_read as R36  # noqa: E402
import analyze as A  # noqa: E402

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
SEED = 20261111
FRLL = ("amsl", "facemorpher", "opencv", "webmorph", "stylegan")
DIM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
E7RAW = ("mordiff", "dim_a", "greedy_dim")
REL = ("madation_vitb16", "madation_vitl14", "madation_fe_vitl14", "madation_fe_vitb16", "mixfacenet_mad_smdd")
REL_ATH = REL + ("madation_fs_vitb16", "madation_fs_vitl14")
FAM22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
ATH = OUT / "athena"
NAME = {"madation_vitb16": "MADation ViT-B/16 (LoRA) release", "madation_vitl14": "MADation ViT-L/14 (LoRA) release",
        "madation_fe_vitl14": "MADation FE ViT-L/14 release", "madation_fe_vitb16": "MADation FE ViT-B/16 release",
        "mixfacenet_mad_smdd": "MixFaceNet-MAD release", "selfmad": "SelfMAD release (HRNet-W18)",
        "madation_fs_vitb16": "MADation FS ViT-B/16 release", "madation_fs_vitl14": "MADation FS ViT-L/14 release"}
PUB = {  # prereg.md, fixed before any RS1 score
    "madation_vitb16": {"mordiff": 1.10, "amsl": 3.85, "facemorpher": 1.35, "opencv": 2.97, "stylegan": 17.21,
                        "webmorph": 3.42},
    "madation_vitl14": {"mordiff": 19.26, "amsl": 7.26, "facemorpher": 0.74, "opencv": 0.99, "stylegan": 24.96,
                        "webmorph": 4.07},
    "madation_fe_vitb16": {"mordiff": 17.86}, "madation_fe_vitl14": {"mordiff": 22.85},
    "mixfacenet_mad_smdd": {"mordiff": 8.50, "amsl": 15.18, "facemorpher": 3.87, "opencv": 4.39, "stylegan": 8.99,
                            "webmorph": 12.35},
    "selfmad": {"amsl": 0.99, "facemorpher": 0.00, "opencv": 0.00, "stylegan": 10.34, "webmorph": 3.45,
                "greedy_dim": 7.60}}
PUB["madation_fs_vitb16"] = {"mordiff": 28.14}
PUB["madation_fs_vitl14"] = {"mordiff": 40.92}
for _d, _v in {"madation_vitb16": (0.00, 33.37, 22.21, 3.85, 10.80), "madation_vitl14": (0.40, 20.32, 9.06, 2.23, 20.40),
               "madation_fe_vitb16": (2.89, 26.00, 34.26, 14.88, 32.80),
               "madation_fe_vitl14": (9.77, 23.51, 21.81, 15.89, 26.40),
               "madation_fs_vitb16": (5.38, 32.87, 27.19, 16.30, 22.80),
               "madation_fs_vitl14": (22.63, 23.80, 21.81, 30.47, 33.60),
               "mixfacenet_mad_smdd": (4.60, 16.70, 20.62, 8.33, 18.20)}.items():   # amendment 1 (MADation T1 / T2)
    PUB[_d].update({f"mad22_{f}": v for f, v in zip(FAM22, _v)})
ALT_PUB = {("madation_vitl14", "mordiff"): 20.40,        # MADation Table 2 (labels permuted against Table 1)
           ("madation_vitl14", "mad22_OpenCV"): 19.26, ("madation_vitl14", "mad22_Webmorph"): 2.23}


def cell_sets(c):
    """genuine, morphs, raw E7, aligned E7, aligned native set names of a cell."""
    if c.startswith("mad22_"):
        f = c[6:]
        return "G22_raw", f"M22_{f}", None, f"E7aln22_{f}", "G22_aln"
    if c == "mordiff":
        return "G_raw", "M_mordiff", "E7raw_mordiff", "E7aln_mordiff", "Galn_mordiff"
    return "G_raw", f"M_{c}", (f"E7raw_{c}" if c in E7RAW else None), f"E7aln_{c}", "Galn_frll"


CELLS = FRLL + ("mordiff",) + DIM + tuple(f"mad22_{f}" for f in FAM22)
LAB_OK, LAB_NO, LAB_NA = "reproduced", "our pipeline, published number not reproduced", "no published number"


def label(det, cell, eer):
    p = PUB.get(det, {}).get(cell)
    if p is None:
        return LAB_NA, None, None
    w = max(1.5, 0.25 * p)
    return (LAB_OK if abs(eer - p) <= w else LAB_NO), p, w


# ------------------------------------------------------------------------------------------------ score tables
class Pool:
    """one image set for one detector: scores (ranking key), persons, expression, source label."""

    def __init__(self, s, pp, ex, src, key, ph=None):
        self.s, self.pp, self.ex, self.src, self.key = np.asarray(s, float), pp, np.asarray(ex), src, key
        self.ph = np.asarray(ph if ph is not None else [""] * len(self.s))

    def sub(self, mask):
        mask = np.asarray(mask)
        return Pool(self.s[mask], [p for p, k in zip(self.pp, mask) if k], self.ex[mask], self.src, self.key,
                    self.ph[mask])


def manifest():
    rows = list(csv.DictReader(open(OUT / "manifest.csv")))
    return {r["id"]: r for r in rows}


def rel_pools(det, man, smoke):
    if smoke:
        fs = [OUT / "scores/smoke" / f"scores_rel_{det}_limit8.npz"]
    else:
        fs = [OUT / "scores" / f"scores_rel_{det}__{part}.npz" for part in ("a46", "new", "amend")]
    fs = [f for f in fs if f.exists()]
    if not fs:
        return None
    by, seen = {}, set()
    for f in fs:
        z = np.load(f)
        assert str(z["det"]) == det and str(z["mode"]) == "rel"
        for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
            assert i not in seen
            seen.add(i)
            r = man[i]
            by.setdefault(r["set"], []).append((float(l), tuple(r["persons"].split("|")), r["expr"], r["photo"]))
    return {s: Pool([v[0] for v in L], [v[1] for v in L], [v[2] for v in L], "own crop", "logit", [v[3] for v in L])
            for s, L in by.items()}


def athena_pools(det):
    f = ATH / "results" / f"scores_rel_{det}__athena.npz"
    if not f.exists():
        return None
    man = {r["id"]: r for r in csv.DictReader(open(ATH / "athena_manifest.csv"))}
    z = np.load(f)
    assert str(z["det"]) == det and str(z["mode"]) == "rel"
    by = {}
    for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
        r = man[i]
        by.setdefault(r["set"], []).append((float(l), tuple(r["persons"].split("|")), r["expr"], r["photo"]))
    return {s_: Pool([v[0] for v in L], [v[1] for v in L], [v[2] for v in L], "own crop (Athena)", "logit",
                     [v[3] for v in L]) for s_, L in by.items()}


def _pools(by, src, key):
    return {s_: Pool([v[0] for v in L], [v[1] for v in L], [v[2] for v in L], src, key, [v[3] for v in L])
            for s_, L in by.items()}


def selfmad_pools(man):
    """SelfMAD own-preprocessing scores, mapped to RS1 set names. Existing files: A41 x7 raw files (logit), A32-RSX our
    frames (probability only; incl. the JPEG 50 / 70 and 50% shrink-and-enlarge frames), A43 own our frames (logit).
    New (amendment 2): AR1 score.py --mode own on FEI, FFHQ and the A43 stored files (logit)."""
    P = {}
    xm = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_heldout/a41g/x7/manifests/a41g_x7.csv"))}
    z = np.load("/mnt/t7/smad_heldout/a41g/a41g_out/x7/selfmad_hrnet_w18/x7/scores_a41g_x7.npz")
    assert str(z["ckpt_sha256"]) == K.WEIGHT_SHA["selfmad_hrnet_w18"]
    fmap = {"frll_bona_raw": "G_raw", "mordiff_raw": "M_mordiff", "dim_a_raw": "M_dim_a",
            "greedy_dim_raw": "M_greedy_dim", **{f"{f}_raw": f"M_{f}" for f in FRLL},
            **{f"e7area_{f}": f"E7raw_{f}" for f in E7RAW}}
    by = {}
    for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
        r = xm[i]
        s_ = fmap.get(r["family"])
        if s_ is None:
            continue
        nm = pathlib.Path(r["raw_path"] or r["path"]).name
        lab = int(r["label"])
        pp, ex = persons_expr(nm, lab)
        by.setdefault(s_, []).append((float(l), pp, ex, f"{pp[0]}_{ex}" if lab == 0 else ""))
    P.update(_pools(by, "SelfMAD crop, raw files (A41 x7)", "logit"))
    ev = {r["id"]: r for r in csv.DictReader(open(DATA / "manifests/eval.csv"))}
    z = np.load("/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz")
    assert str(z["ckpt_sha256"]) == K.WEIGHT_SHA["selfmad_hrnet_w18"]
    by = {}
    for i, p in zip(z["id"].tolist(), z["score"]):
        r = ev[i]
        if r["label"] != "0":
            continue
        st, fam, var = r["set"], r["family"], r["variant"]
        s_ = ("Galn_frll" if (st, var) == ("frllm", "orig") else "Galn_mordiff" if (st, var) == ("mordiff", "orig")
              else f"E7aln_{fam}" if var == "resmatch" and st in ("frllm", "mordiff", "dim")
              else f"G{var}_frll" if st == "frllm" and var in ("jpeg50", "jpeg70", "resample50") else None)
        if s_ is None:
            continue
        pp, ex = persons_expr(pathlib.Path(r["path"]).name, 0)
        by.setdefault(s_, []).append((float(p), pp, ex, f"{pp[0]}_{ex}"))
    P.update(_pools(by, "SelfMAD crop of our aligned frames (A32-RSX)", "prob32"))
    am = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_heldout/a43/data/manifests/a43.csv"))}
    z = np.load("/mnt/t7/smad_heldout/a43/a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz")
    assert str(z["ckpt_sha256"]) == K.WEIGHT_SHA["selfmad_hrnet_w18"]
    by = {}
    for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
        r = am[i]
        if r["arm"]:
            s_ = f"a43f_{r['arm']}"
            if r["arm"] in ("A", "B", "B20"):
                pp = (r["src_a"][:3], r["src_b"][:3])
                ex = r["src_a"][4:6] if r["src_a"][4:6] == r["src_b"][4:6] else "mix"
                ph = ""
            else:
                pp = (r["src_a"][:3],)
                ex = "mix" if r["arm"] in ("C", "C20") else r["src_a"][4:6]
                ph = "" if r["arm"] in ("C", "C20") else r["src_a"]
        elif r["family"] == "mordiff_bona":
            s_ = "a43f_photo"
            pp, ex = persons_expr(pathlib.Path(r["path"]).name, 0)
            ph = f"{pp[0]}_{ex}"
        else:
            continue
        by.setdefault(s_, []).append((float(l), pp, ex, ph))
    P.update(_pools(by, "SelfMAD crop of our aligned frames (A43 own)", "logit"))
    f = OUT / "scores/scores_own_selfmad__amend.npz"
    if f.exists():
        z = np.load(f)
        assert str(z["mode"]) == "own"
        by = {}
        for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
            r = man[i]
            by.setdefault(r["set"], []).append((float(l), tuple(r["persons"].split("|")), r["expr"], r["photo"]))
        P.update(_pools(by, "SelfMAD own crop, stored / dataset files (RS1, amendment 2)", "logit"))
    if "a43_E" not in P:                                   # fall back to the frames for the ladder
        for k in list(P):
            if k.startswith("a43f_"):
                P["a43_" + k[5:]] = P[k]
    return P


def persons_expr(name, lab):
    import re
    if lab == 0:
        m = re.match(r"^(\d{3})_(\d{2})", name)
        return (m.group(1),), m.group(2)
    m = re.match(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})", name)
    if m:
        return (m.group(1), m.group(3)), (m.group(2) if m.group(2) == m.group(4) else "mix")
    m = re.match(r"^(\d{3})_(\d{3})", name)
    return (m.group(1), m.group(2)), ""


def prob32(P):
    return P.s.astype(np.float32).astype(float) if P.key == "prob32" else \
        (1 / (1 + np.exp(-P.s))).astype(np.float32).astype(float)


def common(*pools):
    """pools on one scale: logits if all carry logits, else float32 probabilities (the SelfMAD frames file stores
    probabilities only; sigmoid is monotone, so only float32 saturation ties differ)."""
    if len({P.key for P in pools}) == 1:
        return [P.s for P in pools]
    return [prob32(P) for P in pools]


def pair(a, b):
    return common(a, b)


# ------------------------------------------------------------------------------------------------ statistics
class Stats:
    """separate pigeonhole draws per photo population: the 102 FRLL persons (the registered draw), FEI subjects, FFHQ
    images (no identity labels: one image = one unit)."""

    def __init__(self, Ds):
        self.Ds = Ds

    def D(self, P):
        p0 = P.pp[0][0]
        return self.Ds["fei" if p0.startswith("fei") else "ffhq" if p0.startswith("ffhq") else "frll"]

    def w(self, P):
        D = self.D(P)
        return D.wm(P.pp) if len(P.pp[0]) == 2 else D.wb([(p[0],) for p in P.pp])

    def eer(self, b, m):
        sb, sm = pair(b, m)
        pt = 100 * A.eer(sb, sm)
        rep = 100 * A.eer_weighted(sb, sm, self.w(b), self.w(m))
        return pt, rep

    def auc(self, pos, neg):
        sp, sn = pair(pos, neg)
        pt = float(R36.wauc(sp, sn, np.ones((1, len(sp))), np.ones((1, len(sn))))[0])
        rep = R36.wauc(sp, sn, self.w(pos), self.w(neg))
        return pt, rep


def thr_eer(sb, sm, wb, wm):
    """per replicate (rows of wb, wm): the threshold analyze.eer_weighted selects (flagged = score >= t)."""
    ob, om = np.argsort(sb, kind="stable"), np.argsort(sm, kind="stable")
    bs, ms = sb[ob], sm[om]
    t = np.concatenate([bs, ms])
    ib, im = np.searchsorted(bs, t, side="left"), np.searchsorted(ms, t, side="left")
    cb = np.concatenate([np.zeros((len(wb), 1)), np.cumsum(wb[:, ob], 1)], 1)
    cm = np.concatenate([np.zeros((len(wm), 1)), np.cumsum(wm[:, om], 1)], 1)
    fpr = 1 - cb[:, ib] / np.maximum(cb[:, -1:], 1e-12)
    fnr = cm[:, im] / np.maximum(cm[:, -1:], 1e-12)
    return t[np.argmin(np.abs(fnr - fpr), 1)]


def thr_5(sb, wb, alpha=0.05):
    """per replicate: the lowest native genuine score (among photos drawn in the replicate) with a weighted share of
    native genuine photos strictly above it of at most alpha (flagged = score > t5)."""
    ob = np.argsort(sb, kind="stable")
    bs, W = sb[ob], wb[:, ob]
    tot = W.sum(1, keepdims=True)
    ir = np.searchsorted(bs, bs, side="right")              # count of values <= each candidate
    cum = np.concatenate([np.zeros((len(W), 1)), np.cumsum(W, 1)], 1)
    above = 1 - cum[:, ir] / np.maximum(tot, 1e-12)         # (R, n) share strictly above candidate j
    ok = (above <= alpha + 1e-12) & (W > 0)
    j = np.argmax(ok, 1)                                    # first (lowest) candidate meeting the condition
    return bs[j]


def flag_rate(sx, wx, t, strict):
    hit = (sx[None, :] > t[:, None]) if strict else (sx[None, :] >= t[:, None])
    return (hit * wx).sum(1) / np.maximum(wx.sum(1), 1e-12)


def flag_block(S, G, Mo, X):
    """flag rates of pool X at t5 (score > t5) and t_eer (score >= t_eer), thresholds set on the native genuine photos
    G (and the cell's morphs Mo for t_eer), on one common scale, recomputed in every replicate. -> {name: (point,
    replicates, ties at the point threshold)}"""
    sG, sM, sx = common(G, Mo, X)
    oG, oM, oX = np.ones((1, len(sG))), np.ones((1, len(sM))), np.ones((1, len(sx)))
    wG, wM, wX = S.w(G), S.w(Mo), S.w(X)
    t5p, tep = thr_5(sG, oG)[0], thr_eer(sG, sM, oG, oM)[0]
    return {"t5": (float(flag_rate(sx, oX, np.array([t5p]), True)[0]), flag_rate(sx, wX, thr_5(sG, wG), True),
                   int(np.sum(sx == t5p))),
            "t_eer": (float(flag_rate(sx, oX, np.array([tep]), False)[0]), flag_rate(sx, wX, thr_eer(sG, sM, wG, wM), False),
                      int(np.sum(sx == tep)))}


def ci(rep):
    return M.ci(rep)


def fmt(pt, rep, d=2, pct=False):
    lo, hi = ci(rep)
    k = 100 if pct else 1
    return f"{k * pt:.{d}f} [{k * lo:.{d}f}, {k * hi:.{d}f}]"


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--skip-selfmad", action="store_true")
    a = ap.parse_args()
    man = manifest()
    allp = {p for r in man.values() for p in r["persons"].split("|")}
    pers = sorted(p for p in allp if p.isdigit())
    assert len(pers) == 102
    Ds = {"frll": M.Draw(pers, a.B, SEED), "fei": M.Draw(sorted(p for p in allp if p.startswith("fei")), a.B, SEED + 1),
          "ffhq": M.Draw(sorted(p for p in allp if p.startswith("ffhq")), a.B, SEED + 2)}
    S = Stats(Ds)
    runs = []                                          # (detector, platform, pools)
    for d in REL:
        p = rel_pools(d, man, a.smoke)
        if p:
            runs.append((d, "DGX", p))
    if not a.smoke:
        for d in REL_ATH:
            p = athena_pools(d)
            if p:
                runs.append((d, "Athena", p))
    if not a.skip_selfmad:
        runs.append(("selfmad", "DGX (existing files)", selfmad_pools(man)))
    out = dict(B=a.B, seed=SEED, persons=len(pers), reproduction=[], history=[], flags=[], expression=[], ladder=[],
               ladder_flags=[], counts={})
    for det, plat, P in runs:
        out["counts"][f"{det}@{plat}"] = {s_: len(p.s) for s_, p in sorted(P.items())}
        cells = [c for c in CELLS if cell_sets(c)[0] in P and cell_sets(c)[1] in P]
        for c in cells:
            gs, ms, hraw, haln, gal = cell_sets(c)
            G, Mo = P[gs], P[ms]
            pt, rep = S.eer(G, Mo)
            lab, pub, win = label(det, c, pt)
            alt = ALT_PUB.get((det, c))
            altlab = (LAB_OK if alt is not None and abs(pt - alt) <= max(1.5, 0.25 * alt) else LAB_NO) if alt else ""
            out["reproduction"].append(dict(detector=NAME[det], platform=plat, cell=c, n_genuine=len(G.s),
                                            n_morph=len(Mo.s), native_eer=round(pt, 3), lo=round(ci(rep)[0], 3),
                                            hi=round(ci(rep)[1], 3), published=pub,
                                            abs_diff=None if pub is None else round(abs(pt - pub), 3),
                                            window=win, label=lab, alt_published=alt, alt_label=altlab,
                                            genuine_src=G.src, morph_src=Mo.src))
            # history-matched genuine photos
            if hraw and hraw in P:
                H, kind = P[hraw], "raw E7 files"
            elif haln in P:
                H, kind = P[haln], "aligned-frame E7"
            else:
                H, kind = None, ""
            GA, Ealn, E = P.get(gal), P.get(haln), P.get("a43_E")
            hist = dict(detector=NAME[det], platform=plat, cell=c, label=lab, e7_kind=kind)
            if H is not None:
                hp, hr = S.eer(H, Mo)
                hist.update(e7_eer=fmt(hp, hr), e7_eer_pt=round(hp, 3))
                if kind == "raw E7 files":
                    hist.update(history_effect=fmt(hp - pt, hr - rep), history_effect_pt=round(hp - pt, 3))
                if GA is not None:
                    ap_, ar_ = S.eer(GA, Mo)
                    hist.update(aligned_native_eer=fmt(ap_, ar_), aligned_native_eer_pt=round(ap_, 3))
                    if Ealn is not None:
                        ep, er = S.eer(Ealn, Mo)
                        hist.update(aligned_e7_eer=fmt(ep, er),
                                    aligned_history_effect=fmt(ep - ap_, er - ar_),
                                    aligned_history_effect_pt=round(ep - ap_, 3),
                                    aligned_e7_minus_raw_native=fmt(ep - pt, er - rep))
                hist.update(native_eer=fmt(pt, rep), e7_src=H.src)
            out["history"].append(hist)
            # flag rates at thresholds set on the native raw genuine photos (recomputed per replicate)
            pools = [("native genuine", G), ("history-matched genuine (" + kind + ")", H),
                     ("aligned native genuine", GA), ("stored-small photo (A43 E)", E)]
            for pn, X in pools:
                if X is None:
                    continue
                for tn, (fp, fr, ties) in flag_block(S, G, Mo, X).items():
                    out["flags"].append(dict(detector=NAME[det], platform=plat, cell=c, label=lab, threshold=tn, pool=pn,
                                             n=len(X.s), flagged=fmt(fp, fr, 1, pct=True), flagged_pt=round(100 * fp, 2),
                                             ties_at_threshold=ties, src=X.src))
            # expression split of the genuine class
            for spl, code in (("neutral only", "03"), ("smiling only", "08")):
                Gs = G.sub(G.ex == code)
                ep_, er_ = S.eer(Gs, Mo)
                row = dict(detector=NAME[det], platform=plat, cell=c, label=lab, genuine=spl, n=len(Gs.s),
                           native_eer=fmt(ep_, er_),
                           native_eer_pt=round(ep_, 3))
                if H is not None:
                    Hs = H.sub(H.ex == code)
                    hp_, hr_ = S.eer(Hs, Mo)
                    fp, fr, _ = flag_block(S, G, Mo, Hs)["t5"]
                    row.update(e7_kind=kind, e7_eer=fmt(hp_, hr_), e7_eer_pt=round(hp_, 3),
                               e7_flag_t5=fmt(fp, fr, 1, pct=True), e7_flag_t5_pt=round(100 * fp, 2))
                out["expression"].append(row)
        # MorDIFF ladder on the A43 control images
        if "a43_E" in P and "M_mordiff" in P:
            photo = P["a43_photo"] if "a43_photo" in P and P["a43_E"].src == P["a43_photo"].src else P["G_raw"]
            lab = label(det, "mordiff", 100 * A.eer(*pair(P["G_raw"], P["M_mordiff"])))[0]
            C = [("stored-small photo E vs photo", "a43_E", None), ("reconstruction D20 vs stored-small photo E", "a43_D20", "a43_E"),
                 ("reconstruction D (100 steps) vs stored-small photo E", "a43_D", "a43_E"),
                 ("our morph B20 vs reconstruction D20", "a43_B20", "a43_D20"),
                 ("our morph B (100 steps) vs reconstruction D", "a43_B", "a43_D"),
                 ("published A vs our morph B20", "a43_A", "a43_B20"), ("published A vs our morph B", "a43_A", "a43_B"),
                 ("same-person mix C20 vs reconstruction D20", "a43_C20", "a43_D20"),
                 ("our morph B20 vs same-person mix C20", "a43_B20", "a43_C20"),
                 ("published A vs stored-small photo E", "a43_A", "a43_E"), ("published A vs photo", "a43_A", None)]
            for name, pos, neg in C:
                Pn = photo if neg is None else P[neg]
                pt, rep = S.auc(P[pos], Pn)
                out["ladder"].append(dict(detector=NAME[det], platform=plat, contrast=name, auc=fmt(pt, rep, 3), auc_pt=round(pt, 4),
                                          mordiff_label=lab, n_pos=len(P[pos].s), n_neg=len(Pn.s),
                                          src="photo: " + photo.src + "; controls: " + P[pos].src))
            ep, er = S.eer(photo, P["a43_A"])
            out["ladder"].append(dict(detector=NAME[det], platform=plat, contrast="EER photo vs published A (200 sampled)",
                                      auc=fmt(ep, er), auc_pt=round(ep, 3), mordiff_label=lab, n_pos=200,
                                      n_neg=len(photo.s), src=photo.src))
            G, Mo = P["G_raw"], P["M_mordiff"]
            for arm in ("E", "D20", "D", "C20", "C", "B20", "B", "A"):
                X = P[f"a43_{arm}"]
                for tn, (fp, fr, ties) in flag_block(S, G, Mo, X).items():
                    out["ladder_flags"].append(dict(detector=NAME[det], platform=plat, threshold=tn, arm=arm, n=len(X.s),
                                                    flagged=fmt(fp, fr, 1, pct=True), flagged_pt=round(100 * fp, 2),
                                                    ties_at_threshold=ties, mordiff_label=lab, src=X.src))
    sfx = "_smoke" if a.smoke else ""
    json.dump(out, open(RES / f"rs1_results{sfx}.json", "w"), indent=1, default=float)
    for k in ("reproduction", "history", "flags", "expression", "ladder", "ladder_flags"):
        rows = out[k]
        if not rows:
            continue
        cols = []
        for r in rows:
            cols += [c for c in r if c not in cols]
        with open(RES / f"rs1_{k}{sfx}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    print("written", {k: len(out[k]) for k in out if isinstance(out[k], list)})


if __name__ == "__main__":
    main()

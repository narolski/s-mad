"""SM1 Part 3 reader: per arm and seed, EER per cell (native, E7), rise under E7, AR1 ladder AUCs and flag rates,
within-person neutral-above-smiling AUC; 5-seed means with paired person-bootstrap intervals; registered falsifiers.

Person bootstrap: pigeonhole Draw, B = 2,000; FRLL persons (FRLL-Morphs, MorDIFF, DiM, corrected MAD22 share the 102
persons) seed [20261111, 3]; AR1 persons seed [20261111, 4]. The same draws for every arm and seed. Flag thresholds
are each head's own unit-weight thresholds (A1.5); flag rates are then bootstrapped by person.

  python3 -I read_p3.py [--smoke] [--arms a,b,...] [--B 2000]
-> RES/p3_<tag>.json, RES/p3_<tag>_seeds.csv
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

FRLLM = ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")
DIM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
M22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
LANDMARK7 = ("frllm:amsl", "frllm:facemorpher", "frllm:opencv", "frllm:webmorph", "mad22:FaceMorpher", "mad22:OpenCV",
             "mad22:Webmorph")
DIFF7 = ("mordiff:mordiff",) + tuple(f"dim:{f}" for f in DIM)
GAN3 = ("frllm:stylegan", "mad22:MIPGAN_I", "mad22:MIPGAN_II")
STEPS = (("a", "b", "tool"), ("b", "bp", "partner balance"), ("bp", "cr", "source pool + shared identities"),
         ("cr", "c", "pair similarity (look-alike)"), ("c", "d", "halves as genuine"), ("a", "a256", "size cue"),
         ("c", "dplus", "halves added (unequal count)"), ("d", "e", "history crossing"),
         ("b", "d50", "dose K 5 -> 50"), ("b", "d500", "dose K 5 -> 500"), ("b", "bp", "dose K 5 -> all (b')"))


def meta():
    rows = []
    for t in ("test_eval", "test_mad22", "test_ar1", "test_ar1h"):
        p = K.OUT / "flists" / f"{t}.csv"
        if p.exists():
            rows += list(csv.DictReader(open(p)))
    return rows


class Reader:
    def __init__(self, rows, B):
        self.rows = rows
        self.idx = {}
        for i, r in enumerate(rows):
            self.idx.setdefault((r["cell"], r["label"], r["hist"]), []).append(i)
        self.p1 = np.array([r["p1"] for r in rows])
        self.p2 = np.array([r["p2"] for r in rows])
        fr = [r for r in rows if not r["cell"].startswith("ar1")]
        ar = [r for r in rows if r["cell"].startswith("ar1")]
        self.Df = S.Draw([x for r in fr for x in (r["p1"], r["p2"])], B, [K.SEED, 3])
        self.Da = S.Draw([x for r in ar for x in (r["p1"], r["p2"])], B, [K.SEED, 4])
        self.B = B
        self.wcache = {}

    def sel(self, cell, label, hist):
        return np.array(self.idx.get((cell, label, hist), []), int)

    def w(self, ix, ar1=False):
        key = (ar1, ix.tobytes())
        if key not in self.wcache:
            D = self.Da if ar1 else self.Df
            self.wcache[key] = D.w(self.p1[ix], self.p2[ix])
        return self.wcache[key]


def cells():
    out = {}
    for f in FRLLM:
        out[f"frllm:{f}"] = (("frllm:bona", "0", "native"), (f"frllm:{f}", "0", "e7"), (f"frllm:{f}", "1", "morph"))
    out["mordiff:mordiff"] = (("mordiff:bona", "0", "native"), ("mordiff:mordiff", "0", "e7"),
                              ("mordiff:mordiff", "1", "morph"))
    for f in DIM:
        out[f"dim:{f}"] = (("dim:bona", "0", "native"), (f"dim:{f}", "0", "e7"), (f"dim:{f}", "1", "morph"))
    for f in M22:
        out[f"mad22:{f}"] = (("mad22:bona", "0", "native"), (f"mad22:{f}", "0", "e7"), (f"mad22:{f}", "1", "morph"))
    return out


def one(R, z):
    """All metrics of one score vector z (aligned with R.rows): {name: (point, draws (B,))}."""
    m = {}
    for c, (gn, ge, mo) in cells().items():
        im, ign, ige = R.sel(*mo), R.sel(*gn), R.sel(*ge)
        if not len(im):
            continue
        for h, ig in (("native", ign), ("e7", ige)):
            if not len(ig):
                continue
            pt, thr = S.eer_unit(z[ig], z[im])
            dr, _ = S.weer(z[ig], z[im], R.w(ig), R.w(im))
            m[f"eer:{h}:{c}"] = (pt, dr)
            if c == "frllm:opencv" and h == "native":
                m["_thr_frll_opencv"] = (thr, None)
        if f"eer:e7:{c}" in m:
            m[f"rise:{c}"] = (m[f"eer:e7:{c}"][0] - m[f"eer:native:{c}"][0], m[f"eer:e7:{c}"][1] - m[f"eer:native:{c}"][1])
    for name, group in (("landmark7", LANDMARK7), ("diff7", DIFF7), ("gan3", GAN3)):
        for h in ("native", "e7"):
            ks = [f"eer:{h}:{c}" for c in group if f"eer:{h}:{c}" in m]
            if len(ks) == len(group):
                m[f"mean_eer:{h}:{name}"] = (float(np.mean([m[k][0] for k in ks])), np.mean([m[k][1] for k in ks], 0))
        if f"mean_eer:e7:{name}" in m:
            m[f"mean_rise:{name}"] = (m[f"mean_eer:e7:{name}"][0] - m[f"mean_eer:native:{name}"][0],
                                      m[f"mean_eer:e7:{name}"][1] - m[f"mean_eer:native:{name}"][1])
    # ---- AR1 ladder, flag rates
    g = lambda pool, tool, rung, lab="0": R.sel(f"ar1:{pool}:{tool}:{rung}", lab, "")  # noqa: E731
    r0, r4 = g("frgcferet", "none", "R0"), g("frgcferet", "opencv", "R4", "1")
    if len(r0) and len(r4):
        _, t_ar1 = S.eer_unit(z[r0], z[r4])
        t5 = float(np.quantile(z[r0], 0.95))
        halves = np.concatenate([g("frgcferet", "opencv", "HA"), g("frgcferet", "opencv", "HB")])
        sets = {"halves": halves, "r2w_opencv": g("frgcferet", "opencv", "R2w"),
                "r2w_facemorpher": g("frgcferet", "facemorpher", "R2w"), "r3m_opencv": g("frgcferet", "opencv", "R3m"),
                "r3m_facemorpher": g("frgcferet", "facemorpher", "R3m"), "r0": r0}
        thr = {"ar1eer": t_ar1, "r0_5pct": t5}
        if "_thr_frll_opencv" in m:
            thr["frllopencv"] = m["_thr_frll_opencv"][0]
        for tn, t in thr.items():
            for sn, ix in sets.items():
                if not len(ix):
                    continue
                f = (z[ix] >= t).astype(float)
                W = R.w(ix, True)
                m[f"flag:{tn}:{sn}"] = (float(f.mean()), (W * f).sum(1) / np.maximum(W.sum(1), 1e-12))
        for pool in ("frgcferet", "frll"):
            R0 = g(pool, "none", "R0")
            for tool in ("opencv", "facemorpher"):
                R4 = g(pool, tool, "R4", "1")
                for neg in ("R0", "R2w", "R3", "R3m", "R2", "NC"):
                    ix = R0 if neg == "R0" else g(pool, tool, neg)
                    if len(ix) and len(R4):
                        dr = S.wauc(z[R4], z[ix], R.w(R4, True), R.w(ix, True))
                        pt = S.wauc(z[R4], z[ix], np.ones((1, len(R4))), np.ones((1, len(ix))))[0]
                        m[f"auc:{pool}:{tool}:R4_vs_{neg}"] = (float(pt), dr)
        if len(halves):
            m["auc:frgcferet:halves_vs_R0"] = (float(S.wauc(z[halves], z[r0], np.ones((1, len(halves))),
                                                            np.ones((1, len(r0))))[0]),
                                               S.wauc(z[halves], z[r0], R.w(halves, True), R.w(r0, True)))
    # ---- neutral above smiling, within person
    for cell in ("frllm:bona", "mad22:bona"):
        ix = R.sel(cell, "0", "native")
        if not len(ix):
            continue
        by = {}
        for i in ix:
            by.setdefault(R.rows[i]["p1"], {})[R.rows[i]["expr"]] = z[i]
        per = sorted(p for p, d in by.items() if "03" in d and "08" in d)
        ind = np.array([1.0 if by[p]["03"] > by[p]["08"] else 0.5 if by[p]["03"] == by[p]["08"] else 0.0 for p in per])
        C = R.Df.C[:, [R.Df.pos[p] for p in per]]
        m[f"neutral_above_smiling:{cell}"] = (float(ind.mean()), (C * ind).sum(1) / np.maximum(C.sum(1), 1e-12))
    m.pop("_thr_frll_opencv", None)
    return m


def summarise(per_seed):
    """per_seed: [metrics dict] -> {name: dict(mean, ci, seeds)} (5-seed mean of points; interval of the per-draw
    5-seed mean)."""
    out = {}
    for k in per_seed[0]:
        pts = [d[k][0] for d in per_seed if k in d]
        drs = [d[k][1] for d in per_seed if k in d and d[k][1] is not None]
        out[k] = dict(mean=float(np.mean(pts)), ci=S.ci(np.mean(drs, 0)) if drs else None,
                      seeds=[round(float(p), 4) for p in pts])
    return out


def diff(A, B, k):
    if k not in A[0] or k not in B[0]:
        return None
    pa, pb = np.mean([d[k][0] for d in A]), np.mean([d[k][0] for d in B])
    da, db = np.mean([d[k][1] for d in A], 0), np.mean([d[k][1] for d in B], 0)
    return dict(diff=float(pb - pa), ci=S.ci(db - da))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--arms", default="a,b,bp,c,cr,d,e,d50,d500,a256,dplus")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--boot", action="store_true")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--dir", default=None, help="score folder (default OUT/heads[/smoke]); LoRA: OUT/lora_scores")
    ap.add_argument("--name", default=None, help="output tag (default smoke|full)")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = meta()
    R = Reader(rows, a.B)
    pos = {r["id"]: i for i, r in enumerate(rows)}
    hd = pathlib.Path(a.dir) if a.dir else K.OUT / ("heads/smoke" if a.smoke else "heads")
    res, seeds_csv, raw = {}, [], {}
    sets = [(arm, s) for arm in a.arms.split(",") for s in a.seeds.split(",")]
    for arm, s in sets + [("feref", None)]:
        f = hd / (f"{arm}_s{s}" + ("_boot" if a.boot else "") + ".npz") if arm != "feref" else K.OUT / "heads/feref.npz"
        if not f.exists():
            continue
        zf = np.load(f, allow_pickle=False)
        zi = {str(i): v for i, v in zip(zf["id"], zf["logit"])}
        z = np.array([zi.get(r["id"], np.nan) for r in rows], np.float64)
        if not np.isfinite(z).all():
            miss = [r["id"] for r, v in zip(rows, z) if not np.isfinite(v)]
            sys.exit(f"{f}: {len(miss)} test rows without a score, e.g. {miss[:3]}")
        m = one(R, z)
        raw.setdefault(arm, []).append(m)
        for k, (p, _) in m.items():
            seeds_csv.append(dict(arm=arm, seed=s or "", metric=k, value=round(float(p), 5)))
    for arm, ms in raw.items():
        res[arm] = summarise(ms)
    steps = {}
    keys = ("mean_eer:native:landmark7", "mean_eer:e7:landmark7", "mean_rise:landmark7", "mean_rise:diff7",
            "mean_eer:native:diff7", "mean_eer:native:gan3", "mean_rise:gan3", "flag:ar1eer:halves",
            "flag:ar1eer:r2w_opencv", "flag:ar1eer:r2w_facemorpher", "flag:r0_5pct:halves", "flag:r0_5pct:r2w_opencv",
            "flag:r0_5pct:r2w_facemorpher", "auc:frgcferet:opencv:R4_vs_R2w", "auc:frgcferet:facemorpher:R4_vs_R2w",
            "auc:frgcferet:opencv:R4_vs_R0", "auc:frgcferet:halves_vs_R0", "neutral_above_smiling:frllm:bona",
            "neutral_above_smiling:mad22:bona")
    for x, y, what in STEPS:
        if x in raw and y in raw:
            steps[f"{x}->{y}"] = dict(what=what, **{k: diff(raw[x], raw[y], k) for k in keys})
    fals = {}
    if "b" in raw and "c" in raw:
        dd = diff(raw["b"], raw["c"], "mean_eer:native:landmark7")
        fals["smddT_partner_eer_condition"] = dict(
            **dd, holds=bool(abs(dd["diff"]) < 1 and dd["ci"][0] <= 0 <= dd["ci"][1]),
            text="(c) - (b) mean native EER on the 7 landmark cells: |diff| < 1 point and interval includes 0")
    if "c" in raw and "d" in raw:
        dd = diff(raw["c"], raw["d"], "mean_eer:native:landmark7")
        fc = np.mean([m["flag:ar1eer:halves"][0] for m in raw["c"]])
        fd = np.mean([m["flag:ar1eer:halves"][0] for m in raw["d"]])
        fals["smddT_halves"] = dict(eer_d_minus_c=dd, fails_eer=bool(dd["diff"] > 5), flag_c=float(fc),
                                    flag_d=float(fd), halved=bool(fd <= 0.5 * fc), uninformative=bool(fc < 0.05),
                                    fails=bool(dd["diff"] > 5 or (fc >= 0.05 and fd > 0.5 * fc)))
    tag = (a.name or ("smoke" if a.smoke else "full")) + ("_boot" if a.boot else "")
    json.dump(dict(arms=res, steps=steps, falsifiers=fals, B=a.B,
                   n_rows=len(rows)), open(K.RES / f"p3_{tag}.json", "w"), indent=1)
    with open(K.RES / f"p3_{tag}_seeds.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arm", "seed", "metric", "value"])
        w.writeheader()
        w.writerows(seeds_csv)
    print(json.dumps(fals, indent=1))


if __name__ == "__main__":
    main()

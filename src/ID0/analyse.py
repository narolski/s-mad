"""ID0 analysis: every read of the prereg for one arm. CPU only, reads feature files, writes JSON + CSV.

  python3 -I analyse.py --arm landmark|glint|clip|dino|diffae [--B 2000] [--k 64]
Outputs experiments/ID0_identity-shrinkage-triage/arm_<arm>.json and contrasts_<arm>.csv.
"""
import argparse
import collections
import csv
import itertools
import json
import pathlib
import sys
import time

import numpy as np
from scipy.stats import norm, page_trend_test

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import id0_common as C  # noqa: E402
from iss import ISS, auc_fast  # noqa: E402

sys.path.insert(0, str(C.AR1_SRC))
import stats as ST  # noqa: E402  (AR1's stats.py, unchanged: a41_read.Draw, a36_read.wauc)

B_SEED = [20261111, 1]


# ----------------------------------------------------------------------------------------------- data
def meta_items():
    return {r["key"]: r for r in C.rows(C.OUT / "items.csv")}


def fit_rows():
    return C.rows(C.OUT / "fit.csv")


def valbad(p):
    """True if p is an FRGC/FERET person reserved by is_val."""
    db, s = p.split(":", 1)
    return db in ("frgc", "feret") and C.is_val(s)


# ----------------------------------------------------------------------------------------------- landmark arm
def procrustes_to(X, ref):
    """X (106,2) -> aligned to ref (unit centroid size, centred): translation, scale, rotation (no reflection)."""
    Xc = X - X.mean(0)
    Xc = Xc / np.sqrt((Xc ** 2).sum())
    U, _, Vt = np.linalg.svd(Xc.T @ ref)
    d = np.sign(np.linalg.det(U @ Vt))
    D = np.diag([1, d])
    R = U @ D @ Vt
    return Xc @ R


def gpa(shapes, it=20):
    ref = shapes[0] - shapes[0].mean(0)
    ref = ref / np.sqrt((ref ** 2).sum())
    for _ in range(it):
        A = np.array([procrustes_to(s, ref) for s in shapes])
        new = A.mean(0)
        new = new - new.mean(0)
        new = new / np.sqrt((new ** 2).sum())
        if np.abs(new - ref).max() < 1e-10:
            break
        ref = new
    return ref


def landmark_features():
    """-> keys, X (n x 212), meta dict key -> row (same fields as items.csv), fit keys/pids."""
    fit = fit_rows()
    T = {}
    for r in fit:
        T[r["key"]] = C.read_tem(r["tem"])
    ref = gpa([T[r["key"]] for r in fit])
    meta = {}
    shapes = {}

    def put(key, group, shape, p1, p2=None, w2=0.0, src1="", src2="", expr=""):
        shapes[key] = shape
        meta[key] = dict(key=key, group=group, p1=p1, p2=p2 or p1, w2=w2, src1=src1, src2=src2, expr=expr, extra="")

    for pool, fn in (("frgcferet", "pool_m.csv"), ("frll", "pool_frll_m.csv")):
        rs = C.rows(C.AR1_OUT / fn)
        S = {r["pid"]: C.read_tem(pathlib.Path(r["S"]).with_suffix(".tem")) for r in rs}
        for r in rs:
            h, b = r["pid"], r["B_pid"]
            H = C.read_tem(pathlib.Path(r["H"]).with_suffix(".tem"))
            M = C.read_tem(pathlib.Path(r["M"]).with_suffix(".tem"))
            put(f"L|{pool}|src|{h}|H", f"ar1src_{pool}_H", H, h)
            put(f"L|{pool}|src|{h}|S", f"ar1src_{pool}_S", S[h], h)
            s1, s2 = f"L|{pool}|src|{h}|H", f"L|{pool}|src|{h}|S"
            put(f"L|{pool}|R3|{h}", f"L_{pool}_R3", (H + S[h]) / 2, h, h, 0.5, s1, s2)
            put(f"L|{pool}|R3m|{h}", f"L_{pool}_R3m", (H + M) / 2, h, h, 0.5, s1, s1)
            put(f"L|{pool}|R4|{h}", f"L_{pool}_R4", (H + S[b]) / 2, h, b, 0.5, s1, f"L|{pool}|src|{b}|S")
            for m in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
                put(f"L|{pool}|m{int(round(m * 100)):03d}|{h}", f"L_{pool}_m{int(round(m * 100)):03d}",
                    (1 - m) * H + m * S[b], h, b, m, s1, f"L|{pool}|src|{b}|S")
    # FRLL single shapes and benchmark pair shapes (exact means of the two contributors' neutral shapes)
    fr = {p.stem: C.read_tem(p) for p in sorted((C.AR1_OUT / "frll_src").glob("*.tem"))}
    for st, s in fr.items():
        put(f"L|frllsrc|{st}", "frllsrc", s, f"frll:{st[:3]}", expr=st[4:])
    for fam in ("opencv", "facemorpher", "amsl", "webmorph", "stylegan"):
        for p in sorted((C.FRLLM_RAW / f"morph_{fam}").glob("*.jpg")):
            a, b = p.stem.split("_")[:2]
            if f"{a}_03" in fr and f"{b}_03" in fr:
                put(f"L|frllm|{fam}|{p.stem}", f"L_frllm_{fam}", (fr[f"{a}_03"] + fr[f"{b}_03"]) / 2, f"frll:{a}",
                    f"frll:{b}", 0.5, f"L|frllsrc|{a}_03", f"L|frllsrc|{b}_03", "nn")
    for fam in ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph"):
        for p in sorted((C.MAD22_RAW / fam).iterdir()):
            t = p.stem.split("-vs-")
            if len(t) != 2:
                continue
            a, b = t
            if a in fr and b in fr:
                put(f"L|mad22|{fam}|{p.stem}", f"L_mad22_{fam}", (fr[a] + fr[b]) / 2, f"frll:{a[:3]}", f"frll:{b[:3]}",
                    0.5, f"L|frllsrc|{a}", f"L|frllsrc|{b}", a[4:] + b[4:])
    for r in fit:
        shapes[r["key"]] = T[r["key"]]
    keys = list(shapes)
    X = np.array([procrustes_to(shapes[k], ref).ravel() for k in keys])
    return keys, X, meta, [r["key"] for r in fit], [r["pid"] for r in fit]


# ----------------------------------------------------------------------------------------------- image arms
FEATFILE = {"clip": "clip_cd.npz", "dino": "dino_dn.npz", "glint": "glint_gl.npz", "diffae": "diffae.npz"}


def image_features(arm):
    z = np.load(C.OUT / "feat" / FEATFILE[arm])
    keys = [str(k) for k in z["keys"]]
    X = z["feat"].astype(np.float64)
    found = z["found"]
    if arm == "glint":
        X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
        ex = C.existing_glint()
        new = set(keys)
        add = [k for k in ex if k not in new]
        keys = keys + add
        X = np.concatenate([X, np.array([ex[k] for k in add])])
        found = np.concatenate([found, np.ones(len(add), bool)])
    meta = meta_items()
    fit = fit_rows()
    fk = {r["key"]: r["pid"] for r in fit}
    idx = {k: i for i, k in enumerate(keys)}
    fit_keys = [k for k in fk if k in idx and found[idx[k]]]
    return keys, X, found, meta, fit_keys, [fk[k] for k in fit_keys]


def a46_features(kind):
    """existing a46 feature file: kind 'emb' (glintr100) or 'clip' (timm CLIP ViT-L/14 pooled, fp32)."""
    z = np.load(C.A46_FEAT)
    keys = [str(k) for k in z["keys"]]
    X = z[kind].astype(np.float64)
    if kind == "emb":
        X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    meta = {}
    for k in keys:
        g, n = k.split("|", 1)
        p1 = p2 = None
        w2, expr, s1, s2 = 0.0, "", "", ""
        if n.startswith("morph_"):
            t = n.split("_")
            p1, p2, w2, expr = f"frll:{t[1]}", f"frll:{t[4]}", 0.5, t[2] + t[5]
            s1, s2 = f"a46|raw|{t[1]}_{t[2]}", f"a46|raw|{t[4]}_{t[5]}"
        elif g.startswith("pub_") or g == "cross":
            a, b = n.split("_")[:2]
            p1, p2, w2 = f"frll:{a}", f"frll:{b}", 0.5
            s1, s2 = f"a46|raw|{a}_03", f"a46|raw|{b}_03"
        elif n.endswith("_self"):
            a = n.split("_")[0]
            p1 = p2 = f"frll:{a}"
            w2, s1, s2 = 0.5, f"a46|raw|{a}_03", f"a46|raw|{a}_08"
        else:
            a = n.split("_")[0]
            p1 = p2 = f"frll:{a}"
            s1 = s2 = f"a46|raw|{n}"
        meta[f"a46|{k}"] = dict(key=f"a46|{k}", group=f"a46_{g}", p1=p1, p2=p2, w2=w2, expr=expr, src1=s1, src2=s2,
                                extra="")
    return [f"a46|{k}" for k in keys], X, meta


# ----------------------------------------------------------------------------------------------- statistics
class Reader:
    def __init__(self, keys, X, meta, model, B):
        self.keys = keys
        self.idx = {k: i for i, k in enumerate(keys)}
        self.X = X
        self.meta = meta
        self.M = model
        self.S = model.scores(X)
        self.groups = collections.defaultdict(list)
        for k in keys:
            m = meta.get(k)
            if m is None:
                continue
            if valbad(m["p1"]) or valbad(m["p2"]):
                continue
            self.groups[m["group"]].append(k)
        pers = sorted({meta[k][f] for k in keys if k in meta for f in ("p1", "p2")})
        self.D = ST.Draw(pers, B, B_SEED)
        self.extra = {}

    def pp(self, ks):
        return [(self.meta[k]["p1"],) if self.meta[k]["p1"] == self.meta[k]["p2"] else
                (self.meta[k]["p1"], self.meta[k]["p2"]) for k in ks]

    def sc(self, ks, score="iss"):
        if score in self.extra:
            return np.array([self.extra[score][self.idx[k]] for k in ks])
        return self.S[score][[self.idx[k] for k in ks]]

    def con(self, neg, pos, score="iss", negf=None, posf=None):
        nk = [k for k in self.groups.get(neg, []) if negf is None or negf(self.meta[k])]
        pk = [k for k in self.groups.get(pos, []) if posf is None or posf(self.meta[k])]
        if not nk or not pk:
            return None
        a, ci = ST.wauc_ci(self.D, self.sc(pk, score), self.pp(pk), self.sc(nk, score), self.pp(nk))
        return dict(auc=round(a, 4), ci95=[round(x, 4) for x in ci], n_neg=len(nk), n_pos=len(pk))

    def vec(self, k):
        return self.X[self.idx[k]]

    def cpairs(self, group):
        """contributor similarity in the arm's own identity space for a group's two-person items."""
        ks = [k for k in self.groups.get(group, []) if self.meta[k]["src1"] in self.idx and self.meta[k]["src2"] in self.idx
              and self.meta[k]["p1"] != self.meta[k]["p2"]]
        if not ks:
            return None
        A = np.array([self.vec(self.meta[k]["src1"]) for k in ks])
        Bm = np.array([self.vec(self.meta[k]["src2"]) for k in ks])
        c = self.M.c_pair(A, Bm)
        return dict(n=len(ks), median=round(float(np.median(c)), 4), q10=round(float(np.quantile(c, .1)), 4),
                    q90=round(float(np.quantile(c, .9)), 4))

    def fidelity(self, group, unit=False):
        ks = [k for k in self.groups.get(group, []) if self.meta[k]["src1"] in self.idx and self.meta[k]["src2"] in self.idx]
        if not ks:
            return None
        out, base = [], []
        for k in ks:
            w = float(self.meta[k]["w2"])
            a, b, x = self.vec(self.meta[k]["src1"]), self.vec(self.meta[k]["src2"]), self.vec(k)
            if unit:
                t = (1 - w) * a + w * b
                t = t / np.linalg.norm(t)
                out.append(float(x @ t))
                base.append(float(x @ a))
            else:
                t = (1 - w) * a + w * b - self.M.m
                xc, ac = x - self.M.m, a - self.M.m
                out.append(float(xc @ t / (np.linalg.norm(xc) * np.linalg.norm(t) + 1e-12)))
                base.append(float(xc @ ac / (np.linalg.norm(xc) * np.linalg.norm(ac) + 1e-12)))
        q = lambda v: [round(float(np.quantile(v, x)), 4) for x in (0.25, 0.5, 0.75)]  # noqa: E731
        return dict(n=len(ks), F_q25_med_q75=q(out), cos_to_src1_q25_med_q75=q(base))


def wspearman(x, y, W):
    """weighted Spearman per bootstrap row of W (R x n): Pearson of weighted mid-ranks."""
    out = []
    ox, oy = np.argsort(x, kind="stable"), np.argsort(y, kind="stable")
    for w in W:
        rx = np.empty(len(x))
        cw = np.cumsum(w[ox])
        rx[ox] = cw - w[ox] / 2
        ry = np.empty(len(y))
        cw = np.cumsum(w[oy])
        ry[oy] = cw - w[oy] / 2
        sw = w.sum()
        if sw <= 0:
            out.append(np.nan)
            continue
        mx, my = (w * rx).sum() / sw, (w * ry).sum() / sw
        cov = (w * (rx - mx) * (ry - my)).sum()
        vx, vy = (w * (rx - mx) ** 2).sum(), (w * (ry - my) ** 2).sum()
        out.append(cov / np.sqrt(vx * vy) if vx > 0 and vy > 0 else np.nan)
    return np.array(out)


def spearman_ci(R, ks, x, y):
    from scipy.stats import spearmanr
    rho = float(spearmanr(x, y).statistic)
    W = ST.weights(R.D, R.pp(ks))
    rep = wspearman(np.asarray(x, float), np.asarray(y, float), W)
    return dict(rho=round(rho, 4), ci95=[round(v, 4) for v in ST.ci(rep)], n=len(ks))


def page(R, groups, score="iss"):
    """Page trend test over levels (blocks = hosts present at every level); mean score per level."""
    per = [{R.meta[k]["p1"]: R.sc([k], score)[0] for k in R.groups.get(g, [])} for g in groups]
    hosts = sorted(set.intersection(*[set(p) for p in per]))
    if len(hosts) < 5:
        return None
    data = np.array([[p[h] for p in per] for h in hosts])
    r = page_trend_test(data)
    lev = [dict(level=g, mean=round(float(data[:, i].mean()), 4)) for i, g in enumerate(groups)]
    return dict(hosts=len(hosts), L=float(r.statistic), p=float(r.pvalue), levels=lev,
                monotone_means=bool(np.all(np.diff(data.mean(0)) > 0)))


def cos_glint_lookup():
    """glintr100 cosine of contributor source photos per item key (for the shrink law): AR1 cos_HB; FRLL photos from
    the a46 raw gallery; H3 from the CASIA crops' glint embeddings (feat/h3crops_glint.npz) if present."""
    z = np.load(C.A46_FEAT)
    raw = {str(k).split("|", 1)[1]: e / np.linalg.norm(e) for k, e in zip(z["keys"], z["emb"]) if str(k).startswith("raw|")}
    cos = {}
    for pool, fn in (("frgcferet", "pool_m.csv"), ("frll", "pool_frll_m.csv")):
        for r in C.rows(C.AR1_OUT / fn):
            cos[(pool, r["pid"])] = float(r["cos_HB"])
    h3 = {}
    p = C.OUT / "feat" / "h3crops_glint.npz"
    if p.exists():
        q = np.load(p)
        h3 = {str(k): e for k, e in zip(q["folder"], q["emb"])}
    return raw, cos, h3


def item_cos(m, raw, cos, h3, pool_hint=None):
    k = m["key"]
    if k.startswith(("ar1|", "ar1g|", "L|frgcferet", "L|frll|")):
        pool = "frll" if ("|frll|" in k) else "frgcferet"
        return cos.get((pool, m["p1"]))
    if m["group"].startswith("sg3_h3_sg3"):
        a, b = m["extra"].split(";")
        if a in h3 and b in h3:
            return float(h3[a] @ h3[b])
        return None
    s1, s2 = m["src1"].split("|")[-1], m["src2"].split("|")[-1]
    if s1 in raw and s2 in raw:
        return float(raw[s1] @ raw[s2])
    return None


# ----------------------------------------------------------------------------------------------- the reads
def contrasts_for(arm):
    """(label, neg group, pos group, kind) ; kind in control / one_vs_morph / same_vs_morph / photo_vs_morph / other."""
    L = []
    if arm == "landmark":
        for pool in ("frgcferet", "frll"):
            L += [(f"{pool} exact R0 vs R4", f"ar1src_{pool}_H", f"L_{pool}_R4", "photo_vs_morph"),
                  (f"{pool} exact R0 vs R3 (= R2w shape)", f"ar1src_{pool}_H", f"L_{pool}_R3", "photo_vs_same"),
                  (f"{pool} exact R3 vs R4 (R2w vs R4 shape)", f"L_{pool}_R3", f"L_{pool}_R4", "one_vs_morph"),
                  (f"{pool} exact R3m vs R4", f"L_{pool}_R3m", f"L_{pool}_R4", "same_vs_morph"),
                  (f"{pool} exact R0 vs R3m", f"ar1src_{pool}_H", f"L_{pool}_R3m", "photo_vs_same")]
        for fam in ("opencv", "facemorpher", "amsl", "webmorph", "stylegan"):
            L.append((f"FRLL photo (neutral) vs exact pair mean, FRLL-Morphs {fam} pairs", "frllsrc_03", f"L_frllm_{fam}",
                      "photo_vs_morph"))
        for fam in ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph"):
            L.append((f"FRLL photo (all) vs exact pair mean, MAD22 {fam} pairs", "frllsrc", f"L_mad22_{fam}",
                      "photo_vs_morph"))
        return L
    for pool in ("frgcferet", "frll"):
        for tool in ("opencv", "facemorpher"):
            g = f"ar1_{pool}_{tool}"
            L += [(f"{pool} {tool} R0 vs R4", f"ar1src_{pool}_H", f"{g}_R4", "photo_vs_morph"),
                  (f"{pool} {tool} R2 vs R4", f"{g}_R2", f"{g}_R4", "one_vs_morph"),
                  (f"{pool} {tool} R2w vs R4", f"{g}_R2w", f"{g}_R4", "one_vs_morph"),
                  (f"{pool} {tool} R3 vs R4", f"{g}_R3", f"{g}_R4", "same_vs_morph"),
                  (f"{pool} {tool} R3m vs R4", f"{g}_R3m", f"{g}_R4", "same_vs_morph"),
                  (f"{pool} {tool} R2w vs R3", f"{g}_R2w", f"{g}_R3", "one_vs_same"),
                  (f"{pool} {tool} R0 vs R2w", f"ar1src_{pool}_H", f"{g}_R2w", "photo_vs_one"),
                  (f"{pool} {tool} R0 vs R3", f"ar1src_{pool}_H", f"{g}_R3", "photo_vs_same"),
                  (f"{pool} {tool} NC vs R3 (negative control: R3 positive)", f"{g}_NC", f"{g}_R3", "negctl")]
    for fam in ("opencv", "facemorpher"):
        L.append((f"FRLL native vs published {fam} morph frames", "e7_native", f"bench_{fam}_R4f", "photo_vs_morph"))
    for st, fam in C.E7_PRIMARY + C.E7_DESC:
        L.append((f"control native vs E7 {fam}", "e7_native", f"e7_{fam}",
                  "control" if (st, fam) in C.E7_PRIMARY else "control_desc"))
    a = "a43"
    L += [(f"MorDIFF stored E vs B20", f"{a}_E", f"{a}_B20", "photo_vs_morph"),
          (f"MorDIFF stored D20 vs B20", f"{a}_D20", f"{a}_B20", "one_vs_morph"),
          (f"MorDIFF stored C20 vs B20", f"{a}_C20", f"{a}_B20", "same_vs_morph"),
          (f"MorDIFF stored D20 vs C20", f"{a}_D20", f"{a}_C20", "one_vs_same"),
          (f"MorDIFF stored E vs D20", f"{a}_E", f"{a}_D20", "photo_vs_one"),
          (f"MorDIFF stored D vs B", f"{a}_D", f"{a}_B", "one_vs_morph"),
          (f"MorDIFF stored C vs B", f"{a}_C", f"{a}_B", "same_vs_morph"),
          (f"MorDIFF stored E vs B", f"{a}_E", f"{a}_B", "photo_vs_morph"),
          (f"MorDIFF stored E vs A (published)", f"{a}_E", f"{a}_A", "photo_vs_morph"),
          (f"MorDIFF stored D20 vs A (published)", f"{a}_D20", f"{a}_A", "one_vs_morph"),
          (f"MorDIFF stored D vs A (published)", f"{a}_D", f"{a}_A", "one_vs_morph")]
    if arm == "diffae":
        L += [("MorDIFF DiffAE-native a256 vs B20", "dae_a256", "dae_B20", "photo_vs_morph"),
              ("MorDIFF DiffAE-native D20 vs B20", "dae_D20", "dae_B20", "one_vs_morph"),
              ("MorDIFF DiffAE-native C20 vs B20", "dae_C20", "dae_B20", "same_vs_morph"),
              ("MorDIFF DiffAE-native D20 vs C20", "dae_D20", "dae_C20", "one_vs_same"),
              ("MorDIFF DiffAE-native a256 vs D20", "dae_a256", "dae_D20", "photo_vs_one"),
              ("MorDIFF DiffAE-native a256 vs B (100 steps)", "dae_a256", "dae_B", "photo_vs_morph")]
    L += [("StyleGAN3 h3_bona vs h3_sg3", "sg3_h3_bona", "sg3_h3_sg3", "one_vs_morph"),
          ("StyleGAN3 a37spread vs h3_sg3", "sg3_a37spread", "sg3_h3_sg3", "one_vs_morph"),
          ("StyleGAN3 FRLL native photo vs h3_sg3 (cross-pool)", "e7_native", "sg3_h3_sg3", "photo_vs_morph_xpool")]
    if arm in ("glint", "clip"):
        L += [("a46 rec vs published MorDIFF", "a46_rec", "a46_pub_mordiff", "one_vs_morph"),
              ("a46 rec vs published DiM-C", "a46_rec", "a46_pub_dim_c", "one_vs_morph"),
              ("a46 rec vs published Greedy-DiM", "a46_rec", "a46_pub_greedy_dim", "one_vs_morph"),
              ("a46 rec vs published Greedy-DiM-S", "a46_rec", "a46_pub_greedy_dim_s", "one_vs_morph"),
              ("a46 a43_D vs a43_B", "a46_a43_D", "a46_a43_B", "one_vs_morph"),
              ("a46 a256 vs rec (negative control: aligner copy vs reconstruction)", "a46_a256", "a46_rec", "negctl"),
              ("a46 native vs E7 mordiff", "a46_native", "a46_e7_mordiff", "control_desc"),
              ("a46 native vs E7 dim_c", "a46_native", "a46_e7_dim_c", "control_desc")]
    return L


def dose_groups(arm):
    if arm == "landmark":
        return {f"exact dose {pool}": [f"L_{pool}_m{m:03d}" for m in (0, 10, 20, 30, 40, 50)] for pool in ("frgcferet", "frll")}
    return {"FaceMorpher graded m000-m050": [f"ar1g_m{m:03d}" for m in (0, 10, 20, 30, 40, 50)]}


def shrink_sets(arm):
    if arm == "landmark":
        return ["L_frgcferet_R4", "L_frll_R4", "L_frllm_opencv", "L_frllm_facemorpher"]
    s = ["ar1_frgcferet_opencv_R4", "ar1_frgcferet_facemorpher_R4", "ar1g_pooled", "a43_B20", "a43_B", "a43_A",
         "bench_opencv_R4f", "bench_facemorpher_R4f", "sg3_h3_sg3"]
    if arm == "diffae":
        s += ["dae_B20", "dae_B"]
    if arm in ("glint", "clip"):
        s += ["a46_pub_mordiff", "a46_pub_dim_c", "a46_pub_greedy_dim"]
    return s


def run(arm, B, kmax, out_dir):
    t0 = time.time()
    res = dict(arm=arm, prereg="experiments/ID0_identity-shrinkage-triage/prereg.md")
    if arm == "landmark":
        keys, X, meta, fk, fp = landmark_features()
        for k in keys:
            if k.startswith("L|frllsrc|"):
                pass
        # split FRLL singles by expression for the FRLL-Morphs (neutral) contrasts
        for k in list(meta):
            if meta[k]["group"] == "frllsrc" and meta[k]["expr"] == "03":
                meta[k + "#03"] = dict(meta[k], key=k + "#03", group="frllsrc_03")
        idx = {k: i for i, k in enumerate(keys)}
        extra_keys = [k for k in meta if k.endswith("#03")]
        X = np.concatenate([X, X[[idx[k[:-3]] for k in extra_keys]]])
        keys = keys + extra_keys
        found = np.ones(len(keys), bool)
    else:
        keys, X, found, meta, fk, fp = image_features(arm)
        if arm in ("glint", "clip"):
            k2, X2, m2 = a46_features("emb" if arm == "glint" else "clip")
            keys, X = keys + k2, np.concatenate([X, X2])
            meta.update(m2)
            found = np.concatenate([found, np.ones(len(k2), bool)])
    idx = {k: i for i, k in enumerate(keys)}
    Xfit = X[[idx[k] for k in fk]]
    model = ISS(Xfit, fp, kmax=kmax)
    res["fit"] = model.summary()
    res["fit"]["photos"] = len(fk)
    res["found_share_items"] = float(found.mean())
    meta = {k: v for k, v in meta.items() if k in idx and found[idx[k]]}
    R = Reader(keys, X, meta, model, B)
    res["excluded_is_val_items"] = sum(1 for k, m in meta.items() if valbad(m["p1"]) or valbad(m["p2"]))
    # graded pooled group for the shrink law
    R.groups["ar1g_pooled"] = [k for g in ("ar1g_m010", "ar1g_m020", "ar1g_m030", "ar1g_m040", "ar1g_m050")
                               for k in R.groups.get(g, [])]
    # ---- genuine-only in-domain virtual check (descriptive; added, not in prereg): 5 folds by person
    res["virtual_in_domain"] = virtual_check(Xfit, fp, kmax, unit=(arm == "glint"))
    # ---- predicted ceiling curve
    res["ceiling_curve"] = [dict(c=c, closed=round(model.pred_closed(c), 4), spectrum=round(model.pred_spectrum(c, 100000), 4))
                            for c in np.round(np.arange(0, 1.0, 0.1), 1).tolist()]
    # ---- contrasts
    rows = []
    for lab, neg, pos, kind in contrasts_for(arm):
        for score in ("iss", "typ", "ses"):
            r = R.con(neg, pos, score)
            if r is None:
                continue
            row = dict(label=lab, kind=kind, score=score, neg=neg, pos=pos, **r)
            if score == "iss" and kind.startswith(("photo_vs_morph", "one_vs_morph", "same_vs_morph")):
                cp = R.cpairs(pos)
                if cp:
                    row["c_arm_median"] = cp["median"]
                    row["c_arm_q10_q90"] = [cp["q10"], cp["q90"]]
                    row["pred_closed"] = round(model.pred_closed(max(cp["median"], 0.0)), 4)
                    row["pred_spectrum"] = round(model.pred_spectrum(max(cp["median"], 0.0), 100000), 4)
                row["pred_closed_c0"] = round(model.pred_closed(0.0), 4)
            rows.append(row)
    res["contrasts"] = rows
    # ---- controls verdict
    ctl = [r for r in rows if r["kind"] == "control" and r["score"] == "iss"]
    res["control_primary_iss"] = {r["label"]: r["auc"] for r in ctl}
    res["control_clean_045_055"] = (all(0.45 <= r["auc"] <= 0.55 for r in ctl) if ctl else None)
    # ---- dose
    res["dose"] = {}
    for name, gs in dose_groups(arm).items():
        d = page(R, gs, "iss")
        if d:
            d["auc_vs_m000"] = {g: R.con(gs[0], g, "iss") for g in gs[1:]}
            res["dose"][name] = d
    if arm == "glint":
        res["geo0"] = geo0(R, Xfit, fp, B)
        R.extra["oracle"] = oracle_scores(R)
    # ---- shrink law
    raw, cos, h3 = cos_glint_lookup()
    res["shrink_law"] = {}
    res["shrink_law_power"] = {}
    for g in shrink_sets(arm):
        ks = [k for k in R.groups.get(g, []) if R.meta[k]["p1"] != R.meta[k]["p2"]]
        Ls, kk = [], []
        for k in ks:
            c = item_cos(R.meta[k], raw, cos, h3)
            if c is None:
                continue
            w = float(R.meta[k]["w2"])
            Ls.append(2 * w * (1 - w) * (1 - c))
            kk.append(k)
        if len(kk) < 10:
            continue
        nn = [i for i, k in enumerate(kk) if R.meta[k]["expr"] in ("0303", "nn")]
        for score in (["iss", "head", "oracle"] if arm == "glint" else ["iss"]):
            x = R.sc(kk, score)
            ok = np.isfinite(x)
            if ok.sum() < 10:
                continue
            tgt = res["shrink_law"] if score != "oracle" else res["shrink_law_power"]
            lab = g if score == "iss" else f"{g} [{score}]"
            tgt[lab] = spearman_ci(R, [k for k, o in zip(kk, ok) if o], x[ok], np.array(Ls)[ok])
            if 10 <= len(nn) < len(kk):
                sel = [i for i in nn if ok[i]]
                tgt[lab + " (neutral-neutral)"] = spearman_ci(R, [kk[i] for i in sel], x[sel], [Ls[i] for i in sel])
    # ---- fidelity / linearity (image arms) and c per set
    res["fidelity"] = {}
    res["c_arm"] = {}
    for g in sorted(R.groups):
        if g.startswith(("ar1_", "ar1g_m", "a43_B", "a43_C", "a43_A", "dae_B", "dae_C", "dae_D", "a43_D", "bench_",
                         "a46_pub", "a46_a43", "a46_cross", "a46_self", "a46_rec", "L_")):
            if arm != "landmark":
                f = R.fidelity(g, unit=(arm == "glint"))
                if f:
                    res["fidelity"][g] = f
            cp = R.cpairs(g)
            if cp:
                res["c_arm"][g] = cp
    res["seconds"] = round(time.time() - t0, 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out_dir / f"arm_{arm}.json", "w"), indent=1)
    with open(out_dir / f"contrasts_{arm}.csv", "w", newline="") as f:
        cols = ["label", "kind", "score", "auc", "ci95", "n_neg", "n_pos", "c_arm_median", "pred_closed", "pred_spectrum",
                "pred_closed_c0"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return res


def oracle_scores(R):
    """reference-based oracle 1 - cos(e_built, e_ref) (idea 1's power check): AR1 frgcferet = the host's independent
    reference R; AR1 FRLL = the host's other-expression photo S; FRLL benchmark / A43 / a46 morphs = contributor A's
    other-expression FRLL photo (a46 raw gallery); H3 = contributor A's source crop (labelled source-photo reference)."""
    raw, _, h3 = cos_glint_lookup()
    o = np.full(len(R.keys), np.nan)
    for k, m in R.meta.items():
        if m["p1"] == m["p2"]:
            continue
        e = R.vec(k)
        ref = None
        if k.startswith(("ar1|frgcferet", "ar1g|")):
            rk = f"ar1src|frgcferet|{m['p1']}|R"
            ref = R.vec(rk) if rk in R.idx else None
        elif k.startswith("ar1|frll"):
            rk = f"ar1src|frll|{m['p1']}|S"
            ref = R.vec(rk) if rk in R.idx else None
        elif m["group"] == "sg3_h3_sg3":
            a = m["extra"].split(";")[0]
            ref = h3.get(a)
        else:
            s1 = m["src1"].split("|")[-1]
            if "_" in s1:
                a, e_ = s1.split("_")[:2]
                ref = raw.get(f"{a}_{'08' if e_ == '03' else '03'}")
        if ref is not None:
            o[R.idx[k]] = 1 - float(e @ (ref / np.linalg.norm(ref)))
    return o


def virtual_check(Xfit, fp, kmax, unit=False, seed=20261111, npairs=4000):
    """genuine-only: fit ISS on 4 folds of persons, score held-out singles vs held-out virtual midpoints of two held-out
    persons (same database). Pooled out-of-fold AUC, and per contributor-similarity (c_pair) tercile."""
    pers = sorted(set(fp))
    r = np.random.default_rng(seed)
    r.shuffle(pers)
    fold = {p: i % 5 for i, p in enumerate(pers)}
    fp = np.array(fp)
    S, M, Cs = [], [], []
    for f in range(5):
        tr = np.array([fold[p] != f for p in fp])
        te = ~tr
        mdl = ISS(Xfit[tr], list(fp[tr]), kmax=kmax)
        Xt, pt = Xfit[te], fp[te]
        S.append(mdl.scores(Xt)["iss"])
        db = np.array([p.split(":")[0] for p in pt])
        ia, ib = [], []
        while len(ia) < npairs // 5:
            i, j = r.integers(len(pt), size=2)
            if pt[i] != pt[j] and db[i] == db[j]:
                ia.append(i)
                ib.append(j)
        V = (Xt[ia] + Xt[ib]) / 2
        if unit:
            V = V / np.linalg.norm(V, axis=1, keepdims=True)
        M.append(mdl.scores(V)["iss"])
        Cs.append(mdl.c_pair(Xt[ia], Xt[ib]))
    S, M, Cs = np.concatenate(S), np.concatenate(M), np.concatenate(Cs)
    out = dict(auc_single_vs_virtual_midpoint=round(auc_fast(M, S), 4), n_single=len(S), n_virtual=len(M),
               note="descriptive, genuine-only; added after the prereg (not a decision quantity)")
    qs = np.quantile(Cs, [1 / 3, 2 / 3])
    for lo, hi, name in ((-9, qs[0], "c low tercile"), (qs[0], qs[1], "c mid"), (qs[1], 9, "c high tercile")):
        sel = (Cs >= lo) & (Cs < hi)
        out[name] = dict(c_range=[round(float(Cs[sel].min()), 3), round(float(Cs[sel].max()), 3)],
                         auc=round(auc_fast(M[sel], S), 4))
    return out


# ----------------------------------------------------------------------------------------------- GEO-0 (FR arm)
def geo0(R, Xfit, fp, B):
    from sklearn.covariance import LedoitWolf
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    out = {}
    # (4) Lambda and ceiling
    mu = Xfit.mean(0)
    lw = LedoitWolf().fit(Xfit)
    Lam = float(np.sqrt(mu @ np.linalg.solve(lw.covariance_, mu)))
    out["Lambda"] = round(Lam, 4)
    out["Lambda_ridge_sensitivity"] = {}
    Sig = np.cov(Xfit.T)
    for rr in (1e-4, 1e-3, 1e-2):
        Sr = Sig + rr * np.trace(Sig) / len(Sig) * np.eye(len(Sig))
        out["Lambda_ridge_sensitivity"][str(rr)] = round(float(np.sqrt(mu @ np.linalg.solve(Sr, mu))), 4)
    kap = lambda c: np.sqrt(2 / (1 + c))  # noqa: E731
    # twin cosine from the fit set (two photos of one person), median
    g = collections.defaultdict(list)
    for i, p in enumerate(fp):
        g[p].append(i)
    tw = [float(Xfit[a] @ Xfit[b]) for ix in g.values() for a, b in itertools.combinations(ix, 2)]
    ctw = float(np.median(tw))
    out["twin_cos_fit_median"] = round(ctw, 4)
    out["ceiling_table"] = [dict(c=c, vs_photo=round(float(norm.cdf((kap(c) - 1) * Lam / np.sqrt(2))), 4),
                                 vs_twin=round(float(norm.cdf((kap(c) - kap(ctw)) * Lam / np.sqrt(2))), 4))
                            for c in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)]
    # (2) mean-direction gain
    u = mu / np.linalg.norm(mu)
    gains = {}
    for gname in sorted(R.groups):
        ks = [k for k in R.groups[gname] if R.meta[k]["src1"] in R.idx and R.meta[k]["src2"] in R.idx]
        if not ks or float(R.meta[ks[0]]["w2"]) == 0 and R.meta[ks[0]]["src1"] == R.meta[ks[0]]["src2"]:
            continue
        pb = np.array([R.vec(k) @ u for k in ks])
        ps = np.array([(R.vec(R.meta[k]["src1"]) @ u + R.vec(R.meta[k]["src2"]) @ u) / 2 for k in ks])
        cs = np.array([R.vec(R.meta[k]["src1"]) @ R.vec(R.meta[k]["src2"]) for k in ks])
        W = ST.weights(R.D, R.pp(ks))
        rep = (W * pb).sum(1) / (W * ps).sum(1)
        gains[gname] = dict(n=len(ks), gain=round(float(pb.mean() / ps.mean()), 4), ci95=[round(x, 4) for x in ST.ci(rep)],
                            cos_sources_median=round(float(np.median(cs)), 4),
                            kappa_pred_at_median_cos=round(float(kap(np.median(cs))), 4))
    out["gain"] = gains
    out["gain_predictions_verbatim"] = {"R4": 1.27, "R3": 1.03}
    # (3) virtual head
    pers = sorted(g)
    rng = np.random.default_rng(20261111)
    rng.shuffle(pers)
    fold = {p: i % 5 for i, p in enumerate(pers)}
    fpa = np.array(fp)
    db = np.array([p.split(":")[0] for p in fp])
    items = []  # (fold, vec, label, kind, cos)
    for f in range(5):
        ix = np.where([fold[p] == f for p in fp])[0]
        for i in ix:
            items.append((f, Xfit[i], 0, "single", np.nan))
        for p in [p for p in pers if fold[p] == f]:
            for a, b in itertools.combinations(g[p], 2):
                v = Xfit[a] + Xfit[b]
                items.append((f, v / np.linalg.norm(v), 0, "twin", float(Xfit[a] @ Xfit[b])))
        n = 0
        while n < 4000:
            a, b = rng.choice(ix, 2)
            if fpa[a] == fpa[b] or db[a] != db[b]:
                continue
            v = Xfit[a] + Xfit[b]
            items.append((f, v / np.linalg.norm(v), 1, "morph", float(Xfit[a] @ Xfit[b])))
            n += 1
    F = np.array([t[0] for t in items])
    V = np.array([t[1] for t in items])
    Y = np.array([t[2] for t in items])
    K = np.array([t[3] for t in items])
    Cc = np.array([t[4] for t in items])
    oof = np.zeros(len(items))

    def head():
        return LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000)

    for f in range(5):
        tr, te = F != f, F == f
        sc = StandardScaler().fit(V[tr])
        h = head().fit(sc.transform(V[tr]), Y[tr])
        oof[te] = h.decision_function(sc.transform(V[te]))
    out["virtual_head_in_domain"] = dict(
        auc_morph_vs_single_and_twin=round(auc_fast(oof[Y == 1], oof[Y == 0]), 4),
        auc_morph_vs_single=round(auc_fast(oof[Y == 1], oof[K == "single"]), 4),
        auc_morph_vs_twin=round(auc_fast(oof[Y == 1], oof[K == "twin"]), 4),
        n=dict(collections.Counter(K.tolist())),
        per_cos_bin_morph_vs_single={})
    for lo in (-0.2, 0.0, 0.1, 0.2, 0.3, 0.4):
        sel = (K == "morph") & (Cc >= lo) & (Cc < lo + (0.2 if lo < 0 else 0.1))
        if sel.sum() >= 30:
            out["virtual_head_in_domain"]["per_cos_bin_morph_vs_single"][f"[{lo:.1f},{lo + (0.2 if lo < 0 else 0.1):.1f})"] = \
                dict(n=int(sel.sum()), auc=round(auc_fast(oof[sel], oof[K == "single"]), 4))
    sc = StandardScaler().fit(V)
    h = head().fit(sc.transform(V), Y)
    R.extra["head"] = h.decision_function(sc.transform(R.X))
    heads = []
    for lab, neg, pos in (("AR1 frgcferet opencv R3 vs R4", "ar1_frgcferet_opencv_R3", "ar1_frgcferet_opencv_R4"),
                          ("AR1 frgcferet facemorpher R3 vs R4", "ar1_frgcferet_facemorpher_R3", "ar1_frgcferet_facemorpher_R4"),
                          ("AR1 frgcferet opencv host photo vs R4", "ar1src_frgcferet_H", "ar1_frgcferet_opencv_R4"),
                          ("AR1 frgcferet facemorpher host photo vs R4", "ar1src_frgcferet_H", "ar1_frgcferet_facemorpher_R4"),
                          ("AR1 frgcferet opencv R2w vs R4", "ar1_frgcferet_opencv_R2w", "ar1_frgcferet_opencv_R4"),
                          ("AR1 frll opencv R3 vs R4", "ar1_frll_opencv_R3", "ar1_frll_opencv_R4"),
                          ("a43_B vs a43_D (a46, 100 steps): D neg", "a46_a43_D", "a46_a43_B"),
                          ("a43 stored D vs B (100 steps, this run)", "a43_D", "a43_B"),
                          ("a43 stored D20 vs B20", "a43_D20", "a43_B20"),
                          ("a43 stored C20 vs B20", "a43_C20", "a43_B20"),
                          ("a46 rec vs published MorDIFF", "a46_rec", "a46_pub_mordiff"),
                          ("a46 rec vs published DiM-C", "a46_rec", "a46_pub_dim_c"),
                          ("a46 rec vs published Greedy-DiM", "a46_rec", "a46_pub_greedy_dim"),
                          ("StyleGAN3 h3_bona vs h3_sg3", "sg3_h3_bona", "sg3_h3_sg3"),
                          ("StyleGAN3 a37spread vs h3_sg3", "sg3_a37spread", "sg3_h3_sg3"),
                          ("control native vs E7 opencv", "e7_native", "e7_opencv"),
                          ("control native vs E7 facemorpher", "e7_native", "e7_facemorpher"),
                          ("control native vs E7 stylegan", "e7_native", "e7_stylegan"),
                          ("control native vs E7 mordiff", "e7_native", "e7_mordiff"),
                          ("control a46 native vs E7 mordiff", "a46_native", "a46_e7_mordiff"),
                          ("control rec vs aligner copy a256 (a46)", "a46_a256", "a46_rec")):
        r = R.con(neg, pos, "head")
        if r:
            heads.append(dict(label=lab, **r))
    out["virtual_head_applied"] = heads
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["landmark", "glint", "clip", "dino", "diffae"])
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--k", type=int, default=64)
    ap.add_argument("--out", default=str(C.RES))
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    res = run(a.arm, a.B, a.k, pathlib.Path(a.out))
    print(json.dumps({k: res[k] for k in ("fit", "control_clean_045_055", "virtual_in_domain", "seconds")}, indent=1))
    for r in res["contrasts"]:
        if r["score"] == "iss":
            print(f"{r['label'][:70]:70s} {r['auc']:.3f} [{r['ci95'][0]:.3f},{r['ci95'][1]:.3f}] "
                  f"pred {r.get('pred_closed', '-')}/{r.get('pred_spectrum', '-')} c={r.get('c_arm_median', '-')}")
    print(json.dumps(res["dose"], indent=1)[:3000])
    print(json.dumps(res["shrink_law"], indent=1)[:3000])


if __name__ == "__main__":
    main()

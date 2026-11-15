"""ID0 amendment 1 (prereg.md, 11 Nov 18:45, reason: independent review). Zero GPU, existing features only.

  python3 -I amend1.py --part a|b|c|d [--B 2000]
(a) ideal against realised per arm with a power flag; (b) learning curve and regulariser table of the glint
virtual head; (c) review hypothesis H-new-1 (per-host shift R4 - R2w vs loss of fine detail); (d) storage-history
rows for the glint read-outs. Outputs: experiments/ID0.../amend1_<part>.json (+ .csv for a, b, d).
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

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyse as A  # noqa: E402
import id0_common as C  # noqa: E402
from iss import ISS  # noqa: E402

ST = A.ST
SEED = 20261111
SMOKE = False


# ------------------------------------------------------------------------------------------------ loading
def load(arm, B):
    keys, X, found, meta, fk, fp = A.image_features(arm)
    if arm in ("glint", "clip"):
        k2, X2, m2 = A.a46_features("emb" if arm == "glint" else "clip")
        keys, X = keys + k2, np.concatenate([X, X2])
        meta.update(m2)
        found = np.concatenate([found, np.ones(len(k2), bool)])
    idx = {k: i for i, k in enumerate(keys)}
    Xfit = X[[idx[k] for k in fk]]
    model = ISS(Xfit, fp, kmax=64)
    meta = {k: v for k, v in meta.items() if k in idx and found[idx[k]]}
    R = A.Reader(keys, X, meta, model, B)
    return R, Xfit, fp


def geo0_items(Xfit, fp):
    """the registered geo0 virtual items, rebuilt exactly (same RNG sequence as analyse.geo0)."""
    g = collections.defaultdict(list)
    for i, p in enumerate(fp):
        g[p].append(i)
    pers = sorted(g)
    rng = np.random.default_rng(SEED)
    rng.shuffle(pers)
    fold = {p: i % 5 for i, p in enumerate(pers)}
    fpa = np.array(fp)
    db = np.array([p.split(":")[0] for p in fp])
    it = []  # fold, vec, label, kind, pa, pb
    for f in range(5):
        ix = np.where([fold[p] == f for p in fp])[0]
        for i in ix:
            it.append((f, Xfit[i], 0, "single", fp[i], fp[i]))
        for p in [p for p in pers if fold[p] == f]:
            for a, b in itertools.combinations(g[p], 2):
                v = Xfit[a] + Xfit[b]
                it.append((f, v / np.linalg.norm(v), 0, "twin", p, p))
        n = 0
        while n < 4000:
            a, b = rng.choice(ix, 2)
            if fpa[a] == fpa[b] or db[a] != db[b]:
                continue
            v = Xfit[a] + Xfit[b]
            it.append((f, v / np.linalg.norm(v), 1, "morph", fp[a], fp[b]))
            n += 1
    return it, fold, g, pers


def build_train(Xfit, fp, g, persons, nmorph, rng):
    ps = set(persons)
    ix = np.array([i for i, p in enumerate(fp) if p in ps])
    fpa = np.array(fp)
    db = np.array([p.split(":")[0] for p in fp])
    V, Y = [Xfit[i] for i in ix], [0] * len(ix)
    for p in persons:
        for a, b in itertools.combinations(g[p], 2):
            v = Xfit[a] + Xfit[b]
            V.append(v / np.linalg.norm(v))
            Y.append(0)
    n = 0
    while n < nmorph:
        a, b = rng.choice(ix, 2)
        if fpa[a] == fpa[b] or db[a] != db[b]:
            continue
        v = Xfit[a] + Xfit[b]
        V.append(v / np.linalg.norm(v))
        Y.append(1)
        n += 1
    return np.array(V), np.array(Y)


def fit_head(V, Y, kind="lr", Cc=1.0):
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler().fit(V)
    if kind == "lr":
        h = LogisticRegression(C=Cc, class_weight="balanced", max_iter=3000).fit(sc.transform(V), Y)
        return lambda Z: h.decision_function(sc.transform(np.asarray(Z)))
    h = MLPClassifier(hidden_layer_sizes=(256,), alpha=1e-2, max_iter=60, early_stopping=True,
                      random_state=0).fit(sc.transform(V), Y)
    return lambda Z: h.predict_proba(sc.transform(np.asarray(Z)))[:, 1]


def registered_head(Xfit, fp):
    it, _, _, _ = geo0_items(Xfit, fp)
    V = np.array([t[1] for t in it])
    Y = np.array([t[2] for t in it])
    return fit_head(V, Y)


def r4(x):
    return round(float(x), 4)


def ci(rep):
    return [r4(v) for v in ST.ci(rep)]


# ------------------------------------------------------------------------------------------------ (a)
def ideal_vectors(R, ks, unit, h3=None):
    out, kk = [], []
    for k in ks:
        m = R.meta[k]
        if m["group"] == "sg3_h3_sg3":
            a, b = m["extra"].split(";")
            if h3 is None or a not in h3 or b not in h3:
                continue
            v = h3[a] + h3[b]
        else:
            if m["src1"] not in R.idx or m["src2"] not in R.idx:
                continue
            w = float(m["w2"])
            v = (1 - w) * R.vec(m["src1"]) + w * R.vec(m["src2"])
        if unit:
            v = v / np.linalg.norm(v)
        out.append(v)
        kk.append(k)
    return np.array(out), kk


A_CONTRASTS = [
    ("AR1 OpenCV R4 vs host photo H", "ar1_frgcferet_opencv_R4", "ar1src_frgcferet_H"),
    ("AR1 OpenCV R4 vs R2w", "ar1_frgcferet_opencv_R4", "ar1_frgcferet_opencv_R2w"),
    ("AR1 OpenCV R4 vs R3", "ar1_frgcferet_opencv_R4", "ar1_frgcferet_opencv_R3"),
    ("AR1 FaceMorpher R4 vs host photo H", "ar1_frgcferet_facemorpher_R4", "ar1src_frgcferet_H"),
    ("AR1 FaceMorpher R4 vs R2w", "ar1_frgcferet_facemorpher_R4", "ar1_frgcferet_facemorpher_R2w"),
    ("AR1 FaceMorpher R4 vs R3", "ar1_frgcferet_facemorpher_R4", "ar1_frgcferet_facemorpher_R3"),
    ("AR1 OpenCV R3 (same person) vs host photo H", "ar1_frgcferet_opencv_R3", "ar1src_frgcferet_H"),
    ("AR1 OpenCV R3 (same person) vs R2w", "ar1_frgcferet_opencv_R3", "ar1_frgcferet_opencv_R2w"),
    ("A43 stored B20 vs E", "a43_B20", "a43_E"),
    ("A43 stored B20 vs D20", "a43_B20", "a43_D20"),
    ("A43 stored C20 (same person) vs E", "a43_C20", "a43_E"),
    ("A43 stored C20 (same person) vs D20", "a43_C20", "a43_D20"),
    ("DiffAE-native B20 vs a256", "dae_B20", "dae_a256"),
    ("DiffAE-native B20 vs D20", "dae_B20", "dae_D20"),
    ("DiffAE-native C20 (same person) vs a256", "dae_C20", "dae_a256"),
    ("DiffAE-native C20 (same person) vs D20", "dae_C20", "dae_D20"),
    ("H3 StyleGAN3 morph vs h3_bona", "sg3_h3_sg3", "sg3_h3_bona"),
    ("H3 StyleGAN3 morph vs a37spread", "sg3_h3_sg3", "sg3_a37spread"),
    ("published MorDIFF vs rec (a46)", "a46_pub_mordiff", "a46_rec"),
]


def part_a(B):
    rows = []
    h3 = None
    p = C.OUT / "feat" / "h3crops_glint.npz"
    if p.exists():
        q = np.load(p)
        h3 = {str(f): e / np.linalg.norm(e) for f, e in zip(q["folder"], q["emb"])}
    for arm in ("glint", "clip", "dino", "diffae"):
        t0 = time.time()
        R, Xfit, fp = load(arm, B)
        unit = arm == "glint"
        reads = {"ISS": lambda Z, M=R.M: M.scores(np.asarray(Z))["iss"]}
        if arm == "glint":
            hd = registered_head(Xfit, fp)
            u = Xfit.mean(0)
            u = u / np.linalg.norm(u)
            reads["virtual head"] = hd
            reads["mean-direction projection"] = lambda Z, u=u: np.asarray(Z) @ u
        for lab, pos, neg in A_CONTRASTS:
            pk = R.groups.get(pos, [])
            nk = R.groups.get(neg, [])
            if not pk or not nk:
                continue
            V, kk = ideal_vectors(R, pk, unit, h3 if arm == "glint" else None)
            if len(kk) < 10:
                continue
            Xr = np.array([R.vec(k) for k in kk])
            Xn = np.array([R.vec(k) for k in nk])
            pp, pn = R.pp(kk), R.pp(nk)
            for rn, fn in reads.items():
                sr, si, sn = fn(Xr), fn(V), fn(Xn)
                ar, cr = ST.wauc_ci(R.D, sr, pp, sn, pn)
                ai, cii = ST.wauc_ci(R.D, si, pp, sn, pn)
                rr = ST.wauc_rep(R.D, sr, pp, sn, pn)
                ri = ST.wauc_rep(R.D, si, pp, sn, pn)
                with np.errstate(divide="ignore", invalid="ignore"):
                    sh = (rr - 0.5) / (ri - 0.5)
                powered = bool(ai >= 0.65 and cii[0] > 0.60)
                rows.append(dict(arm=arm, contrast=lab, readout=rn, n_pos=len(kk), n_neg=len(nk),
                                 auc_real=r4(ar), ci_real=[r4(x) for x in cr], auc_ideal=r4(ai),
                                 ci_ideal=[r4(x) for x in cii],
                                 realised_share=r4((ar - 0.5) / (ai - 0.5)) if ai != 0.5 else None,
                                 ci_share=ci(sh) if powered else None, powered=powered))
        print(f"{arm} done in {time.time() - t0:.0f} s", flush=True)
    return rows


# ------------------------------------------------------------------------------------------------ (b)
def part_b(B):
    R, Xfit, fp = load("glint", B)
    it, fold, g, pers = geo0_items(Xfit, fp)
    F = np.array([t[0] for t in it])
    V = np.array([t[1] for t in it])
    Y = np.array([t[2] for t in it])
    K = np.array([t[3] for t in it])
    PP = [(t[4],) if t[4] == t[5] else (t[4], t[5]) for t in it]
    D = ST.Draw(sorted(set(fp)), B, [SEED, 1])

    def oof(variant):
        kind, Cc, N = variant
        s = np.zeros(len(it))
        for f in range(5):
            other = [p for p in pers if fold[p] != f]
            order = list(np.random.default_rng(SEED + f).permutation(other))
            use = order if N is None else order[:N]
            nm = int(round(16000 * len(use) / len(other)))
            Vt, Yt = build_train(Xfit, fp, g, use, nm, np.random.default_rng(SEED + 100 + f))
            te = F == f
            if kind == "proj":
                u = Xfit[[i for i, p in enumerate(fp) if p in set(use)]].mean(0)
                s[te] = V[te] @ (u / np.linalg.norm(u))
            else:
                s[te] = fit_head(Vt, Yt, kind, Cc)(V[te])
        out = {}
        for name, neg in (("morph vs single", K == "single"), ("morph vs single+twin", Y == 0)):
            pos = Y == 1
            a, c = ST.wauc_ci(D, s[pos], [PP[i] for i in np.where(pos)[0]], s[neg], [PP[i] for i in np.where(neg)[0]])
            out[name] = dict(auc=r4(a), ci95=[r4(x) for x in c])
        return out

    variants = [("lr", 1.0, 75), ("lr", 1.0, 150), ("lr", 1.0, 300), ("lr", 1.0, None)]
    variants += [("lr", c, None) for c in (0.001, 0.01, 0.1, 10.0, 100.0)]
    variants += [("proj", None, None), ("mlp", None, None)]
    if SMOKE:
        variants = [("lr", 1.0, 75), ("proj", None, None)]
    rows = []
    for v in variants:
        t0 = time.time()
        r = oof(v)
        row = dict(head=v[0], C=v[1], train_persons="all (about 620 per fold)" if v[2] is None else v[2], **{
            f"in_domain {k}": x for k, x in r.items()})
        # the same variant refitted on all fit persons, applied to the real contrasts
        if v[0] == "proj":
            u = Xfit.mean(0)
            fn = lambda Z, u=u / np.linalg.norm(u): np.asarray(Z) @ u  # noqa: E731
        elif v[2] is None:
            Vall = np.array([t[1] for t in it])
            fn = fit_head(Vall, Y, v[0], v[1] if v[1] else 1.0)
        else:
            fn = None
        if fn is not None:
            R.extra["v"] = fn(R.X)
            for lab, neg, pos in (("AR1 OpenCV R3 vs R4", "ar1_frgcferet_opencv_R3", "ar1_frgcferet_opencv_R4"),
                                  ("AR1 OpenCV H vs R4", "ar1src_frgcferet_H", "ar1_frgcferet_opencv_R4"),
                                  ("AR1 OpenCV R2w vs R4", "ar1_frgcferet_opencv_R2w", "ar1_frgcferet_opencv_R4"),
                                  ("a43_D vs a43_B (a46)", "a46_a43_D", "a46_a43_B"),
                                  ("control native vs E7 mordiff", "e7_native", "e7_mordiff")):
                x = R.con(neg, pos, "v")
                row[f"real {lab}"] = dict(auc=x["auc"], ci95=x["ci95"]) if x else None
        rows.append(row)
        print(v, f"{time.time() - t0:.0f} s", json.dumps(r), flush=True)
    return rows


# ------------------------------------------------------------------------------------------------ (c)
def part_c(B):
    cues = np.load("/mnt/t7/smad_next/AF0/cues/ar1.npz")
    names = list(cues["names"])
    ip = {r["id"]: r["path"] for r in C.rows("/mnt/t7/smad_next/AF0/lists/ar1.csv")}
    by = {ip[str(i)]: c for i, c in zip(cues["ids"], cues["cues"]) if str(i) in ip}
    jf, jw = names.index("lapvar_face"), names.index("lapvar")
    out = {}
    for arm in ("clip", "diffae", "dino"):
        R, _, _ = load(arm, B)
        ks, sh, sht, dl, dlw = [], [], [], [], []
        for k in R.groups.get("ar1_frgcferet_opencv_R4", []):
            h = R.meta[k]["p1"]
            k2 = f"ar1|frgcferet|opencv|R2w|{h}"
            if k2 not in R.idx or k2 not in R.meta:
                continue
            p4, p2 = R.meta[k]["path"], R.meta[k2]["path"]
            if p4 not in by or p2 not in by:
                continue
            ks.append(k)
            sh.append(R.S["iss"][R.idx[k]] - R.S["iss"][R.idx[k2]])
            sht.append(R.S["typ"][R.idx[k]] - R.S["typ"][R.idx[k2]])
            dl.append(np.log(by[p2][jf]) - np.log(by[p4][jf]))
            dlw.append(np.log(by[p2][jw]) - np.log(by[p4][jw]))
        out[arm] = dict(n=len(ks),
                        ISS_vs_lapvar_face=A.spearman_ci(R, ks, np.array(sh), np.array(dl)),
                        ISS_vs_lapvar_whole=A.spearman_ci(R, ks, np.array(sh), np.array(dlw)),
                        TYP_vs_lapvar_face=A.spearman_ci(R, ks, np.array(sht), np.array(dl)),
                        median_detail_loss_log=r4(np.median(dl)), median_shift_iss=r4(np.median(sh)))
        print(arm, json.dumps(out[arm]), flush=True)
    c, d = abs(out["clip"]["ISS_vs_lapvar_face"]["rho"]), abs(out["diffae"]["ISS_vs_lapvar_face"]["rho"])
    out["H-new-1"] = dict(clip_abs_rho=r4(c), diffae_abs_rho=r4(d), clip_ge_0_3=c >= 0.3, diffae_below_0_15=d < 0.15,
                          falsified_clip_below_0_1=c < 0.1)
    return out


# ------------------------------------------------------------------------------------------------ (d)
def part_d(B):
    R, Xfit, fp = load("glint", B)
    hd = registered_head(Xfit, fp)
    u = Xfit.mean(0)
    u = u / np.linalg.norm(u)
    reads = {"ISS": R.S["iss"], "virtual head": hd(R.X), "mean-direction projection": R.X @ u}
    nat = {k.split("|", 2)[2]: k for k in R.groups.get("e7_native", [])}
    rows = []
    for st, fam in C.E7_PRIMARY + C.E7_DESC:
        cks = [k for k in R.groups.get(f"e7_{fam}", []) if k.split("|", 2)[2] in nat]
        if not cks:
            continue
        nks = [nat[k.split("|", 2)[2]] for k in cks]
        a = np.array([R.vec(k) for k in nks])
        b = np.array([R.vec(k) for k in cks])
        W = ST.weights(R.D, R.pp(cks)).astype(int)
        row = dict(family=fam, primary=(st, fam) in C.E7_PRIMARY, n=len(cks),
                   cos_native_copy_median=r4(np.median((a * b).sum(1))))
        for rn, s in reads.items():
            sa = np.array([s[R.idx[k]] for k in nks])
            sb = np.array([s[R.idx[k]] for k in cks])
            au, ac = ST.wauc_ci(R.D, sb, R.pp(cks), sa, R.pp(nks))
            low = (sb < sa).astype(float)
            sdv = sa.std() if sa.std() > 0 else 1.0
            d = (sb - sa) / sdv
            rep_low = (W * low).sum(1) / np.maximum(W.sum(1), 1)
            rep_med = np.array([np.median(np.repeat(d, w)) if w.sum() else np.nan for w in W])
            row[rn] = dict(auc_copy_vs_native=r4(au), ci95=[r4(v) for v in ac], share_lower=r4(low.mean()),
                           share_lower_ci95=ci(rep_low), median_shift_sd=r4(np.median(d)), median_shift_ci95=ci(rep_med))
        rows.append(row)
        print(fam, json.dumps({k: v for k, v in row.items() if isinstance(v, dict)}), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=list("abcd"))
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--smoke", action="store_true", help="small test: part b two variants; output tagged _smoke")
    a = ap.parse_args()
    global SMOKE
    SMOKE = a.smoke
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    t0 = time.time()
    res = {"a": part_a, "b": part_b, "c": part_c, "d": part_d}[a.part](a.B)
    tag = "_smoke" if a.smoke else ""
    out = (C.OUT / "test" if a.smoke else C.RES) / f"amend1_{a.part}{tag}.json"
    json.dump(dict(part=a.part, amendment="prereg.md amendment 1 (11 Nov 18:45)", B=a.B,
                   seconds=round(time.time() - t0, 1), result=res), open(out, "w"), indent=1)
    if isinstance(res, list) and res:
        cols = sorted({k for r in res for k in r}, key=lambda k: list(res[0]).index(k) if k in res[0] else 99)
        with open(out.with_suffix(".csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in res:
                w.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in r.items()})
    print("wrote", out, f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()

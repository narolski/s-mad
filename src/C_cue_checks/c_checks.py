"""C1, C3, C4 zero-compute cue checks on every benchmark cell (FRLL-Morphs x5, corrected MAD22 x5, MorDIFF, DiM x6).
Reads file headers and decoded pixels only; no re-encoding, no resampling of stored data (the aligned crops are existing
files; the expression probe downsamples an in-memory copy of an existing crop for a CPU logistic regression, nothing
is written). Run: python3 -I src/C_cue_checks/c_checks.py [--smoke]
"""
import csv, json, os, pathlib, re, sys, hashlib
from multiprocessing import Pool
import numpy as np

DL = pathlib.Path("/mnt/t7/Datasety/downloads")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
MADA = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native")
EV = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C_cue_checks")
SMOKE = "--smoke" in sys.argv
IMG = (".jpg", ".jpeg", ".png")
DIM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
FRLLM = ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")
MAD22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")


def forbidden(p):
    s = str(p).lower()
    return any(t in s for t in ("fst", "a12sp", "a12-sp")) or ("valx" in s and "valx_a.csv" not in s)


def lst(d):
    return [p for p in sorted(pathlib.Path(d).glob("*")) if p.is_file() and p.suffix.lower() in IMG and not forbidden(p)]


def persons(name):
    n = pathlib.Path(name).stem
    for rx in (r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})", r"^(\d{3})_(\d{2})-vs-(\d{3})_(\d{2})"):
        m = re.match(rx, n)
        if m:
            return (m.group(1), m.group(3)), (m.group(2), m.group(4))
    m = re.match(r"^(\d{3})_(\d{3})(?:_|$)", n)
    if m:
        return (m.group(1), m.group(2)), (None, None)
    m = re.match(r"^(\d{3})_(\d{2})(?:_|$)", n)
    if m:
        return (m.group(1),), (m.group(2),)
    raise ValueError(name)


def cells():
    frll_raw = lst(DL / "frll_base/extracted/neutral_front") + lst(DL / "frll_base/extracted/smiling_front")
    ev = list(csv.DictReader(open(EV / "manifests/eval.csv")))
    al = lambda st, fam, lab: [EV / r["path"] for r in ev if (r["set"], r["family"], r["label"], r["variant"]) == (st, fam, lab, "orig")]  # noqa: E731
    C = {}
    for f in FRLLM:
        C[f"FRLL-Morphs/{f}"] = dict(m_raw=lst(DL / f"FRLL-Morphs/facelab_london/morph_{f}"), b_raw=frll_raw,
                                    m_al=al("frllm", f, "1"), b_al=al("frllm", "frll_bona", "0"))
    for f in MAD22:
        C[f"MAD22c/{f}"] = dict(m_raw=lst(MAD / f), b_raw=lst(MAD / "BonaFide"), m_al=lst(MADA / f), b_al=lst(MADA / "BonaFide"))
    C["MorDIFF"] = dict(m_raw=sorted(p for d in (DL / "MorDIFF/MorDIFF_crop").glob("*/morphed") for p in lst(d)), b_raw=frll_raw,
                        m_al=al("mordiff", "mordiff", "1"), b_al=al("mordiff", "mordiff_bona", "0"))
    for f in DIM:
        C[f"DiM/{f}"] = dict(m_raw=lst(DL / f"DiM-FRLL-Morphs/morphs/{f}"), b_raw=frll_raw, m_al=al("dim", f, "1"), b_al=al("dim", "dim_bona", "0"))
    if SMOKE:
        C = {k: {kk: vv[:4] + vv[-4:] for kk, vv in v.items()} for k, v in list(C.items())[:3] + list(C.items())[5:6] + list(C.items())[10:12]}
    return C


def header(p):
    from PIL import Image, JpegImagePlugin
    with open(p, "rb") as f:
        mg = f.read(8)
    cont = "JPEG" if mg[:3] == b"\xff\xd8\xff" else "PNG" if mg[:8] == b"\x89PNG\r\n\x1a\n" else "other"
    with Image.open(p) as im:
        sub = prog = None
        if cont == "JPEG":
            try:
                sub = int(JpegImagePlugin.get_sampling(im))
            except Exception:
                sub = None
            prog = bool(im.info.get("progressive") or im.info.get("progression"))
        return {"container": cont, "sub": sub, "prog": prog, "mode": im.mode, "icc": bool(im.info.get("icc_profile")),
                "bits": im.info.get("bits") or (16 if im.mode.startswith("I;16") else 8)}


def stats_job(args):
    p, kind = args
    from PIL import Image
    try:
        with Image.open(p) as im:
            a = np.asarray(im.convert("RGB"), dtype=np.float64)
        o = {"path": str(p)}
        flat = a.reshape(-1, 3)
        o["mean"] = flat.mean(0).tolist()
        o["std"] = flat.std(0).tolist()
        if kind == "al":
            nz = flat[flat.sum(1) > 0]
            o["mean_nz"] = nz.mean(0).tolist() if len(nz) else [np.nan] * 3
            o["std_nz"] = nz.std(0).tolist() if len(nz) else [np.nan] * 3
            o["zero_frac"] = float(1 - len(nz) / len(flat))
            # expression probe input: lower-face box of the eye-aligned 512 frame, grey, block-averaged 6x6 (in memory)
            g = a[300:432, 150:366].mean(2)
            o["mouth"] = g.reshape(22, 6, 36, 6).mean((1, 3)).ravel().tolist()
        else:
            o["hdr"] = header(p)
        return o
    except Exception as e:  # noqa: BLE001
        return {"path": str(p), "error": repr(e)}


def auc(pos, neg):
    from scipy.stats import rankdata
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
    if not len(pos) or not len(neg):
        return None
    r = rankdata(np.r_[pos, neg])
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def fold_of(p, k=5):
    return int(hashlib.sha1(f"c3-{p}".encode()).hexdigest(), 16) % k


def cv_lr(X, y, P, k=5):
    """5-fold by person: test = items with any person in fold f; train = items with no person in fold f."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    aucs = []
    for f in range(k):
        te = np.array([any(fold_of(q) == f for q in pp) for pp in P])
        tr = np.array([all(fold_of(q) != f for q in pp) for pp in P])
        if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X[tr], y[tr])
        s = m.decision_function(X[te])
        aucs.append(auc(s[y[te] == 1], s[y[te] == 0]))
    return {"auc_mean": float(np.mean(aucs)), "auc_folds": [round(a, 3) for a in aucs]}


def cat_o(xm, xb):
    """categorical one-feature separability: in-sample morph rate per category as the score, O = max(AUC, 1-AUC)."""
    keys = sorted(set(map(str, xm)) | set(map(str, xb)))
    rate = {c: (sum(str(x) == c for x in xm) / max(len(xm), 1)) / ((sum(str(x) == c for x in xm) / max(len(xm), 1)) + (sum(str(x) == c for x in xb) / max(len(xb), 1)))
            for c in keys}
    a = auc([rate[str(x)] for x in xm], [rate[str(x)] for x in xb])
    return max(a, 1 - a), {c: [sum(str(x) == c for x in xm), sum(str(x) == c for x in xb)] for c in keys}


def main():
    C = cells()
    jobs = sorted({(str(p), "raw") for c in C.values() for p in c["m_raw"] + c["b_raw"]} |
                  {(str(p), "al") for c in C.values() for p in c["m_al"] + c["b_al"]})
    print(len(jobs), "images", flush=True)
    with Pool(14) as pool:
        R = {(o["path"], j[1]): o for j, o in zip(jobs, pool.map(stats_job, jobs, chunksize=16))}
    errs = [k for k, v in R.items() if "error" in v]
    print("errors", len(errs), errs[:5], flush=True)
    # ---------- expression probe (C1, FRLL-Morphs and DiM have no expression in their file names)
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    gb = C[next(k for k in C if k.startswith("FRLL-Morphs"))]["b_al"]
    Xg = np.array([R[(str(p), "al")]["mouth"] for p in gb])
    yg = np.array([1 if persons(p.name)[1][0] == "08" else 0 for p in gb])
    pg = [persons(p.name)[0][0] for p in gb]
    accs = []
    for f in range(5):
        te = np.array([fold_of(q) == f for q in pg])
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Xg[~te], yg[~te])
        accs.append(float((m.predict(Xg[te]) == yg[te]).mean()))
    probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Xg, yg)
    res = {"expression_probe": {"cv_accuracy_by_person": [round(a, 3) for a in accs], "mean": float(np.mean(accs)),
                                "note": "trained on FRLL genuine aligned crops (neutral 03 vs smiling 08), lower-face box, 5-fold by person"},
           "cells": {}}
    for cn, c in C.items():
        o = {"n_morph_raw": len(c["m_raw"]), "n_bona_raw": len(c["b_raw"]), "n_morph_al": len(c["m_al"]), "n_bona_al": len(c["b_al"])}
        # C1
        def exprs(paths):
            out = []
            for p in paths:
                _pp, ee = persons(pathlib.Path(p).name)
                out.append(ee)
            return out
        eb = exprs(c["b_raw"]) if not cn.startswith("MAD22c") else exprs(c["b_raw"])
        if cn.startswith("FRLL-Morphs") or cn.startswith("DiM") or "neutral_front" in str(c["b_raw"][0]):
            eb = ["03" if "neutral_front" in str(p) else "08" if "smiling_front" in str(p) else persons(p.name)[1][0] for p in c["b_raw"]]
        else:
            eb = [e[0] for e in eb]
        em = exprs(c["m_raw"])
        named = [e for e in em if e[0] is not None]
        o["C1"] = {"bona_expr_counts": {k: eb.count(k) for k in sorted(set(eb))},
                   "morph_expr_from_names": ({"/".join(e): ["/".join(x) for x in named].count("/".join(e)) for e in sorted(set(map(tuple, named)))}
                                             if named else "not in file names")}
        if not named:
            sm = probe.predict_proba(np.array([R[(str(p), "al")]["mouth"] for p in c["m_al"]]))[:, 1]
            o["C1"]["morph_probe_p_smiling"] = {"mean": float(sm.mean()), "frac_gt_0.5": float((sm > 0.5).mean())}
        m_neu = ([1.0 if e == ("03", "03") else 0.0 if e == ("08", "08") else 0.5 for e in named] if named else None)
        if named:
            frac_m_smile = 1 - float(np.mean(m_neu))
            frac_b_smile = eb.count("08") / len(eb)
            # O of the expression label alone (smiling = 1, mixed = 0.5)
            o["C1"]["O_expression_label"] = max(auc([1 - x for x in m_neu], [1.0 if e == "08" else 0.0 for e in eb]),
                                                1 - auc([1 - x for x in m_neu], [1.0 if e == "08" else 0.0 for e in eb]))
            o["C1"]["smiling_share_morph_vs_bona"] = [frac_m_smile, frac_b_smile]
        # C3 colour statistics
        for kind in ("raw", "al"):
            pm, pb = c[f"m_{kind}"], c[f"b_{kind}"]
            feats = [("mean", 0), ("mean", 1), ("mean", 2), ("std", 0), ("std", 1), ("std", 2)]
            if kind == "al":
                feats += [("mean_nz", 0), ("mean_nz", 1), ("mean_nz", 2), ("std_nz", 0), ("std_nz", 1), ("std_nz", 2)]
            F = lambda ps: np.array([[R[(str(p), kind)][a][i] for a, i in feats] for p in ps if "error" not in R[(str(p), kind)]])  # noqa: E731
            Fm, Fb = F(pm), F(pb)
            one = {f"{a}_{'RGB'[i]}": auc(Fm[:, j], Fb[:, j]) for j, (a, i) in enumerate(feats)}
            X = np.r_[Fm[:, :6], Fb[:, :6]]
            y = np.r_[np.ones(len(Fm)), np.zeros(len(Fb))]
            P = [persons(pathlib.Path(p).name)[0] for p in pm if "error" not in R[(str(p), kind)]] + \
                [persons(pathlib.Path(p).name)[0] for p in pb if "error" not in R[(str(p), kind)]]
            o[f"C3_{kind}"] = {"one_feature_auc": one, "O_max": max(max(v, 1 - v) for v in one.values() if v is not None),
                               "lr6_cv_by_person": cv_lr(X, y, P)}
            if kind == "al":
                o["C3_al"]["lr6_nonzero_cv_by_person"] = cv_lr(np.r_[Fm[:, 6:], Fb[:, 6:]], y, P)
                zm = [R[(str(p), "al")]["zero_frac"] for p in pm]
                zb = [R[(str(p), "al")]["zero_frac"] for p in pb]
                o["C3_al"]["zero_border_frac_median_morph_bona"] = [float(np.median(zm)), float(np.median(zb))]
        # C4 headers of the stored files
        hm = [R[(str(p), "raw")]["hdr"] for p in c["m_raw"] if "error" not in R[(str(p), "raw")]]
        hb = [R[(str(p), "raw")]["hdr"] for p in c["b_raw"] if "error" not in R[(str(p), "raw")]]
        c4 = {}
        for k in ("container", "sub", "mode", "icc", "prog", "bits"):
            O, cnt = cat_o([h[k] for h in hm], [h[k] for h in hb])
            c4[k] = {"O": O, "counts_morph_bona": cnt}
        O, cnt = cat_o(["|".join(str(h[k]) for k in ("container", "sub", "mode", "prog")) for h in hm],
                       ["|".join(str(h[k]) for k in ("container", "sub", "mode", "prog")) for h in hb])
        c4["format_key container|sub|mode|prog"] = {"O": O, "counts_morph_bona": cnt}
        o["C4"] = c4
        res["cells"][cn] = o
        print(cn, json.dumps({"C1": o["C1"], "C3raw": [round(o["C3_raw"]["O_max"], 3), round(o["C3_raw"]["lr6_cv_by_person"]["auc_mean"], 3)],
                              "C3al": [round(o["C3_al"]["O_max"], 3), round(o["C3_al"]["lr6_cv_by_person"]["auc_mean"], 3), round(o["C3_al"]["lr6_nonzero_cv_by_person"]["auc_mean"], 3)],
                              "C4": {k: round(v["O"], 3) for k, v in c4.items()}}), flush=True)
    res["errors"] = errs
    if not SMOKE:
        json.dump(res, open(OUT / "c_checks.json", "w"), indent=1, default=str)
    else:
        print("smoke ok")


if __name__ == "__main__":
    main()

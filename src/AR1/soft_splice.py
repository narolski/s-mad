"""Reader for amendment 8 (softened copies, crossed contrasts) and amendment 7 (spliced inner-face morph). Released
detectors; person bootstrap as analyse.py (B = 2,000). Writes experiments/AR1/soft_splice.json."""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import analyse as A  # noqa: E402
import stats  # noqa: E402


def load_many(tag, sfx):
    S = {}
    for s in sfx:
        x = A.load(f"{tag}__{s}") if s else A.load(tag)
        if x:
            S.update(x)
    return S


def img_feat(args):
    import cv2
    rid, path, ta, tb = args
    img = cv2.imread(path)
    Y = stats.M.luminance(img[..., ::-1])
    import splice as SP
    m = SP.hull(ta, tb, img.shape)
    L = cv2.Laplacian(Y, cv2.CV_64F)
    return rid, dict(thumb=img.reshape(32, 16, 32, 16, 3).mean((1, 3)).ravel().astype(np.float32),
                     band=np.array(stats.M.band_shares(stats.M.power_profile(Y)[0]), np.float32),
                     lapvar=float(L.var()), ratio=float(L[m].var() / max(L[~m].var(), 1e-12)))


def base_excess(D, S, pos, neg, drep, FEAT):
    """detector AUC minus the best simple baseline on the same images (thumbnail, band: logistic, strict person folds;
    Laplacian variance, inside/outside sharpness ratio: scalars, folded), paired person bootstrap."""
    from gate_c import oof_persons
    rows = [r for r in neg + pos if r["id"] in FEAT and r["id"] in S]
    y = np.array([0] * sum(1 for r in neg if r["id"] in FEAT and r["id"] in S) + [1] * sum(1 for r in pos if r["id"] in FEAT and r["id"] in S))
    best = None
    out = {}
    for b in ("thumb", "band", "lapvar", "ratio"):
        if b in ("thumb", "band"):
            X = np.stack([FEAT[r["id"]][b] for r in rows])
            sc, _ = oof_persons(X, y, [(r["p1"], r["p2"]) for r in rows])
        else:
            sc = np.array([FEAT[r["id"]][b] for r in rows])
        bs = {r["id"]: v for r, v in zip(rows, sc) if np.isfinite(v)}
        a_, rep, _, _ = A.contrast(D, bs, pos, neg)
        if a_ < 0.5:
            a_, rep = 1 - a_, 1 - rep
        out[b] = a_
        if best is None or a_ > best[0]:
            best = (a_, rep, b)
    da = None
    return dict(baselines=out, best=best[2], best_auc=best[0], excess_ci95=stats.ci(drep - best[1]),
                excess=float(np.nanmedian(drep - best[1])))


FEAT = {}


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    soft = list(csv.DictReader(open(K.OUT / "manifest_soft.csv")))
    P = A.Pool(man, "frgcferet")
    D = P.D
    sp = list(csv.DictReader(open(K.OUT / "manifest_splice2.csv")))
    pool = {r["pid"]: r for r in csv.DictReader(open(K.OUT / "pool.csv"))}
    need = [r for r in sp if r["variant"] == "native"] + [r for r in man if r["pool"] == "frgcferet" and r["rung"] in ("R2w4", "R2w", "R4", "R3")]
    from multiprocessing import Pool as MP
    with MP(2) as mp:
        FEAT.update(mp.map(img_feat, [(r["id"], r["path"], pool[r["p1"]]["H"][:-4] + ".tem", pool[r["p1"]]["B"][:-4] + ".tem")
                                      for r in need], chunksize=16))
    out = {"soft": {}, "splice": {}}
    for name, tag in A.REL:
        S = load_many(tag, ["", "soft", "splice2", "splice2_bl"])
        so = out["soft"].setdefault(name, {})
        for st in ("fm61", "amsl112"):
            hosts = {r["p1"] for r in soft if r["rung"] == "R2wsoft" and r["strength"] == st}
            nat = lambda tool, g: [r for r in P.rows(tool, g) if r["p1"] in hosts]  # noqa
            sf = lambda tool, g: [r for r in soft if r["strength"] == st and r["rung"] == g + "soft" and  # noqa
                                  (g == "R0" or r["tool"] == tool) and r["p1"] in hosts]
            res = {}
            for lab, pos, neg in (("R2wsoft_vs_R4native (OC)", nat("opencv", "R4"), sf("opencv", "R2w")),
                                  ("R2wnative_vs_R4soft (OC)", sf("opencv", "R4"), nat("opencv", "R2w")),
                                  ("R2wsoft_vs_R4soft (OC)", sf("opencv", "R4"), sf("opencv", "R2w")),
                                  ("R2wnative_vs_R4native (OC, same hosts)", nat("opencv", "R4"), nat("opencv", "R2w")),
                                  ("R0native_vs_R0soft", sf("opencv", "R0"), nat("opencv", "R0")),
                                  ("R0soft_vs_R2wsoft (OC)", sf("opencv", "R2w"), sf("opencv", "R0")),
                                  ("R2wsoft_vs_R4native (FM)", nat("facemorpher", "R4"), sf("facemorpher", "R2w")),
                                  ("R2wnative_vs_R4native (FM, same hosts)", nat("facemorpher", "R4"), nat("facemorpher", "R2w"))):
                a, rep, n1, n0 = A.contrast(D, S, pos, neg)
                res[lab] = dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
            so[st] = res
        for st_lab in ("OC", "FM"):
            vals = [so[st][f"R2wsoft_vs_R4native ({st_lab})"] for st in ("fm61", "amsl112")]
            if any(v["auc"] < 0.75 and v["ci95"][1] < 0.85 for v in vals):
                vd = "detail loss explains the warp-vs-morph separation"
            elif all(v["auc"] >= 0.85 and v["ci95"][0] > 0.75 for v in vals):
                vd = "more than detail loss"
            else:
                vd = "mixed"
            so[f"verdict_{st_lab}"] = vd
        # splice, amendment 7b (one R4 hull per host; the earlier per-arm-hull splice files are superseded, unread)
        sl = out["splice"].setdefault(name, {})
        spr = lambda tool, rung, var: [r for r in sp if r["tool"] == tool and r["rung"] == rung and r["variant"] == var]  # noqa
        for tool in ("opencv", "facemorpher"):
            res = {}
            pairs = [("S0_vs_S4", "S4", "S0"), ("S3_vs_S4", "S4", "S3"), ("R2w4_vs_S4", "S4", "R2w4"),
                     ("R2w4_vs_S0", "S0", "R2w4"), ("R2w_vs_S3", "S3", "R2w"), ("S4_vs_R4", "R4", "S4")]
            nat = lambda g: spr(tool, g, "native") if g.startswith("S") else P.rows(tool, g)  # noqa
            for lab, pos, neg in pairs + [("R2w4_vs_R4 (unspliced)", "R4", "R2w4"), ("R3_vs_R4 (unspliced)", "R4", "R3")]:
                a_, rep, n1, n0 = A.contrast(D, S, nat(pos), nat(neg))
                res[lab] = dict(auc=a_, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
                if lab in [x[0] for x in pairs]:
                    res[lab]["vs_baselines"] = base_excess(D, S, nat(pos), nat(neg), rep, FEAT)
            for v in ("bg", "face"):
                for lab, pos, neg in (("R2w4_vs_S4", "S4", "R2w4"), ("S0_vs_S4", "S4", "S0"), ("S3_vs_S4", "S4", "S3")):
                    a_, rep, n1, n0 = A.contrast(D, S, spr(tool, pos, v + "_R4hull"), spr(tool, neg, v + "_R4hull"))
                    res[f"{v}-blanked (R4 hull): {lab}"] = dict(auc=a_, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
            res["drop_R2w4vsS4_vs_unspliced"] = res["R2w4_vs_R4 (unspliced)"]["auc"] - res["R2w4_vs_S4"]["auc"]
            sl[tool] = res
        print("done", name, flush=True)
    json.dump(out, open(K.RES / "soft_splice.json", "w"), indent=1)


if __name__ == "__main__":
    main()

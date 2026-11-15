"""Post hoc addendum P1-P4 (registered in prereg.md before running; zero GPU). Released detectors, primary pool.
P1 per-database contrasts with person bootstrap (incl. blanked); P2 pair dissimilarity (H-new-2); P3 detail-loss
matched strata (H-new-1); P4 Bonferroni-at-8 baseline excess on R3 -> R4, R0 vs R2wm (H-new-5), padding (H-new-4).
Writes experiments/AR1/posthoc.json and posthoc.md.
"""
import csv
import json
import pathlib
import sys
from multiprocessing import Pool as MPool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import analyse as A  # noqa: E402
import stats  # noqa: E402

REL = A.REL
CONTR = [("R0", "R2w"), ("R2w", "R3"), ("R3", "R4"), ("R2w", "R4"), ("R2w4", "R4"), ("R2w", "R2w4"), ("R0", "R4"),
         ("R0", "R2wm"), ("R2wm", "R3m"), ("R3m", "R4"), ("R0", "R2")]
BL_CONTR = [("R2w", "R4"), ("R0", "R4"), ("R3", "R4"), ("R0", "R2w")]
B8 = (100 * 0.05 / 8 / 2, 100 * (1 - 0.05 / 8 / 2))


def rows_of(man, tool, rung, db=None):
    out = [r for r in man if r["pool"] == "frgcferet" and r["rung"] == rung and (rung == "R0" or r["tool"] == tool)]
    return [r for r in out if db is None or r["p1"].startswith(db + ":")]


def draw(man, db):
    pers = sorted({r["p1"] for r in man if r["pool"] == "frgcferet" and r["p1"].startswith(db + ":")} |
                  {r["p2"] for r in man if r["pool"] == "frgcferet" and r["p2"].startswith(db + ":")})
    return stats.Draw(pers, A.B, [20261111, 5, len(pers)])


def cr(D, S, pos, neg):
    a, rep, n1, n0 = A.contrast(D, S, pos, neg)
    return dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0), rep


def img_feats(p):
    import cv2
    img = cv2.imread(p)
    Y = stats.M.luminance(img[..., ::-1])
    band = stats.M.band_shares(stats.M.power_profile(Y)[0])
    z = (img == 0).all(2)
    th = img.reshape(32, 16, 32, 16, 3).mean((1, 3)).ravel()
    return p, dict(lap=float(cv2.Laplacian(Y, cv2.CV_64F).var()), b23=float(band[1] + band[2]), zero=np.packbits(z), thumb=th)


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    pool = {r["pid"]: r for r in csv.DictReader(open(K.OUT / "pool.csv"))}
    out = {"P1": {}, "P2": {}, "P3": {}, "P4": {}}
    Dd = {db: draw(man, db) for db in ("frgc", "feret")}
    # image features for P2-P4
    paths = sorted({r["path"] for r in man if r["pool"] == "frgcferet" and r["rung"] in ("R2w", "R4")} |
                   {v["H"] for v in pool.values()} | {v["B"] for v in pool.values()})
    with MPool(2) as mp:
        FE = dict(mp.map(img_feats, paths, chunksize=16))
    for name, tag in REL:
        S = A.load(tag)
        Sb = {v: A.load(f"{tag}__{v}") for v in ("bg", "face")}
        o1 = out["P1"].setdefault(name, {})
        for tool in ("opencv", "facemorpher"):
            for db in ("frgc", "feret"):
                c = o1.setdefault(f"{tool}/{db}", {})
                for neg, pos in CONTR:
                    c[f"{neg}vs{pos}"], _ = cr(Dd[db], S, rows_of(man, tool, pos, db), rows_of(man, tool, neg, db))
                for v in ("bg", "face"):
                    for neg, pos in BL_CONTR:
                        c[f"{v}:{neg}vs{pos}"], _ = cr(Dd[db], Sb[v], rows_of(man, tool, pos, db), rows_of(man, tool, neg, db))
            # P2 dissimilarity
            r4 = [r for r in rows_of(man, tool, "R4") if r["id"] in S]
            from scipy.stats import spearmanr
            cos = np.array([float(pool[r["p1"]]["cos_HB"]) for r in r4])
            thd = np.array([float(np.abs(FE[pool[r["p1"]]["H"]]["thumb"] - FE[pool[r["p1"]]["B"]]["thumb"]).mean()) for r in r4])
            sc = np.array([S[r["id"]] for r in r4])
            o2 = out["P2"].setdefault(name, {}).setdefault(tool, {})
            o2["spearman_R4logit_cosHB"] = float(spearmanr(sc, cos)[0])
            o2["spearman_R4logit_thumbdist"] = float(spearmanr(sc, thd)[0])
            P = A.Pool(man, "frgcferet")
            full, _ = cr(P.D, S, rows_of(man, tool, "R4"), rows_of(man, tool, "R3"))
            top = set()
            for db in ("frgc", "feret"):
                hs = [p for p in pool if p.startswith(db + ":")]
                cs = np.array([float(pool[p]["cos_HB"]) for p in hs])
                thr = np.quantile(cs, 0.9)
                top |= {p for p, c_ in zip(hs, cs) if c_ >= thr}
            dec, _ = cr(P.D, S, [r for r in rows_of(man, tool, "R4") if r["p1"] in top],
                        [r for r in rows_of(man, tool, "R3") if r["p1"] in top])
            o2["R3vsR4_full"] = full
            o2["R3vsR4_most_similar_decile"] = dec
            o2["decile_hosts"] = len(top)
            o2["falsified_H_new_2(within 0.03)"] = bool(abs(dec["auc"] - full["auc"]) <= 0.03)
            # P3 detail-loss strata
            rr = [r for r in rows_of(man, tool, "R2w") + rows_of(man, tool, "R4") if r["id"] in S]
            lap = np.array([FE[r["path"]]["lap"] for r in rr])
            b23 = np.array([FE[r["path"]]["b23"] for r in rr])
            y = np.array([r["rung"] == "R4" for r in rr])
            ql = np.digitize(lap, np.quantile(lap, [0.2, 0.4, 0.6, 0.8]))
            qb = np.digitize(b23, np.quantile(b23, [0.2, 0.4, 0.6, 0.8]))
            num = den = 0.0
            used = 0
            for i in range(5):
                for j in range(5):
                    k = (ql == i) & (qb == j)
                    if (k & y).sum() >= 10 and (k & ~y).sum() >= 10:
                        a_ = stats.auc([S[r["id"]] for r, m in zip(rr, k & y) if m], [S[r["id"]] for r, m in zip(rr, k & ~y) if m])
                        w = min((k & y).sum(), (k & ~y).sum())
                        num += w * a_
                        den += w
                        used += int((k).sum())
            out["P3"].setdefault(name, {})[tool] = dict(matched_auc=num / den if den else None, images_in_used_cells=used,
                                                        of=len(rr), unmatched_auc=stats.auc(sc, [S[r["id"]] for r in rr if r["rung"] == "R2w"]))
            # P4 Bonferroni-at-8 excess on R3 -> R4, R0 vs R2wm
            oofz = dict(np.load(A.SC / "baselines_oof.npz"))
            best, best_rep, key = A._best(P, S, tool, "R4", "R3", oofz, ("thumb32", "background", "band", "lapvar", "bytes", "border"))
            da, drep, _, _ = A.contrast(P.D, S, P.rows(tool, "R4"), P.rows(tool, "R3"))
            o4 = out["P4"].setdefault(name, {}).setdefault(tool, {})
            o4["R3toR4_excess_best_simple"] = dict(best=key, best_auc=best, detector_auc=da, excess=da - best,
                                                    ci95=stats.ci(drep - best_rep), ci_bonferroni8=stats.ci(drep - best_rep, *B8))
            o4["R0vsR2wm"], _ = cr(P.D, S, P.rows(tool, "R2wm"), P.rows(tool, "R0"))
            # H-new-4 padding (colorFERET)
            fr = [r for r in rows_of(man, tool, "R4", "feret") if r["id"] in S]
            pad = np.array([float(np.unpackbits(FE[pool[r["p1"]]["H"]]["zero"] ^ FE[pool[r["p1"]]["B"]]["zero"]).mean()) for r in fr])
            o4["feret_pad_diff_area_median"] = float(np.median(pad))
            o4["feret_spearman_R4_vs_paddiff"] = float(spearmanr([S[r["id"]] for r in fr], pad)[0])
            frf = [r for r in fr if r["id"] in Sb["face"]]
            padf = np.array([float(np.unpackbits(FE[pool[r["p1"]]["H"]]["zero"] ^ FE[pool[r["p1"]]["B"]]["zero"]).mean()) for r in frf])
            o4["feret_spearman_faceblankedR4_vs_paddiff"] = float(spearmanr([Sb["face"][r["id"]] for r in frf], padf)[0])
        print("done", name, flush=True)
    json.dump(out, open(K.RES / "posthoc.json", "w"), indent=1)


if __name__ == "__main__":
    main()

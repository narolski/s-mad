"""Amendment 10 (registered in git commit 81864bd before this ran). Measurement only, no image written.
(a) simple-statistic floor for S4 vs swap-splice SW (OpenCV-style); (b) noise-residual floor (first-order luma
differences inside / outside the hull) for R2w vs R4 and R2w4 vs R4, both tools. Released detectors' excess, paired
person bootstrap. -> experiments/AR1/floors10.json"""
import csv
import json
import pathlib
import sys
from multiprocessing import Pool as MP

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import analyse as A  # noqa: E402
import stats  # noqa: E402
import splice as SP  # noqa: E402
import swap as SWM  # noqa: E402

POOL = {r["pid"]: r for r in csv.DictReader(open(K.OUT / "pool.csv"))}


def kurt(x):
    x = x - x.mean()
    v = (x ** 2).mean()
    return float((x ** 4).mean() / max(v * v, 1e-12))


def feats(a):
    import cv2
    rid, path, pid = a
    r = POOL[pid]
    img = cv2.imread(path)
    m = SP.hull(r["H"][:-4] + ".tem", r["B"][:-4] + ".tem", img.shape)
    Y = stats.M.luminance(img[..., ::-1])
    L = cv2.Laplacian(Y, cv2.CV_64F)
    simple = dict(ratio=float(L[m].var() / max(L[~m].var(), 1e-12)), lap_in=float(L[m].var()))
    t = SWM.seam(img, m)
    simple.update(tone_luma=t[0], tone_rg=t[1], abs_step=t[2])
    for i, b in enumerate(stats.M.band_shares(stats.M.power_profile(Y)[0])):
        simple[f"band{i + 1}"] = float(b)
    dx = np.diff(Y, axis=1)
    dy = np.diff(Y, axis=0)
    mx, my = m[:, 1:] & m[:, :-1], m[1:, :] & m[:-1, :]
    nr = []
    for d, mm in ((dx, mx), (dy, my)):
        for reg in (mm, ~mm):
            v = d[reg]
            nr += [float(v.std()), float(np.abs(v).mean()), kurt(v)]
    return rid, simple, np.array(nr, np.float32)


def floor_eval(D, rows_pos, rows_neg, F, learned_keys, single_keys):
    from gate_c import oof_persons
    rows = rows_neg + rows_pos
    y = np.array([0] * len(rows_neg) + [1] * len(rows_pos))
    res = {}
    best = None
    for k in single_keys:
        sc = {r["id"]: F[r["id"]][0][k] for r in rows}
        a, rep, _, _ = A.contrast(D, sc, rows_pos, rows_neg)
        if a < 0.5:
            a, rep = 1 - a, 1 - rep
        res[k] = dict(auc=a, ci95=stats.ci(rep))
        if best is None or a > best[0]:
            best = (a, rep, k)
    for name, getx in learned_keys:
        X = np.stack([getx(F[r["id"]]) for r in rows])
        s, nun = oof_persons(X, y, [(r["p1"], r["p2"]) for r in rows])
        sc = {r["id"]: v for r, v in zip(rows, s) if np.isfinite(v)}
        a, rep, _, _ = A.contrast(D, sc, rows_pos, rows_neg)
        res[name] = dict(auc=a, ci95=stats.ci(rep), n_untested=nun)
        if best is None or a > best[0]:
            best = (a, rep, name)
    return res, best


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    sp = [r for r in csv.DictReader(open(K.OUT / "manifest_splice2.csv")) if r["variant"] == "native"]
    sw = list(csv.DictReader(open(K.OUT / "manifest_swap.csv")))
    P = A.Pool(man, "frgcferet")
    D = P.D
    s4 = [r for r in sp if r["rung"] == "S4" and r["tool"] == "opencv"]
    need = s4 + sw + [r for r in man if r["pool"] == "frgcferet" and r["rung"] in ("R2w", "R2w4", "R4")]
    with MP(2) as mp:
        F = {rid: (s, n) for rid, s, n in mp.map(feats, [(r["id"], r["path"], r["p1"]) for r in need], chunksize=16)}
    out = {"a_S4_vs_SW": {}, "b_noise_residual": {}}
    keys = ["ratio", "lap_in", "tone_luma", "tone_rg", "abs_step"] + [f"band{i}" for i in range(1, 6)]
    allx = lambda f: np.array([f[0][k] for k in keys], np.float32)  # noqa
    fa, best_a = floor_eval(D, s4, sw, F, [("combined_logistic", allx)], keys)
    out["a_S4_vs_SW"]["floors"] = fa
    out["a_S4_vs_SW"]["best_floor"] = dict(name=best_a[2], auc=best_a[0], ci95=stats.ci(best_a[1]))
    out["b_noise_residual"]["floors"] = {}
    bests = {}
    for tool in ("opencv", "facemorpher"):
        for base in ("R2w", "R2w4"):
            fb, bb = floor_eval(D, P.rows(tool, "R4"), P.rows(tool, base), F, [("noise_residual_logistic", lambda f: f[1])], [])
            out["b_noise_residual"]["floors"][f"{tool}/{base}vsR4"] = fb
            bests[(tool, base)] = bb
    for name, tag in A.REL:
        S = A.load(tag)
        S.update(A.load(f"{tag}__splice2") or {})
        S.update(A.load(f"{tag}__swap") or {})
        da, drep, _, _ = A.contrast(D, S, s4, sw)
        out["a_S4_vs_SW"][name] = dict(auc=da, ci95=stats.ci(drep), excess=da - best_a[0], excess_ci95=stats.ci(drep - best_a[1]))
        o = out["b_noise_residual"].setdefault(name, {})
        for (tool, base), bb in bests.items():
            da, drep, _, _ = A.contrast(D, S, P.rows(tool, "R4"), P.rows(tool, base))
            o[f"{tool}/{base}vsR4"] = dict(auc=da, ci95=stats.ci(drep), floor=bb[0], excess=da - bb[0],
                                         excess_ci95=stats.ci(drep - bb[1]))
    json.dump(out, open(K.RES / "floors10.json", "w"), indent=1)
    print(json.dumps(out["a_S4_vs_SW"], indent=0)[:3000])
    for name, _ in A.REL:
        print(name, {k: (round(v["auc"], 3), round(v["floor"], 3), round(v["excess"], 3), [round(x, 3) for x in v["excess_ci95"]])
                     for k, v in out["b_noise_residual"][name].items()})


if __name__ == "__main__":
    main()

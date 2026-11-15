"""Amendment 11 (registered in git a265476 before this ran). Measurement only.
(a) paired excess of each release over inside-hull Laplacian variance on S4 vs SW; combined 22-number floor
    (10 simple statistics + 12 noise residuals, logistic, strict person folds) on primary warp-only vs morph.
(b) H-D on FRLL R2w vs R4 (confounded rungs, descriptive), combined 22-number floor. -> experiments/AR1/floors11.json"""
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
import floors10 as FL  # noqa: E402

FL.POOL.update({r["pid"]: r for r in csv.DictReader(open(K.OUT / "pool_frll.csv"))})
KEYS = ["ratio", "lap_in", "tone_luma", "tone_rg", "abs_step"] + [f"band{i}" for i in range(1, 6)]
both = lambda f: np.r_[np.array([f[0][k] for k in KEYS], np.float32), f[1]]  # noqa


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    sp = [r for r in csv.DictReader(open(K.OUT / "manifest_splice2.csv")) if r["variant"] == "native"]
    sw = list(csv.DictReader(open(K.OUT / "manifest_swap.csv")))
    P = A.Pool(man, "frgcferet")
    PF = A.Pool(man, "frll")
    s4 = [r for r in sp if r["rung"] == "S4" and r["tool"] == "opencv"]
    need = s4 + sw + [r for r in man if r["pool"] in ("frgcferet", "frll") and r["rung"] in ("R2w", "R2w4", "R4")]
    with MP(2) as mp:
        F = {rid: (s, n) for rid, s, n in mp.map(FL.feats, [(r["id"], r["path"], r["p1"]) for r in need], chunksize=16)}
    out = {"a_lapin": {}, "a_combined_primary": {}, "b_HD_frll": {}}
    _, best_l = FL.floor_eval(P.D, s4, sw, F, [], ["lap_in"])
    floors = {}
    for pool, PP in (("frgcferet", P), ("frll", PF)):
        for tool in ("opencv", "facemorpher"):
            for base in ("R2w", "R2w4") if pool == "frgcferet" else ("R2w",):
                fr, bb = FL.floor_eval(PP.D, PP.rows(tool, "R4"), PP.rows(tool, base), F, [("combined22", both)], [])
                floors[(pool, tool, base)] = bb
    for name, tag in A.REL:
        S = A.load(tag)
        S.update(A.load(f"{tag}__splice2") or {})
        S.update(A.load(f"{tag}__swap") or {})
        da, drep, _, _ = A.contrast(P.D, S, s4, sw)
        out["a_lapin"][name] = dict(auc=da, lap_in=best_l[0], excess=da - best_l[0], excess_ci95=stats.ci(drep - best_l[1]))
        for (pool, tool, base), bb in floors.items():
            PP = P if pool == "frgcferet" else PF
            da, drep, _, _ = A.contrast(PP.D, S, PP.rows(tool, "R4"), PP.rows(tool, base))
            key = "a_combined_primary" if pool == "frgcferet" else "b_HD_frll"
            out[key].setdefault(name, {})[f"{tool}/{base}vsR4"] = dict(auc=da, ci95=stats.ci(drep), floor=bb[0],
                                                                       excess=da - bb[0], excess_ci95=stats.ci(drep - bb[1]))
    hd = out["b_HD_frll"]
    L = hd["MADation ViT-L/14"]
    lb = min(L[k]["excess_ci95"][0] for k in L)
    out["HD_verdict"] = dict(
        vitl14_excess_ge_003_and_lb_gt_0={k: bool(v["excess"] >= 0.03 and v["excess_ci95"][0] > 0) for k, v in L.items()},
        selfmad_opencv_interval_includes_0=bool(hd["SelfMAD"]["opencv/R2wvsR4"]["excess_ci95"][0] <= 0 <= hd["SelfMAD"]["opencv/R2wvsR4"]["excess_ci95"][1]),
        falsified=bool(lb <= 0))
    json.dump(out, open(K.RES / "floors11.json", "w"), indent=1)
    for k in ("a_lapin",):
        for n, v in out[k].items():
            print(k, n, round(v["auc"], 3), round(v["lap_in"], 3), round(v["excess"], 3), [round(x, 3) for x in v["excess_ci95"]])
    for k in ("a_combined_primary", "b_HD_frll"):
        for n, v in out[k].items():
            print(k, n, {c: (round(x["floor"], 3), round(x["auc"], 3), round(x["excess"], 3), [round(y, 3) for y in x["excess_ci95"]]) for c, x in v.items()})
    print(out["HD_verdict"])


if __name__ == "__main__":
    main()

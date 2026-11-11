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


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    soft = list(csv.DictReader(open(K.OUT / "manifest_soft.csv")))
    sp = list(csv.DictReader(open(K.OUT / "manifest_splice.csv")))
    P = A.Pool(man, "frgcferet")
    D = P.D
    out = {"soft": {}, "splice": {}}
    for name, tag in A.REL:
        S = load_many(tag, ["", "soft", "splice", "splice_bl"])
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
        # splice
        sl = out["splice"].setdefault(name, {})
        spr = lambda tool, rung, var: [r for r in sp if r["tool"] == tool and r["rung"] == rung and r["variant"] == var]  # noqa
        for tool in ("opencv", "facemorpher"):
            res = {}
            pairs = [("R2w4_vs_S4", spr(tool, "S4", "native"), P.rows(tool, "R2w4")),
                     ("R2w_vs_S3", spr(tool, "S3", "native"), P.rows(tool, "R2w")),
                     ("S3_vs_S4", spr(tool, "S4", "native"), spr(tool, "S3", "native")),
                     ("S4_vs_R4", P.rows(tool, "R4"), spr(tool, "S4", "native")),
                     ("R2w4_vs_R4 (unspliced reference)", P.rows(tool, "R4"), P.rows(tool, "R2w4"))]
            for v in ("bg", "face"):
                pairs.append((f"{v}-blanked R4-hull: R2w4_vs_S4", spr(tool, "S4", f"{v}_S4hull"), spr(tool, "R2w4", f"{v}_S4hull")))
                pairs.append((f"{v}-blanked R3-hull: R2w_vs_S3", spr(tool, "S3", f"{v}_S3hull"), spr(tool, "R2w", f"{v}_S3hull")))
            for lab, pos, neg in pairs:
                a, rep, n1, n0 = A.contrast(D, S, pos, neg)
                res[lab] = dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
            a_sp, a_un = res["R2w4_vs_S4"]["auc"], res["R2w4_vs_R4 (unspliced reference)"]["auc"]
            res["drop_vs_unspliced"] = a_un - a_sp
            sl[tool] = res
        print("done", name, flush=True)
    json.dump(out, open(K.RES / "soft_splice.json", "w"), indent=1)


if __name__ == "__main__":
    main()

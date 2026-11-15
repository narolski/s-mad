"""Wave 3 control 5 read: AUC of the main contrasts before and after blanking the same out-of-coverage region in both
classes (border.py), per head; Laplacian-variance floor before / after (cues of the blanked images: cues/border.npz).
  python3 -I border_read.py --backbone clip224 --tags full,arm_a_img_photos,arm_b_img_halves,arm_c_const_halves,arm_d_meas_halves,arm_e_meas_photos
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import metrics as M  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", default="clip224")
    ap.add_argument("--tags", required=True)
    a = ap.parse_args()
    B = {r["id"]: r for r in L.rows("border")}
    M._ROWS["border"] = B
    orig = {r["id"][3:]: r for r in B.values()}
    M._ROWS["orig_of_border"] = {}
    for lst in ("af0_w1", "af0_w2", "af0_h", "ar1"):
        for i, r in M.rows(lst).items():
            if i in orig:
                M._ROWS["orig_of_border"][i] = r
    cb = L.OUT / "cues" / "border.npz"
    if cb.exists():
        z = np.load(cb)
        M._CUES["border"] = (dict(zip(z["ids"], z["cues"])), list(z["names"]))
    co = {}
    names = None
    for lst in ("valcmp", "ar1"):
        c = M.cues(lst)
        if c:
            co.update(c[0])
            names = c[1]
    M._CUES["orig_of_border"] = (co, names) if names else None
    pos_af0 = lambda r: r["set"] in ("af0", "border") and r["rung"] == "u50"  # noqa
    neg_af0 = lambda r: r["set"] in ("af0", "border") and r["rung"] in ("halfA", "halfB")  # noqa
    pos_cv = lambda r: r["cell"] == "frgcferet" and r["tool"] == "opencv" and r["rung"] == "R4"  # noqa
    neg_cv = lambda r: r["cell"] == "frgcferet" and r["tool"] == "opencv" and r["rung"] == "R2w"  # noqa
    out = {}
    for tag in a.tags.split(","):
        d = L.OUT / "heads" / a.backbone / tag
        heads = sorted({p.name[5:-11] for p in d.glob("pred_*_border.npz")})
        for h in heads:
            Sb = M.load(a.backbone, tag, h, "border")[0]
            So = {}
            for lst in ("af0_w1", "af0_w2", "af0_h", "ar1"):
                P = M.load(a.backbone, tag, h, lst)
                if P:
                    So.update({i: s for i, s in P[0].items() if i in M._ROWS["orig_of_border"]})
            r = dict(
                af0_u50_vs_halves_blanked=M.contrast(Sb, "border", pos_af0, neg_af0),
                af0_u50_vs_halves_original=M.contrast(So, "orig_of_border", lambda x: x.get("set") == "af0" and x["rung"] == "u50",
                                                      lambda x: x.get("set") == "af0" and x["rung"] in ("halfA", "halfB")),
                opencv_R2w_vs_R4_blanked=M.contrast(Sb, "border", pos_cv, neg_cv),
                opencv_R2w_vs_R4_original=M.contrast(So, "orig_of_border", pos_cv, neg_cv))
            out[f"{tag}/{h}"] = r
            f = lambda c: None if not c else (c["auc"], c.get("lapvar_floor"))  # noqa
            print(tag, h, "AF0 orig", f(r["af0_u50_vs_halves_original"]), "blanked", f(r["af0_u50_vs_halves_blanked"]),
                  "| OpenCV R2w/R4 orig", f(r["opencv_R2w_vs_R4_original"]), "blanked", f(r["opencv_R2w_vs_R4_blanked"]), flush=True)
    json.dump(out, open(L.RES / f"wave3_border_{a.backbone}.json", "w"), indent=1)


if __name__ == "__main__":
    main()

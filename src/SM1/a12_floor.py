"""SM1 A14 follow-up (post hoc, review F2 / H-new-B rho part, zero GPU): the calibration floor of every LoRA fit.

Per fit: head norm ||w|| and bias (head.cls of ad4eval/last_trainable.pt; the PN1 reference retrains have no saved
head here, so their logit range is printed instead), the camera threshold (95th percentile of AR1 FRGC/colorFERET R0
logits), threshold minus R0 median, and for each genuine-class source the source median minus the threshold and the
flag rate at the threshold. H-new-B (rho part): Spearman correlation, over all (fit, source) cells, of the flag rate
with (threshold − source median); prediction |rho| >= 0.8.

  python3 -I a12_floor.py -> RES/a12_floor.json
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import read_p3 as P  # noqa: E402

SETS = {"vitb": (K.OUT / "lora_scores_vitb", K.OUT / "athena/lora_vitb", "SM1B"),
        "vitl": (K.OUT / "lora_scores", K.OUT / "athena/lora", "SM1L"),
        "pn1ref_vitb_release": (K.OUT / "lora_scores_pn1ref", None, None)}
SOURCES = {"ar1_R0": ("ar1:frgcferet:none:R0", "0", ""), "ar1_halves_HA": ("ar1:frgcferet:opencv:HA", "0", ""),
           "ar1_R2w_opencv": ("ar1:frgcferet:opencv:R2w", "0", ""), "frll_untouched": ("frllm:bona", "0", "native"),
           "frll_jpeg50": ("frllm:bona_jpeg50", "0", "jpeg50"), "mordiff_native": ("mordiff:bona", "0", "native"),
           "mordiff_E7": ("mordiff:mordiff", "0", "e7"), "dim_native": ("dim:bona", "0", "native"),
           "mad22_native": ("mad22:bona", "0", "native"), "frll_amsl_E7": ("frllm:amsl", "0", "e7")}


def rank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return r


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    rows = P.meta()
    pos = {r["id"]: i for i, r in enumerate(rows)}
    sel = {}
    for k, (c, lab, h) in SOURCES.items():
        sel[k] = [i for i, r in enumerate(rows) if r["cell"] == c and r["label"] == lab and r["hist"] == h]
    res, cells = {}, []
    for fam, (sd, td, pre) in SETS.items():
        for f in sorted(sd.glob("*_s*.npz")):
            z = np.load(f)
            zi = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            o = dict(logit_min=round(min(zi.values()), 3), logit_max=round(max(zi.values()), 3))
            if td is not None:
                arm, seed = f.stem.split("_s")
                pt = td / f"{pre}_{arm}_s{seed}" / "ad4eval/last_trainable.pt"
                if pt.exists():
                    w = torch.load(pt, map_location="cpu", weights_only=True)
                    o["head_norm"] = round(float(w["head.cls.weight"].norm()), 3)
                    o["head_bias"] = round(float(w["head.cls.bias"]), 3)
            r0 = np.array([zi[rows[i]["id"]] for i in sel["ar1_R0"] if rows[i]["id"] in zi])
            if len(r0) < 50:
                continue
            t = float(np.quantile(r0, 0.95))
            o["thr_cam"] = round(t, 3)
            o["thr_minus_R0_median"] = round(t - float(np.median(r0)), 3)
            o["sources"] = {}
            for k, ix in sel.items():
                v = np.array([zi[rows[i]["id"]] for i in ix if rows[i]["id"] in zi])
                if len(v) < 20:
                    continue
                o["sources"][k] = dict(n=len(v), median_minus_thr=round(float(np.median(v)) - t, 3),
                                       flag_at_thr=round(float((v >= t).mean()), 3))
                if k != "ar1_R0":
                    cells.append((t - float(np.median(v)), float((v >= t).mean())))
            res[f"{fam}:{f.stem}"] = o
            print(fam, f.stem, json.dumps({k: v for k, v in o.items() if k != "sources"}),
                  {k: (v["median_minus_thr"], v["flag_at_thr"]) for k, v in o["sources"].items()}, flush=True)
    g = np.array(cells)
    rho = float(np.corrcoef(rank(g[:, 0]), rank(g[:, 1]))[0, 1])
    res["h_new_B_rho"] = dict(rho_flag_vs_thr_minus_source_median=round(rho, 4), n_cells=len(g),
                              prediction="|rho| >= 0.8")
    print(res["h_new_B_rho"])
    json.dump(res, open(K.RES / "a12_floor.json", "w"), indent=1)


if __name__ == "__main__":
    main()

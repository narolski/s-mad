"""SM1 amendment A12 item 6 (post hoc, H-new-3): the Part 3 steps re-read with the alignment border held equal.

Border fraction per aligned evaluation frame = EV1's zero_frac (1 - share of pixels with R+G+B > 0; EV1 feat.npz
al_zero for every FRLL / DiM / MorDIFF / corrected-MAD22 frame, border_e5e7.npz for the E7 genuine pools). Genuine
frames of the landmark cells carry no border (median 0.000), so a border-matched comparison exists only where the
morph frames are border-free too:
  border-free landmark cells: landmark cells whose morph frames have border < 0.005 in >= 90% of frames
      (corrected MAD22 OpenCV and Webmorph); only their border-free morphs are used;
  bordered landmark cells: the other five landmark cells (FRLL-Morphs AMSL, FaceMorpher, OpenCV, WebMorph; MAD22
      FaceMorpher); no genuine frame with a border exists there, so "matched pairs" cannot be formed; instead each
      cell's morphs are split at the cell's median border (low / high half), each half against the same genuine set.
Per arm and seed: native EER per cell and subset, mean over the cells of a group; 5-seed means with the person
bootstrap of read_p3 (same draws); steps b -> b', b' -> c', c' -> c, c -> d, d -> e (and b -> K = 50) per group.
Prediction (review): with the border held equal, b -> b' shrinks by more than half; falsified if it stays within
1 point of the registered step (-3.42).

  python3 -I a12_border.py [--dir OUT/heads] [--name a12_border] -> RES/<name>.json
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import read_p3 as P  # noqa: E402

EV1 = pathlib.Path("/mnt/t7/smad_next/EV1")
ARMS = ("a", "b", "d50", "bp", "cr", "c", "d", "e", "f")
STEPS = (("b", "bp"), ("bp", "cr"), ("cr", "c"), ("c", "d"), ("d", "e"), ("b", "d50"), ("a", "b"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--name", default="a12_border")
    ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    z1 = np.load(EV1 / "feat.npz")
    bmap = dict(zip([str(p) for p in z1["al_path"]], z1["al_zero"].astype(float)))
    z2 = np.load(EV1 / "border_e5e7.npz")
    bmap.update(dict(zip([str(p) for p in z2["path"]], z2["zero_frac"].astype(float))))
    rows = P.meta()
    hd = pathlib.Path(a.dir) if a.dir else K.OUT / "heads"
    have = {str(i) for i in np.load(hd / "b_s401.npz")["id"]}
    rows = [r for r in rows if r["id"] in have]
    R = P.Reader(rows, a.B)
    bord = np.array([bmap.get(r["path"], np.nan) for r in rows])
    cells = P.cells()
    groups, desc = {}, {}
    for c in P.LANDMARK7:
        gn, _, mo = cells[c]
        im, ig = R.sel(*mo), R.sel(*gn)
        bm, bg = bord[im], bord[ig]
        assert np.isfinite(bm).all(), c
        desc[c] = dict(n_morph=len(im), morph_border_median=round(float(np.median(bm)), 4),
                       share_morph_border_free=round(float((bm < 0.005).mean()), 3),
                       genuine_border_median=round(float(np.nanmedian(bg)), 4) if np.isfinite(bg).any() else None)
        if (bm < 0.005).mean() >= 0.9:
            groups.setdefault("border_free", []).append((c, ig, im[bm < 0.005]))
        else:
            med = np.median(bm)
            groups.setdefault("bordered_low_half", []).append((c, ig, im[bm <= med]))
            groups.setdefault("bordered_high_half", []).append((c, ig, im[bm > med]))
            groups.setdefault("bordered_all", []).append((c, ig, im))
    raw = {}
    for arm in ARMS:
        for s in K.SEEDS:
            f = hd / f"{arm}_s{s}.npz"
            if not f.exists():
                continue
            zf = np.load(f)
            zi = {str(i): v for i, v in zip(zf["id"], zf["logit"])}
            z = np.array([zi[r["id"]] for r in rows], np.float64)
            m = {}
            for g, items in groups.items():
                pts, drs = [], []
                for c, ig, im in items:
                    pt, _ = S.eer_unit(z[ig], z[im])
                    dr, _ = S.weer(z[ig], z[im], R.w(ig), R.w(im))
                    pts.append(pt)
                    drs.append(dr)
                    m[f"eer:{g}:{c}"] = (pt, dr)
                m[f"mean_eer:{g}"] = (float(np.mean(pts)), np.mean(drs, 0))
            raw.setdefault(arm, []).append(m)
    res = dict(cells=desc, groups={g: [c for c, _, _ in v] for g, v in groups.items()},
               arms={arm: P.summarise(ms) for arm, ms in raw.items()}, steps={})
    for x, y in STEPS:
        if x in raw and y in raw:
            res["steps"][f"{x}->{y}"] = {g: P.diff(raw[x], raw[y], f"mean_eer:{g}") for g in groups}
    st = res["steps"].get("b->bp", {})
    if "border_free" in st:
        bf = st["border_free"]["diff"]
        res["prediction"] = dict(text="b -> b' with the border held equal shrinks by more than half of the registered "
                                      "-3.42; falsified if within 1 point of -3.42", registered_step=-3.42,
                                 border_free_step=round(bf, 3), shrinks_by_half=bool(abs(bf) < 0.5 * 3.42),
                                 falsified=bool(abs(bf - (-3.42)) <= 1.0))
    res["note"] = ("post hoc (A12 item 6); our frames, first-test data, arms fixed in advance; matched pairs are not "
                   "possible in the bordered cells (their genuine frames have no border)")
    json.dump(res, open(K.RES / f"{a.name}.json", "w"), indent=1)
    for g in groups:
        print(g, res["groups"][g], {arm: round(v[f"mean_eer:{g}"]["mean"], 2) for arm, v in res["arms"].items()})
    print(json.dumps({k: {g: (round(v["diff"], 2), [round(x, 2) for x in v["ci"]]) for g, v in d.items()}
                      for k, d in res["steps"].items()}, indent=0))
    print(res.get("prediction"))


if __name__ == "__main__":
    main()

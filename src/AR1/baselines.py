"""AR3 baselines (no detector involved). Features of the 512^2 frames:
  non-content: bytes (PNG file size, one scalar, used as is: AUC printed raw and folded);
               border (exact-zero pixel mask: its fraction + 16x16-block means = 32x32 grid, logistic);
               background (face-blanked copy from blank.py: 32x32x3 block-mean thumbnail, logistic);
  content    : thumb32 (whole image, 32x32x3 block means, logistic); face (background-blanked copy, same).
Block means are numpy averages over 16x16 pixel blocks (a feature; nothing is written or shown to a detector).
Learned baselines: out-of-fold scores, 5-fold GroupKFold by host person, one probe per contrast.
FRLL benchmark side: raw-file bytes, width, height for R0raw vs R4pub per tool (one scalar each).
Writes OUT/scores/baselines_oof.npz (key '<pool>|<tool>|<contrast>|<baseline>' -> ids, scores) and
experiments/AR1/baselines.json.
"""
import csv
import json
import os
import pathlib
import sys
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import stats  # noqa: E402

CONTRASTS = (("R0", "R2"), ("R2", "R3"), ("R3", "R4"), ("R2", "R4"), ("R0", "R4"), ("R3", "NC"),
             ("R0", "R2w"), ("R2w", "R4"), ("R2w", "R3m"), ("R3m", "R4"), ("R2w", "R3"),
             ("R2wm", "R4"), ("R0", "R2wm"), ("R2wm", "R3m"), ("R2w4", "R4"), ("R2w", "R2w4"), ("R0", "R2w4"))
BASES = ("bytes", "border", "background", "thumb32", "face", "band", "lapvar")


def blocks(img):
    h, w = img.shape[:2]
    return img.reshape(32, h // 32, 32, w // 32, -1).mean((1, 3)).ravel().astype(np.float32)


def feats(args):
    import cv2
    import stats as _st   # a41_read luminance / power_profile / band_shares (unchanged)
    i, p, bgp, fap = args
    img = cv2.imread(p)
    z = (img == 0).all(2).astype(np.float32)
    Y = _st.M.luminance(img[..., ::-1])
    f = dict(bytes=np.array([os.path.getsize(p)], np.float32),
             border=np.r_[z.mean(), blocks(z[..., None])].astype(np.float32),
             thumb32=blocks(img.astype(np.float32)),
             band=np.array(_st.M.band_shares(_st.M.power_profile(Y)[0]), np.float32),
             lapvar=np.array([cv2.Laplacian(Y, cv2.CV_64F).var()], np.float32))
    if fap:
        f["background"] = blocks(cv2.imread(fap).astype(np.float32))
        f["face"] = blocks(cv2.imread(bgp).astype(np.float32))
    return i, f


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="compute only contrasts containing this rung and merge into the outputs")
    ap.add_argument("--feats", default="", help="comma list of baselines to compute (default all); merged into outputs")
    a = ap.parse_args()
    from gate_c import oof
    man = {r["id"]: r for r in csv.DictReader(open(K.OUT / "manifest.csv"))}
    bl = {r["id"]: r for r in csv.DictReader(open(K.OUT / "blank/blank_manifest.csv"))}
    todo = [(i, r["path"], bl[i]["bg_path"] if i in bl else "", bl[i]["face_path"] if i in bl else "")
            for i, r in man.items() if r["pool"] in ("frgcferet", "frll") and (not a.only or r["rung"] in
                                                                                  ("R0", "R3m", "R4", "R2w", a.only)) and r["rung"] in ("R0", "R2", "R3", "R4", "NC", "R2w", "R3m", "R2wm", "R2w4")]
    with Pool(12) as p:
        F = dict(p.map(feats, todo, chunksize=16))
    oofs, summ = {}, {}
    for pool in ("frgcferet", "frll"):
        pers = sorted({r["p1"] for r in man.values() if r["pool"] == pool} |
                      {r["p2"] for r in man.values() if r["pool"] == pool})
        D = stats.Draw(pers, 2000, [20261111, 1])
        r0 = [r for r in man.values() if r["pool"] == pool and r["rung"] == "R0"]
        for tool in ("opencv", "facemorpher"):
            rows = {g: [r for r in man.values() if r["pool"] == pool and r["tool"] == tool and r["rung"] == g]
                    for g in ("R2", "R3", "R4", "NC", "R2w", "R3m", "R2wm", "R2w4")}
            rows["R0"] = r0
            for neg, pos in CONTRASTS:
                if a.only and a.only not in (neg, pos):
                    continue
                rr = rows[neg] + rows[pos]
                y = np.array([0] * len(rows[neg]) + [1] * len(rows[pos]))
                g = np.array([r["p1"] for r in rr])
                P = [(r["p1"], r["p2"]) for r in rows[pos]]
                N = [(r["p1"], r["p2"]) for r in rows[neg]]
                if not rows[neg] or not rows[pos]:
                    continue
                for b in BASES:
                    if (a.feats and b not in a.feats.split(",")) or b not in F[rr[0]["id"]]:
                        continue
                    X = np.stack([F[r["id"]][b] for r in rr])
                    s = X[:, 0] if b in ("bytes", "lapvar") else (oof(X, y, g) if np.ptp(X) > 0 else np.zeros(len(y)))
                    au, c = stats.wauc_ci(D, s[y == 1], P, s[y == 0], N)
                    key = f"{pool}|{tool}|{pos}vs{neg}|{b}"
                    oofs[key + "|id"] = np.array([r["id"] for r in rr])
                    oofs[key + "|score"] = s.astype(np.float32)
                    summ[key] = dict(auc=au, ci95=c, folded=stats.fold(au),
                                     kind="non-content" if b in ("bytes", "border", "background") else
                                     ("low-level statistic" if b in ("band", "lapvar") else "content"))
                    print(key, round(au, 3), [round(x, 3) for x in c], flush=True)
    if a.only or a.feats:
        old = dict(np.load(K.OUT / "scores/baselines_oof.npz"))
        old.update(oofs)
        np.savez(K.OUT / "scores/baselines_oof.npz", **old)
        js = json.load(open(K.RES / "baselines.json"))
        js.update(summ)
        json.dump(js, open(K.RES / "baselines.json", "w"), indent=1)
        return
    # FRLL benchmark side: raw file attributes
    from PIL import Image
    pers = sorted({r["p1"] for r in man.values() if r["pool"] == "frll_bench"} |
                  {r["p2"] for r in man.values() if r["pool"] == "frll_bench"})
    D = stats.Draw(pers, 2000, [20261111, 1])
    r0 = [r for r in man.values() if r["pool"] == "frll_bench" and r["rung"] == "R0raw"]
    for tool in ("opencv", "facemorpher"):
        r4 = [r for r in man.values() if r["pool"] == "frll_bench" and r["tool"] == tool and r["rung"] == "R4pub"]
        for b in ("bytes", "width", "height"):
            def v(r):
                if b == "bytes":
                    return os.path.getsize(r["path"])
                with Image.open(r["path"]) as im:
                    return im.size[0] if b == "width" else im.size[1]
            au, c = stats.wauc_ci(D, [v(r) for r in r4], [(r["p1"], r["p2"]) for r in r4],
                                  [v(r) for r in r0], [(r["p1"],) for r in r0])
            summ[f"frll_bench|{tool}|R4pubvsR0raw|{b}"] = dict(auc=au, ci95=c, folded=stats.fold(au), kind="non-content")
    np.savez(K.OUT / "scores/baselines_oof.npz", **oofs)
    json.dump(summ, open(K.RES / "baselines.json", "w"), indent=1)


if __name__ == "__main__":
    main()

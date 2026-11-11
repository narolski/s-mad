"""Amendment 9b: swap-splice SW (diagnostic only, never for training). Inside the R4 hull: B warped to the R4 mean shape
(variants.warp_cv, the OpenCV-style tool's own warp routine, B texture only); outside: R2w4. Pixel copy only.
Also the seam statistics of S4, S0, SW (signed luma and R-G step and mean absolute luma step between a 3-px ring inside
and a 3-px ring outside the hull; measurement only).
  python3 -I swap.py build [--limit 8]  -> OUT/img/frgcferet/opencv/SW/, OUT/manifest_swap.csv, experiments/AR1/swap_seam.csv
"""
import argparse
import csv
import pathlib
import sys
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import splice as SP  # noqa: E402
import variants as V  # noqa: E402


def seam(img, m):
    import cv2
    k = np.ones((7, 7), np.uint8)
    mu = m.astype(np.uint8)
    inner = mu & (1 - cv2.erode(mu, k))
    outer = cv2.dilate(mu, k) & (1 - mu)
    f = img.astype(np.float32)
    Y = 0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2]
    RG = f[..., 2] - f[..., 1]
    dil = cv2.dilate(mu, np.ones((3, 3), np.uint8))
    ero = cv2.erode(mu, np.ones((3, 3), np.uint8))
    # mean absolute luma step: |Y(p) - Y(p')| for boundary pixels vs their 3x3 neighbourhood mean across the boundary
    return [float(Y[inner == 1].mean() - Y[outer == 1].mean()), float(RG[inner == 1].mean() - RG[outer == 1].mean()),
            float(np.abs(Y[(ero == 0) & (mu == 1)].mean() - Y[(dil == 1) & (mu == 0)].mean()))]


def one(r):
    import cv2
    stem = r["pid"].replace(":", "_")
    d = K.OUT / "img/frgcferet/opencv"
    base = cv2.imread(str(d / "R2w4" / f"{stem}.png"))
    m = SP.hull(r["H"][:-4] + ".tem", r["B"][:-4] + ".tem", base.shape)
    o = d / "SW" / f"{stem}.png"
    if not o.exists():
        hm = V._load(K.MC / "scripts/68_hires_morph.py", "hm68")
        b = cv2.imread(r["B"])
        bw = V.warp_cv(b, K.read_tem(r["B"][:-4] + ".tem"), K.read_tem(r["H"][:-4] + ".tem"), hm)
        sw = base.copy()
        sw[m] = bw[m]
        o.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(o), sw)
    rows = []
    for arm in ("S4", "S0", "SW"):
        img = cv2.imread(str(d / arm / f"{stem}.png"))
        rows.append(dict(host=r["pid"], arm=arm, tone_luma=None, tone_rg=None, abs_step=None))
        rows[-1]["tone_luma"], rows[-1]["tone_rg"], rows[-1]["abs_step"] = seam(img, m)
    return r, str(o), rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("build",))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    pool = list(csv.DictReader(open(K.OUT / "pool.csv")))[: a.limit or None]
    with Pool(2) as p:
        res = p.map(one, pool, chunksize=8)
    man, sm = [], []
    for r, path, rows in res:
        man.append(dict(id=f"sw_SW_opencv_{r['pid'].replace(':', '_')}", path=path, pool="frgcferet", tool="opencv",
                        rung="SW", p1=r["pid"], p2=r["B_pid"]))
        sm += rows
    sfx = "" if not a.limit else "_smoke"
    with open(K.OUT / f"manifest_swap{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0]))
        w.writeheader()
        w.writerows(man)
    with open(K.RES / f"swap_seam{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sm[0]))
        w.writeheader()
        w.writerows(sm)
    import collections
    g = collections.defaultdict(list)
    for x in sm:
        g[x["arm"]].append((x["tone_luma"], x["tone_rg"], x["abs_step"]))
    for k, v in g.items():
        v = np.array(v)
        print(k, "median tone luma %.2f, R-G %.2f, |step| %.2f" % tuple(np.median(v, 0)))


if __name__ == "__main__":
    main()

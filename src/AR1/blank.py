"""AR4 / AR3: constant-colour blanking. Face mask = convex hull (cv2.fillConvexPoly, a drawn mask, no resampling) of the
image's 106-point face geometry w1 * tem1 + (1 - w1) * tem2 (manifest columns). Variant 'bg': outside the hull set to
(128, 128, 128); 'face': inside the hull set to (128, 128, 128). Lossless PNG.

  python3 -I blank.py --pools frgcferet --rungs R0,R2,R3,R4,NC [--limit 8]
Writes OUT/blank/<variant>/<id>.png and OUT/blank/blank_manifest.csv (id, path, bg_path, face_path).
"""
import argparse
import csv
import pathlib
import sys
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

GREY = (128, 128, 128)


def hull_mask(r, shape):
    import cv2
    import numpy as np
    w = float(r["w1"])
    pts = w * K.read_tem(r["tem1"]) + (1 - w) * K.read_tem(r["tem2"])
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillConvexPoly(m, cv2.convexHull(np.rint(pts).astype(np.int32)), 1)
    return m.astype(bool)


def one(r):
    import cv2
    out = K.OUT / "blank"
    bg, fa = out / "bg" / f"{r['id']}.png", out / "face" / f"{r['id']}.png"
    if bg.exists() and fa.exists():
        return r["id"], str(bg), str(fa)
    img = cv2.imread(r["path"])
    m = hull_mask(r, img.shape)
    b = img.copy()
    b[~m] = GREY
    f = img.copy()
    f[m] = GREY
    cv2.imwrite(str(bg), b)
    cv2.imwrite(str(fa), f)
    return r["id"], str(bg), str(fa)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", default="frgcferet")
    ap.add_argument("--rungs", default="R0,R2,R3,R4,NC")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    for v in ("bg", "face"):
        (K.OUT / "blank" / v).mkdir(parents=True, exist_ok=True)
    rows = [r for r in csv.DictReader(open(K.OUT / "manifest.csv"))
            if r["pool"] in a.pools.split(",") and r["rung"] in a.rungs.split(",") and r["tem1"]]
    rows = rows[: a.limit or None]
    with Pool(a.workers) as p:
        res = p.map(one, rows, chunksize=16)
    src = {r["id"]: r["path"] for r in rows}
    with open(K.OUT / "blank" / ("blank_manifest.csv" if not a.limit else "blank_manifest_smoke.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "path", "bg_path", "face_path"])
        for i, b, fa in res:
            w.writerow([i, src[i], b, fa])
    print(len(res), "blanked")


if __name__ == "__main__":
    main()

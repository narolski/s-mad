"""PN1 amendment 11 (H-new-5): face-blanked copies of the corrected-MAD22 (bench_s) and H1 evaluation frames: constant
grey 128 inside the convex hull of AF0's fixed canonical landmarks (allowed operation: constant-colour region
blanking). Written as lossless PNG to /mnt/t7/smad_next/PN1/img/blank_bench/; list lists/bench_blank.csv."""
import csv
import pathlib
import sys

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/PN1/img/blank_bench")
L = pathlib.Path("/mnt/t7/smad_next/PN1/lists")


def main():
    import cv2
    lm = np.load("/mnt/t7/smad_next/AF0/canonical_lm.npy")
    mask = np.zeros((512, 512), np.uint8)
    cv2.fillConvexPoly(mask, cv2.convexHull(np.round(lm).astype(np.int32)), 1)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    src = [r for r in csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/bench_s.csv")) if r["cell"].startswith("mad22")]
    src += list(csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/h1.csv")))
    for r in src:
        o = OUT / f"{r['id']}__face.png"
        if not o.exists():
            img = cv2.imread(r["path"])
            assert img.shape == (512, 512, 3)
            img[mask == 1] = 128
            assert cv2.imwrite(str(o), img)
        x = dict(r)
        x.update(id=r["id"] + "__face", path=str(o))
        rows.append(x)
    with open(L / "bench_blank.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("bench_blank", len(rows), "hull pixels", int(mask.sum()))


if __name__ == "__main__":
    main()

"""AF0 32-pixel thumbnail baseline features: 16 x 16 block means of the 512^2 frame (a numpy reduction, never written
as an image or shown to any model), (N, 32, 32, 3) float32 per list, as AR1's thumbnail baseline.
  python3 -I thumbs.py af0_w1 ar1 bench --workers 2
"""
import argparse
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402


def thumb(p):
    import cv2
    cv2.setNumThreads(1)
    im = cv2.imread(p)[:, :, ::-1].astype(np.float32)
    assert im.shape == (512, 512, 3), p
    return im.reshape(32, 16, 32, 16, 3).mean((1, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lists", nargs="+")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    from multiprocessing import Pool
    for n in a.lists:
        out = L.OUT / "thumbs" / f"{n}.npz"
        if out.exists():
            continue
        R = L.rows(n)
        with Pool(a.workers) as p:
            T = np.stack(p.map(thumb, [r["path"] for r in R], chunksize=16))
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(out, ids=np.array([r["id"] for r in R]), thumb=T)
        print(n, T.shape, flush=True)


if __name__ == "__main__":
    main()

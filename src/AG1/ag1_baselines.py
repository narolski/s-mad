"""AG1 simple baselines per image (amendment 3, rules 4 and 5; DGX CPU; measurement only, no image is written).
For every row of manifests/ag1.csv (the 512 aligned frames the detectors score):
  bytes   file size of the frame PNG
  lapvar  variance of the 3 x 3 Laplacian (cv2.Laplacian, CV_64F) of the gray frame
  hfband  share of the gray frame's spectral power beyond half the Nyquist radius (numpy FFT, DC removed)
  sym     mean absolute difference between the gray frame and its left-right mirror (the frame is symmetric about
          the eye midpoint: prep_eval puts the eyes at x = 190 and 322 of 512); larger = less symmetric
  thumb   32 x 32 block mean of the gray frame (16 x 16 blocks, the EV1 thumbnail; no resampling routine)
Out: DATA/baselines.npz (id, bytes, lapvar, hfband, sym, thumb[n, 1024]).
Usage: python -I ag1_baselines.py DATA [--workers 8]
"""
import csv
import os
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

DATA = None


def feat(rel):
    import cv2
    p = DATA / rel
    g = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    if g is None or g.shape != (512, 512):
        raise RuntimeError(f"{p}: not a 512 x 512 frame")
    gf = g.astype(np.float64)
    lap = cv2.Laplacian(gf, cv2.CV_64F).var()
    F = np.abs(np.fft.fftshift(np.fft.fft2(gf - gf.mean()))) ** 2
    yy, xx = np.mgrid[-256:256, -256:256]
    r = np.hypot(yy, xx) / 256.0
    hf = F[r > 0.5].sum() / max(F.sum(), 1e-12)
    sym = np.abs(gf - gf[:, ::-1]).mean()
    th = gf.reshape(32, 16, 32, 16).mean((1, 3)).ravel().astype(np.float32)
    return os.path.getsize(p), lap, hf, sym, th


def main():
    global DATA
    DATA = pathlib.Path(sys.argv[1])
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    rows = list(csv.DictReader(open(DATA / "manifests/ag1.csv")))
    with Pool(workers) as pool:
        R = pool.map(feat, [r["path"] for r in rows], chunksize=16)
    np.savez(DATA / "baselines.npz", id=np.array([r["id"] for r in rows]),
             bytes=np.array([x[0] for x in R], np.float64), lapvar=np.array([x[1] for x in R]),
             hfband=np.array([x[2] for x in R]), sym=np.array([x[3] for x in R]),
             thumb=np.stack([x[4] for x in R]))
    print(f"BASELINES {len(rows)} frames")


if __name__ == "__main__":
    main()

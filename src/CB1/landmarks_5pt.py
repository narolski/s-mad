"""CB1: five facial points for the FD-MAD fused branch (landmark input only; no image is written or changed).

insightface FaceAnalysis detection module (buffalo_l SCRFD det_10g, the RetinaFace-style five points: left eye, right
eye, nose, left and right mouth corner), CPU, largest face, det_size 320 (at 640 the detector found 1 of 40 eval frames and 7 of 40 SMDD frames; at 320 all 80). Points are stored normalised by the image width
and height, so they can be scaled to any loader side. No face: NaN.
  python3 -I landmarks_5pt.py --list PATHS.txt --out OUT.npz [--limit N]
"""
import argparse
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    import cv2
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(320, 320))
    paths = [l.strip() for l in open(a.list) if l.strip()]
    if a.limit:
        paths = paths[:a.limit]
    K = np.full((len(paths), 5, 2), np.nan, np.float32)
    S = np.zeros(len(paths), np.float32)
    t0 = time.time()
    for i, p in enumerate(paths):
        img = cv2.imread(p)
        if img is None:
            continue
        fs = app.get(img)
        if fs:
            f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
            K[i] = f.kps / np.array([img.shape[1], img.shape[0]], np.float32)
            S[i] = f.det_score
        if i % 2000 == 0:
            print(f"{i}/{len(paths)} ({time.time() - t0:.0f}s)", flush=True)
    np.savez(a.out, path=np.array(paths), kps=K, det_score=S)
    print(f"WRITTEN {a.out}: {len(paths)} images, no face {int(np.isnan(K[:, 0, 0]).sum())}")


if __name__ == "__main__":
    main()

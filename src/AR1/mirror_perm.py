"""R3m support: the left-right index permutation of the insightface 106-point layout, measured (not assumed).
For N host frames: flip losslessly (cv2.flip, x -> W-1-x), run the same 106-point detector as 73_delin_align.app() on
the flipped frame, and assign each mirrored original point (W-1-x, y) to the detected points (Hungarian, by distance).
The permutation must be identical on every frame and an involution; written to OUT/mirror_perm106.json with the
per-frame residuals. Measurement only (landmark detection); no image is written.
  python3 -I mirror_perm.py [--n 24]
"""
import argparse
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=24)
    a = ap.parse_args()
    import cv2
    from scipy.optimize import linear_sum_assignment
    da = K.load_module(K.MC / "scripts/73_delin_align.py", "delin_align")
    rows = list(csv.DictReader(open(K.OUT / "pool.csv")))[:: max(1, 536 // a.n)][: a.n]
    perms, res = [], []
    for r in rows:
        img = cv2.imread(r["H"])
        W = img.shape[1]
        lm = K.read_tem(r["H"][:-4] + ".tem")
        fl = cv2.flip(img, 1)
        fc = da.app().get(fl)
        f = max(fc, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        det = f.landmark_2d_106.astype(np.float32)
        mir = lm.copy()
        mir[:, 0] = W - 1 - mir[:, 0]
        d = np.linalg.norm(mir[:, None] - det[None], axis=2)
        i, j = linear_sum_assignment(d)
        perm = np.empty(106, int)
        perm[j] = i            # detected index j on the flipped image <- original index perm[j]
        perms.append(perm)
        res.append(float(d[i, j].mean()))
    P = np.array(perms)
    mode = np.array([np.bincount(P[:, k], minlength=106).argmax() for k in range(106)])
    agree = float((P == mode[None]).mean())
    invol = bool((mode[mode] == np.arange(106)).all())
    out = dict(perm=mode.tolist(), frames=len(rows), agreement=agree, involution=invol,
               mean_residual_px=float(np.mean(res)), max_residual_px=float(np.max(res)),
               fixed_points=[int(k) for k in range(106) if mode[k] == k])
    json.dump(out, open(K.OUT / "mirror_perm106.json", "w"), indent=1)
    json.dump(out, open(K.RES / "mirror_perm106.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "perm"}))


if __name__ == "__main__":
    main()

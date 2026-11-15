"""Mirror-asymmetry test (AS0): shared paths, guards and small helpers. Measurement only: no image is written.

Conventions (registered in experiments/AS0_mirror-asymmetry/prereg.md):
  flip      : lossless left-right flip about the frame's vertical centre line, x -> W-1-x (numpy index reversal,
              the same flip cv2.flip(img, 1) and torch.flip(dims=[-1]) perform and that built the mirror rungs).
  landmarks : the 106-point insightface layout of 73_delin_align / prep_eval (.tem files where they exist; otherwise
              detected with the same insightface buffalo_l 2d106det model on the CPU, see as0_landmarks.py).
"""
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path("/home/narolski/smad-next")
SRC = REPO / "src/AS0"
RES = REPO / "experiments/AS0_mirror-asymmetry"
OUT = pathlib.Path("/mnt/t7/smad_next/AS0")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
MC = pathlib.Path("/home/narolski/mambamorph-code")
PERM106 = np.array(json.load(open(REPO / "experiments/AR1/mirror_perm106.json"))["perm"])
assert (PERM106[PERM106] == np.arange(106)).all()

# 106-point layout (indices measured from the AR1 mean shape, README section 3)
CONTOUR_L = [1, 9, 10, 11, 12, 13, 14, 15, 16, 2, 3, 4, 5, 6, 7, 8]      # image-left side, temple -> chin
CONTOUR_R = [17, 25, 26, 27, 28, 29, 30, 31, 32, 18, 19, 20, 21, 22, 23, 24]
CHIN = 0
BROW_L_TOP = [43, 48, 49, 51, 50]        # image-left brow, upper edge, outer -> inner
BROW_R_TOP = [101, 105, 104, 103, 102]   # image-right brow, upper edge, outer -> inner


def face_polygon(lm):
    """closed polygon: left contour temple -> chin, right contour chin -> temple, right brow top outer -> inner,
    left brow top inner -> outer. Excludes forehead/hair above the brows, ears and backdrop."""
    idx = CONTOUR_L + [CHIN] + CONTOUR_R[::-1] + BROW_R_TOP + BROW_L_TOP[::-1]
    return lm[idx]
PUPIL_L, PUPIL_R = 38, 92
NOSE_TIP = 86
MIDLINE = [0, 53, 60, 62, 71, 72, 73, 74, 80, 86]   # fixed points of the mirror permutation


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def guard(p):
    if forbidden(p):
        sys.exit(f"refusing forbidden path {p}")
    return p


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_tem(path):
    lines = open(guard(path)).read().splitlines()
    n = int(lines[0].strip())
    return np.array([list(map(float, lines[i].split())) for i in range(1, n + 1)], np.float64)


def mirror_shape(lm, W):
    """mirrored, re-indexed shape of an image of width W (as AR1 variants.mirror writes the mirror .tem)."""
    m = lm[PERM106].copy()
    m[:, 0] = W - 1 - m[:, 0]
    return m


def read_csv(p):
    return list(csv.DictReader(open(guard(p))))


def write_csv(p, rows, fields=None):
    fields = fields or list(rows[0])
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

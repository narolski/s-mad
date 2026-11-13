"""Layer misregistration echo (ME1): measurements in memory (lead's ruling in NOTEBOOK: phase correlation between images
in memory and echo / autocorrelation statistics are measurements; nothing shifted or filtered is stored).
Rows: the 291 BD1 hosts (FS1 evaluation frames, OpenCV-style). Hull: AR1 amendment-7b hull (mean(H, B) landmarks) for
S4, S3, S0, R2w4, R2w, R4, R3; H's own hull for R0, R0_61. Luminance Y (BT.601).
Oracle (needs the counterpart): warped halves inside the hull from existing images by arithmetic, since a 50% OpenCV
morph is the mean of its two warped halves: two-person H_w = R2w4, B_w = 2 S4 - R2w4; same-person H_w = R2w,
S_w = 2 S3 - R2w (uint8 rounding gives errors of about 1 level). Phase correlation (cv2.phaseCorrelate, Hann window)
in 24 x 24 windows on a 12 px grid, windows fully inside the hull eroded by 12 px; statistic: median shift magnitude
(px); also median peak response.
Single image: in 24 x 24 windows (12 px grid) of the Sobel gradient magnitude, mean removed and Hann-windowed:
autocorrelation by FFT; echo = max over lags with 2 <= max(|dx|, |dy|) <= 8, excluding lags whose dx or dy is a
non-zero multiple of 8 (JPEG block period), of AC(lag) / AC(0). Statistic: median echo over hull windows (hull
eroded by 4 px) divided by the median over windows fully inside an outer ring of at least the hull's area; the hull
median alone is printed.
Out: /mnt/t7/smad_next/ME1/me1_feats.csv (+ .sha256).   nice -n 19 python3 -I me1_measure.py [--limit 6]"""
import argparse
import csv
import hashlib
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import splice as ARS  # noqa: E402
sys.path.insert(0, "/home/narolski/smad-next/src/TB1")
from tb1_measure import dilate, erode, ring_of  # noqa: E402

MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
EVAL = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/ME1")
WIN, STEP = 24, 12
NAMES = ("S4", "S3", "S0", "R2w4", "R2w", "R4", "R3", "R0", "R0_61")


def Y(p):
    import cv2
    x = cv2.imread(str(p)).astype(np.float64)
    return 0.114 * x[..., 0] + 0.587 * x[..., 1] + 0.299 * x[..., 2]


def windows(mask):
    h, w = mask.shape
    out = []
    for y in range(0, h - WIN + 1, STEP):
        for x in range(0, w - WIN + 1, STEP):
            if mask[y:y + WIN, x:x + WIN].all():
                out.append((y, x))
    return out


HANN = np.outer(np.hanning(WIN), np.hanning(WIN))
LAGS = [(dy, dx) for dy in range(-8, 9) for dx in range(-8, 9)
        if 2 <= max(abs(dy), abs(dx)) <= 8 and not (dx != 0 and dx % 8 == 0) and not (dy != 0 and dy % 8 == 0)]


def echo(gm, wins):
    if not wins:
        return np.nan
    W = np.stack([gm[y:y + WIN, x:x + WIN] for y, x in wins])
    W = (W - W.mean(axis=(1, 2), keepdims=True)) * HANN
    F = np.fft.fft2(W, s=(2 * WIN, 2 * WIN))
    ac = np.fft.ifft2(np.abs(F) ** 2).real
    a0 = ac[:, 0, 0] + 1e-12
    vals = np.stack([ac[:, dy % (2 * WIN), dx % (2 * WIN)] for dy, dx in LAGS], 1)
    return float(np.median(vals.max(1) / a0))


def phase_shift(a, b, wins):
    import cv2
    sh, rs = [], []
    hann = cv2.createHanningWindow((WIN, WIN), cv2.CV_64F)
    for y, x in wins:
        (dx, dy), r = cv2.phaseCorrelate(a[y:y + WIN, x:x + WIN], b[y:y + WIN, x:x + WIN], hann)
        sh.append(np.hypot(dx, dy))
        rs.append(r)
    return (float(np.median(sh)), float(np.median(rs))) if sh else (np.nan, np.nan)


def main():
    import cv2
    cv2.setNumThreads(1)
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    man = [r for r in csv.DictReader(open(MAN)) if r["role"] in ("dev", "test")]
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    by = {}
    for r in man:
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3", "S0"):
            by.setdefault(r["host"], {})[r["rung"]] = r
        elif r["fam"] == "ladder" and r["tool"] in ("opencv", "none") and r["rung"] in ("R2w4", "R2w", "R4", "R3", "R0"):
            key = r["rung"] + ("_" + r["strength"] if r["strength"] else "")
            if r["strength"] in ("", "61") and (r["rung"] == "R0" or r["strength"] == ""):
                by.setdefault(r["host"], {})[key] = r
    hosts = sorted(h for h, d in by.items() if all(k in d for k in NAMES))[: a.limit or None]
    out = []
    for h in hosts:
        P, d = pool[h], by[h]
        m7 = ARS.hull(P["H"][:-4] + ".tem", P["B"][:-4] + ".tem", (512, 512))
        mH = ARS.hull(P["H"][:-4] + ".tem", P["H"][:-4] + ".tem", (512, 512))
        rec = dict(host=h, db=P["db"], role=d["S4"]["role"])
        Yi = {n: Y(EVAL / d[n]["path"]) for n in NAMES}
        wo = windows(erode(m7, 12))
        for tag, sp, cp in (("O4", "S4", "R2w4"), ("O3", "S3", "R2w")):
            assert np.abs(Yi[sp] - Yi[cp])[~m7].max() < 1e-9, (h, sp)
            hw = Yi[cp]
            xw = np.clip(2 * Yi[sp] - Yi[cp], 0, 255)
            rec[f"{tag}_shift"], rec[f"{tag}_resp"] = phase_shift(hw, xw, wo)
            rec[f"{tag}_nwin"] = len(wo)
        for n in NAMES:
            m = mH if n.startswith("R0") else m7
            gm = np.hypot(cv2.Sobel(Yi[n], cv2.CV_64F, 1, 0, ksize=3), cv2.Sobel(Yi[n], cv2.CV_64F, 0, 1, ksize=3))
            ein = echo(gm, windows(erode(m, 4)))
            eout = echo(gm, windows(ring_of(m, dilate(m, 4))))
            rec[f"{n}_echo_in"], rec[f"{n}_echo_out"] = ein, eout
            rec[f"{n}_echo_ratio"] = ein / eout if eout and np.isfinite(eout) else np.nan
            rec[f"{n}_id"] = d[n]["id"]
        out.append(rec)
    tag = f"me1_feats_limit{a.limit}" if a.limit else "me1_feats"
    f = OUT / f"{tag}.csv"
    if f.exists():
        sys.exit(f"{f} exists; refusing to overwrite")
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    hsh = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / f"{tag}.csv.sha256").write_text(f"{hsh}  {f.name}\n")
    print("hosts", len(out), "sha256", hsh)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

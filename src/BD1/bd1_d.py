"""Blend-difference attribution (BD1): blend-difference energy D of every OpenCV-style splice of the FS1 evaluation list
(S4 and S3, development and test hosts). No new image operation: D is a subtraction of two existing stored images.
  S4 = R2w4 with the R4 pixels copied inside the hull; counterpart R2w4.
  S3 = R2w  with the R3 pixels copied inside the same hull; counterpart R2w.
AR1 amendment 7b (splice.py job7b, the build of the current files): one hull for every arm, mean(H, B) landmarks
(the R4 geometry). The hull is rebuilt with AR1's own splice.hull (imported unchanged) from those .tem files.
D = mean over hull pixels and the 3 channels of |S - counterpart| (0-255). D_Y = the same on luma. Asserted: S equals
its counterpart outside the hull. Out: /mnt/t7/smad_next/BD1/d_values.csv (+ .sha256).
Amendment 1 (pre-run review): also S0 (= R2w4 outside, R2w inside the same hull; counterpart R2w4; identity-free);
D_int = D on the hull eroded by 5 px (cv2.erode, 11x11 ellipse; a mask operation), D_band = D on hull minus interior;
G = mean landmark distance (px) between mean(H, S) and mean(H, B), the geometry gap of S3's inside against the hull;
host and partner databases.
  python3 -I bd1_d.py [--limit 8]"""
import argparse
import csv
import hashlib
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import splice as ARS  # noqa: E402   (AR1 splice builder: hull() only)

SPL = pathlib.Path("/mnt/t7/smad_next/PN1/lists/splice_nat.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/BD1")


def main():
    import cv2
    cv2.setNumThreads(1)
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    ev = {r["id"]: r for r in csv.DictReader(open(MAN)) if r["fam"] == "splice" and r["rung"] in ("S0", "S3", "S4")}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rows = [r for r in csv.DictReader(open(SPL)) if r["id"] in ev and r["tool"] == "opencv"]
    assert len(rows) == 873, len(rows)
    rows = rows[: a.limit or None]
    out = []
    for r in rows:
        d = os.path.dirname(os.path.dirname(r["path"]))
        stem = os.path.basename(r["path"])[:-4]
        base = "R2w" if r["rung"] == "S3" else "R2w4"
        P = pool[r["p1"]]
        X = P["B"]                                                 # amendment 7b: R4 hull for every arm
        S = cv2.imread(r["path"]).astype(np.int16)
        Bimg = cv2.imread(f"{d}/{base}/{stem}.png").astype(np.int16)
        m = ARS.hull(P["H"][:-4] + ".tem", X[:-4] + ".tem", S.shape)
        diff = np.abs(S - Bimg)
        assert diff[~m].max() == 0, ("splice differs outside the hull", r["id"])
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        mi = cv2.erode(m.astype(np.uint8), k).astype(bool)
        mb = m & ~mi
        g = float(np.linalg.norm(0.5 * (ARS.K.read_tem(P["H"][:-4] + ".tem") + ARS.K.read_tem(P["S"][:-4] + ".tem"))
                                 - 0.5 * (ARS.K.read_tem(P["H"][:-4] + ".tem") + ARS.K.read_tem(X[:-4] + ".tem")), axis=1).mean())
        w = np.array([0.114, 0.587, 0.299])                       # BGR luma weights
        dy = np.abs((S * w).sum(2) - (Bimg * w).sum(2))
        out.append(dict(id=r["id"], rung=r["rung"], role=ev[r["id"]]["role"], host=r["p1"], counterpart=base,
                        hull_px=int(m.sum()), D=float(diff[m].mean()), D_Y=float(dy[m].mean()),
                        D_int=float(diff[mi].mean()), D_band=float(diff[mb].mean()), G=g, db_host=P["db"],
                        db_partner=pool[P["B_pid"]]["db"] if P["B_pid"] in pool else ""))
    tag = f"d_values_limit{a.limit}" if a.limit else "d_values"
    f = OUT / f"{tag}.csv"
    if f.exists():
        sys.exit(f"{f} exists; refusing to overwrite")
    with open(f, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0]))
        wr.writeheader()
        wr.writerows(out)
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / f"{tag}.csv.sha256").write_text(f"{h}  {f.name}\n")
    print("rows", len(out), "sha256", h)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

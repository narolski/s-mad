"""Blend-difference attribution (BD1): blend-difference energy D of every OpenCV-style splice of the FS1 evaluation list
(S4 and S3, development and test hosts). No new image operation: D is a subtraction of two existing stored images.
  S4 = R2w4 with the R4 pixels copied inside the hull; counterpart R2w4.
  S3 = R2w  with the R3 pixels copied inside the same hull; counterpart R2w.
AR1 amendment 7b (splice.py job7b, the build of the current files): one hull for every arm, mean(H, B) landmarks
(the R4 geometry). The hull is rebuilt with AR1's own splice.hull (imported unchanged) from those .tem files.
D = mean over hull pixels and the 3 channels of |S - counterpart| (0-255). D_Y = the same on luma. Asserted: S equals
its counterpart outside the hull. Out: /mnt/t7/smad_next/BD1/d_values.csv (+ .sha256).
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
    ev = {r["id"]: r for r in csv.DictReader(open(MAN)) if r["fam"] == "splice" and r["rung"] in ("S3", "S4")}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rows = [r for r in csv.DictReader(open(SPL)) if r["id"] in ev and r["tool"] == "opencv"]
    assert len(rows) == 582, len(rows)
    rows = rows[: a.limit or None]
    out = []
    for r in rows:
        d = os.path.dirname(os.path.dirname(r["path"]))
        stem = os.path.basename(r["path"])[:-4]
        base = "R2w4" if r["rung"] == "S4" else "R2w"
        P = pool[r["p1"]]
        X = P["B"]                                                 # amendment 7b: R4 hull for every arm
        S = cv2.imread(r["path"]).astype(np.int16)
        Bimg = cv2.imread(f"{d}/{base}/{stem}.png").astype(np.int16)
        m = ARS.hull(P["H"][:-4] + ".tem", X[:-4] + ".tem", S.shape)
        diff = np.abs(S - Bimg)
        assert diff[~m].max() == 0, ("splice differs outside the hull", r["id"])
        w = np.array([0.114, 0.587, 0.299])                       # BGR luma weights
        dy = np.abs((S * w).sum(2) - (Bimg * w).sum(2))
        out.append(dict(id=r["id"], rung=r["rung"], role=ev[r["id"]]["role"], host=r["p1"], counterpart=base,
                        hull_px=int(m.sum()), D=float(diff[m].mean()), D_Y=float(dy[m].mean())))
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

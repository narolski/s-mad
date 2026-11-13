"""BD1 amendment 2 (BD1b): colour and texture decomposition of the inside difference S - counterpart for every
OpenCV-style S0, S3, S4 splice of the FS1 list (statistics only; no image is created or written).
Inside the amendment-7b hull (mean(H, B) landmarks; AR1 splice.hull unchanged), with d = S - C per channel (0-255):
  D_dc   = mean over channels of |mean(d)|                        (mean colour shift)
  D_ac   = mean |d - mean(d)| over hull pixels and channels         (difference with the mean shift removed)
  D_lin  = mean |S - (a*C + b)| with per-channel least-squares a, b inside the hull (gain and offset removed)
  D_grad = mean of |dx d| + |dy d| over hull pixels whose right / lower neighbour is in the hull
Out: /mnt/t7/smad_next/BD1/d_feats.csv (+ .sha256).   python3 -I bd1b_feat.py [--limit 9]"""
import argparse
import csv
import hashlib
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import splice as ARS  # noqa: E402

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
    assert len(rows) == 873
    rows = rows[: a.limit or None]
    out = []
    for r in rows:
        d0 = os.path.dirname(os.path.dirname(r["path"]))
        stem = os.path.basename(r["path"])[:-4]
        base = "R2w" if r["rung"] == "S3" else "R2w4"
        P = pool[r["p1"]]
        S = cv2.imread(r["path"]).astype(np.float64)
        C = cv2.imread(f"{d0}/{base}/{stem}.png").astype(np.float64)
        m = ARS.hull(P["H"][:-4] + ".tem", P["B"][:-4] + ".tem", S.shape)
        assert np.abs(S - C)[~m].max() == 0
        d = S - C
        dm = d[m]                                            # (n, 3)
        mu = dm.mean(0)
        D_dc = float(np.abs(mu).mean())
        D_ac = float(np.abs(dm - mu).mean())
        res = []
        for ch in range(3):
            x, y = C[..., ch][m], S[..., ch][m]
            A = np.c_[x, np.ones_like(x)]
            coef, *_ = np.linalg.lstsq(A, y, rcond=None)
            res.append(np.abs(y - A @ coef))
        D_lin = float(np.mean(np.concatenate(res)))
        mx = m[:, :-1] & m[:, 1:]
        my = m[:-1, :] & m[1:, :]
        gx = np.abs(d[:, 1:] - d[:, :-1])[mx].mean()
        gy = np.abs(d[1:, :] - d[:-1, :])[my].mean()
        out.append(dict(id=r["id"], rung=r["rung"], role=ev[r["id"]]["role"], host=r["p1"],
                        D_dc=D_dc, D_ac=D_ac, D_lin=D_lin, D_grad=float(gx + gy)))
    tag = f"d_feats_limit{a.limit}" if a.limit else "d_feats"
    f = OUT / f"{tag}.csv"
    if f.exists():
        sys.exit(f"{f} exists; refusing to overwrite")
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / f"{tag}.csv.sha256").write_text(f"{h}  {f.name}\n")
    print("rows", len(out), "sha256", h)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

"""Texture band profile, two people against one (TB1): band statistics in memory (lead's ruling 13 Nov: FFT band
statistics computed in memory are measurements like the hand-made statistics, AS0 precedent; no filtered image is
stored). Bands: AS0's octave bands B1..B5 (`src/AS0/as0_measure.band_weights`, imported unchanged), nominal IOD of the
ar1_512 frame (AS0 `iod_nominal.json`, median 130.51 px), luminance Y = 0.299 R + 0.587 G + 0.114 B.
- P (oracle half-difference): d = Y(S) - Y(counterpart) for S4 (counterpart R2w4) and S3 (counterpart R2w); since a
  splice equals its counterpart outside the amendment-7b hull and equals the 50% morph inside, d = 0.5 (Y(X_w) - Y(H_w))
  inside the hull. E_k = sum over the hull of b_k(d)^2; p_k = E_k / sum_k E_k.
- S (single image): for S4, S3, S0, R2w4 (hull = amendment-7b hull, mean(H, B)) and R0, R0_61 (hull of H's own .tem):
  e_in,k = mean over the hull of b_k(Y)^2, e_out,k = the same over an outer ring of at least the hull's area (3 x 3
  dilations of the hull until the ring area >= the hull area); r_k = ln(e_in,k / e_out,k).
Amendment 1 (pre-run T2, T3): d is centred by its hull mean before the FFT; P energies also over the hull eroded by
16 px; S r_k also with a 16 px guard band either side of the hull edge (inside: hull eroded 16 px; ring of equal
area outside the hull dilated 16 px); R2w is measured on the amendment-7b hull too (warp-magnitude control).
Out: /mnt/t7/smad_next/TB1/tb1_feats.csv (+ .sha256).   python3 -I tb1_measure.py [--limit 6]"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AS0")
import as0_measure as AM  # noqa: E402
sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import splice as ARS  # noqa: E402

MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
EVAL = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
IOD = json.load(open("/mnt/t7/smad_next/AS0/iod_nominal.json"))["ar1_512"]["median"]
OUT = pathlib.Path("/mnt/t7/smad_next/TB1")


def Y(p):
    import cv2
    x = cv2.imread(str(p)).astype(np.float64)
    return 0.114 * x[..., 0] + 0.587 * x[..., 1] + 0.299 * x[..., 2]


def bands(y):
    import scipy.fft as sf
    h, w = y.shape
    Hs = AM.band_weights(h, w, IOD)
    F = sf.rfft2(y, workers=1)
    return [sf.irfft2(F * Hs[k], s=(h, w), workers=1) for k in range(1, 6)]


def erode(m, px):
    import cv2
    return cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=px).astype(bool)


def dilate(m, px):
    import cv2
    return cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=px).astype(bool)


def ring_of(m, base=None):
    """ring outside base (default m) of at least m's area"""
    import cv2
    k = np.ones((3, 3), np.uint8)
    base = m if base is None else base
    d = base.astype(np.uint8)
    for _ in range(400):
        d = cv2.dilate(d, k)
        r = d.astype(bool) & ~base
        if r.sum() >= m.sum():
            return r
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    man = [r for r in csv.DictReader(open(MAN)) if r["role"] in ("dev", "test")]
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    want = {("splice", "S4", ""), ("splice", "S3", ""), ("splice", "S0", ""), ("ladder", "R2w4", ""), ("ladder", "R2w", ""),
            ("ladder", "R0", ""), ("ladder", "R0", "61")}
    by = {}
    for r in man:
        key = (r["fam"], r["rung"], r["strength"])
        if key in want and (r["fam"] == "splice" or r["tool"] in ("opencv", "none")):
            by.setdefault(r["host"], {})[f"{r['rung']}{'_' + r['strength'] if r['strength'] else ''}"] = r
    hosts = sorted(h for h, d in by.items() if all(k in d for k in ("S4", "S3", "S0", "R2w4", "R2w", "R0", "R0_61")))
    hosts = hosts[: a.limit or None]
    out = []
    for h in hosts:
        P, d = pool[h], by[h]
        m7 = ARS.hull(P["H"][:-4] + ".tem", P["B"][:-4] + ".tem", (512, 512))
        mH = ARS.hull(P["H"][:-4] + ".tem", P["H"][:-4] + ".tem", (512, 512))
        rec = dict(host=h, db=P["db"], role=d["S4"]["role"])
        m7e = erode(m7, 16)
        for name, img, cp in (("P4", "S4", "R2w4"), ("P3", "S3", "R2w")):
            diff = Y(EVAL / d[img]["path"]) - Y(EVAL / d[cp]["path"])
            assert np.abs(diff[~m7]).max() == 0, (h, img)
            diff[m7] -= diff[m7].mean()                       # amendment 1 (T3): hull-mean centring
            bb = bands(diff)
            E = np.array([float((b[m7] ** 2).sum()) for b in bb])
            Ee = np.array([float((b[m7e] ** 2).sum()) for b in bb])
            for k in range(5):
                rec[f"{name}_p{k + 1}"] = float(E[k] / E.sum())
                rec[f"{name}_pe{k + 1}"] = float(Ee[k] / Ee.sum())
            rec[f"{name}_Etot"] = float(E.sum())
        for name in ("S4", "S3", "S0", "R2w4", "R2w", "R0", "R0_61"):
            m = mH if name.startswith("R0") else m7
            rg = ring_of(m)
            mi = erode(m, 16)
            rgg = ring_of(m, dilate(m, 16))
            b = bands(Y(EVAL / d[name]["path"]))
            for k in range(5):
                rec[f"{name}_r{k + 1}"] = float(np.log((b[k][m] ** 2).mean() / (b[k][rg] ** 2).mean()))
                rec[f"{name}_rg{k + 1}"] = float(np.log((b[k][mi] ** 2).mean() / (b[k][rgg] ** 2).mean()))
            rec[f"{name}_id"] = d[name]["id"]
        out.append(rec)
    tag = f"tb1_feats_limit{a.limit}" if a.limit else "tb1_feats"
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

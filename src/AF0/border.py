"""Wave 3, control 5: border (out-of-coverage) blanking, one rerun of the main contrasts.
Out-of-coverage = pixels where a warped source is exactly black (all three channels 0; the aligned source frames carry
black borders that the warp moves into the frame). The same region is blanked with constant grey (128, 128, 128) in
both classes before feature extraction (constant-colour blanking is an approved operation; nothing else changes).
  AF0 validation: each uniform-0.5 morph and its two halves; region = black in halfA OR black in halfB.
  AR1 primary pool, OpenCV-style engine: R4 (H, B) and R2w (H warped to the mean of H, S); region = black in the
  engine's own warped H or warped B of R4 (af_morph.warped_pair, the unchanged engine) OR black in R2w.
Writes OUT/img/border/<id>.png and the list lists/border.csv (feat.py format, geometry of the source row).
  python3 -I border.py --workers 2
"""
import argparse
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

GREY = 128


def blank(path, mask, out):
    import cv2
    im = cv2.imread(path)
    im[mask] = GREY
    out.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(out), im)


def job_af0(t):
    import cv2
    cv2.setNumThreads(1)
    m, ha, hb = t
    A, B = cv2.imread(ha["path"]), cv2.imread(hb["path"])
    mask = (A.max(-1) == 0) | (B.max(-1) == 0)
    rows = []
    for r in (m, ha, hb):
        o = L.OUT / "img" / "border" / f"{r['id']}.png"
        if not o.exists():
            blank(r["path"], mask, o)
        rows.append(dict(r, id="bd_" + r["id"], path=str(o), set="border"))
    return rows, float(mask.mean())


def job_ar1(t):
    import cv2
    cv2.setNumThreads(1)
    import af_morph as AM
    r4, r2w, pool = t
    H, Bm = cv2.imread(pool["H"]), cv2.imread(pool["B"])
    wA, wB, _, _ = AM.warped_pair(H, AM.parse_tem(pool["H"][:-4] + ".tem"), Bm, AM.parse_tem(pool["B"][:-4] + ".tem"))
    W2 = cv2.imread(r2w["path"])
    mask = (np.clip(wA, 0, 255).astype(np.uint8).max(-1) == 0) | (np.clip(wB, 0, 255).astype(np.uint8).max(-1) == 0) | (W2.max(-1) == 0)
    rows = []
    for r in (r4, r2w):
        o = L.OUT / "img" / "border" / f"{r['id']}.png"
        if not o.exists():
            blank(r["path"], mask, o)
        rows.append(dict(r, id="bd_" + r["id"], path=str(o), set="border"))
    return rows, float(mask.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    vc = L.rows("valcmp")
    byid = {r["id"]: r for r in vc}
    t_af0 = [(r, byid[r["id"] + "_halfA"], byid[r["id"] + "_halfB"]) for r in vc
             if r["rung"] == "u50" and r["id"] + "_halfA" in byid and r["id"] + "_halfB" in byid]
    ar1 = [r for r in L.rows("ar1") if r["cell"] == "frgcferet" and r["tool"] == "opencv"]
    pool = {r["pid"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv"))}
    r4 = {r["p1"]: r for r in ar1 if r["rung"] == "R4"}
    r2w = {r["p1"]: r for r in ar1 if r["rung"] == "R2w"}
    t_ar1 = [(r4[h], r2w[h], pool[h]) for h in sorted(r4) if h in r2w]
    from multiprocessing import Pool
    rows, fr_af0, fr_ar1 = [], [], []
    with Pool(a.workers) as p:
        for rr, f in p.imap(job_af0, t_af0, chunksize=4):
            rows += rr
            fr_af0.append(f)
        for rr, f in p.imap(job_ar1, t_ar1, chunksize=4):
            rows += rr
            fr_ar1.append(f)
    with open(L.OUT / "lists" / "border.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("border list", len(rows), "AF0 triples", len(t_af0), "mean blanked fraction", round(float(np.mean(fr_af0)), 4),
          "AR1 pairs", len(t_ar1), "mean blanked fraction", round(float(np.mean(fr_ar1)), 4))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

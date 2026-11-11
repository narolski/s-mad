"""Own-crop re-score of the audit rows (RS1), amendment 2 (d): black-border check of each release's own crop.
For every crop a release receives, the fraction of pixels whose three channels are exactly 0, summarised per set:
mean fraction, share of crops with any such pixel, share with more than 1%, maximum.
  MTCNN crops (MADation, MixFaceNet-MAD): the reused A46 crops and the RS1 crops (lists/score.csv).
  SelfMAD own crop: its saved raw-file crops in /mnt/t7/smad_heldout/a41g/x7/a41g_x7/ (A41 x7 manifest).
  For reference, the same statistic on the uncropped inputs our aligner produced (aligned frames) where they exist.
  python3 -I border.py  -> experiments/RS1_own-crop-rescore/rs1_border.csv
"""
import collections
import csv
import pathlib

import cv2
import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
X7 = pathlib.Path("/mnt/t7/smad_heldout/a41g/x7")
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")


def zero_frac(p):
    im = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if im is None:
        return np.nan
    return float((im.max(axis=2) == 0).mean())


def summarise(tag, by):
    rows = []
    for s, v in sorted(by.items()):
        v = np.array([x for x in v if np.isfinite(x)])
        rows.append(dict(crop=tag, set=s, n=len(v), mean_black_frac=round(float(v.mean()), 5),
                         share_any_black=round(float((v > 0).mean()), 4), share_over_1pct=round(float((v > 0.01).mean()), 4),
                         max_black_frac=round(float(v.max()), 4)))
    return rows


def main():
    import sys
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    cut = (lambda L: L[:lim]) if lim else (lambda L: L)
    man = {r["id"]: r for r in csv.DictReader(open(OUT / "manifest.csv"))}
    by = collections.defaultdict(list)
    for r in cut(list(csv.DictReader(open(OUT / "lists/score.csv")))):
        by[man[r["id"]]["set"]].append(zero_frac(r["path"]))
    rows = summarise("MTCNN crop (MADation, MixFaceNet-MAD)", by)
    by = collections.defaultdict(list)
    for r in cut(list(csv.DictReader(open(X7 / "manifests/a41g_x7.csv")))):
        by[r["family"]].append(zero_frac(X7 / r["path"]))
    rows += summarise("SelfMAD crop of raw files (A41 x7)", by)
    by = collections.defaultdict(list)                     # our aligned frames themselves (inputs, not crops)
    for r in cut([r for r in csv.DictReader(open(DATA / "manifests/eval.csv"))
                  if r["set"] in ("frllm", "mordiff") and r["variant"] in ("orig", "resmatch")]):
        if True:
            by[f"{r['set']}/{r['family']}/{r['variant']}"].append(zero_frac(DATA / r["path"]))
    rows += summarise("our aligned 512 frame (input, uncropped)", by)
    with open(RES / ("rs1_border.csv" if not lim else "rs1_border_smoke.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()

"""D5 measurement: border fraction of existing aligned genuine frames (read only; no image is written or changed).

border_frac = share of exactly-black pixels of the 512 frame, the TT1 definition (src/TT1/align.py,
prep_ffhqm.border_frac): (img.max(2) == 0).mean(). Frames:
  MS1 FFHQ     /mnt/t7/smad_next/MS1/ffhq/src/*.png          (persons.csv)
  CelebA-HQ    /mnt/t7/smad_next/MS1/celebahq/frames/*.png    (persons.csv, kept persons only: dropped == 0)
  AR1 sources  /mnt/t7/smad_next/AR1/src/<db>/<subject>/*.png (FRGC / colorFERET, ladder_split roles)
  AF0 sources  /mnt/t7/smad_next/AF0/src/<db>/<subject>/*.png (af0_split roles)
Val-reserved persons (is_val = 1 in the PN1 split files; never valx.csv) are left out.
The source eye distance (ied_src) is NOT in any existing record for these frames (73_delin_align logs no scale);
it is written as empty.

  python -I d5_measure_border.py [--limit 8]  -> /mnt/t7/smad_next/DATA/D5/frames_measured.csv
"""
import argparse
import csv
import hashlib
import pathlib
from multiprocessing import Pool

import cv2

T7 = pathlib.Path("/mnt/t7/smad_next")
SPL = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
OUT = T7 / "DATA/D5"


def items():
    out = []
    for r in csv.DictReader(open(T7 / "MS1/ffhq/persons.csv")):
        out.append(dict(source="ms1_ffhq", person=r["pid"], role=r["part"], path=r["frame"]))
    for r in csv.DictReader(open(T7 / "MS1/celebahq/persons.csv")):
        if r["dropped"] == "0":
            out.append(dict(source="celebahq", person=r["person"], role="training_source",
                            path=str(T7 / "MS1/celebahq/frames" / f"{r['index']}.png")))
    lad = {r["pid"]: r for r in csv.DictReader(open(SPL / "ladder_split.csv"))}
    af = {r["pid"]: r for r in csv.DictReader(open(SPL / "af0_split.csv"))}
    for name, tab, rk in (("ar1", lad, "role"), ("af0", af, "pn1_use")):
        for p in sorted((T7 / name.upper() / "src").glob("*/*/*.png")):
            pid = f"{p.parent.parent.name}:{p.parent.name}"
            r = tab.get(pid)
            if r is None or r["is_val"] != "0":
                continue
            out.append(dict(source=name, person=pid, role=r[rk], path=str(p)))
    return out


def measure(it):
    img = cv2.imread(it["path"])
    if img is None:
        return dict(it, border_frac="", ied_src="", h="", w="", note="unreadable")
    return dict(it, border_frac=round(float((img.max(2) == 0).mean()), 6), ied_src="", h=img.shape[0], w=img.shape[1],
                note="")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    its = items()
    if a.limit:
        its = its[: a.limit]
    with Pool(a.workers) as pool:
        res = pool.map(measure, its, chunksize=64)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ("frames_measured.csv" if not a.limit else "frames_measured_test8.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print(p, len(res), hashlib.sha256(p.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()

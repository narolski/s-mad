"""Diffusion-autoencoder generation on Athena (DG1): merge per-shard manifests written by dg1_validity.py manifest
(each with image paths relative to its own shard folder) into one manifest whose image paths are relative to the common
generation root (/mnt/t7/smad_next/DG1/gen), checking that no (pool, image name) appears twice.

usage: python -I dg1_merge_manifests.py --out CSV  <validity_dir>:<prefix> [<validity_dir>:<prefix> ...]
  e.g. /mnt/t7/smad_next/DG1/validity/setB_s0:setB_s0
"""
import argparse
import csv
import pathlib
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("parts", nargs="+")
    a = ap.parse_args()
    rows, seen, cols = [], set(), None
    for part in a.parts:
        d, pre = part.split(":", 1)
        for r in csv.DictReader(open(pathlib.Path(d) / "manifest.csv")):
            cols = cols or list(r)
            key = (r["pool"], pathlib.PurePosixPath(r["image"]).name)
            if key in seen:
                sys.exit(f"{key} appears twice")
            seen.add(key)
            r["image"] = f"{pre}/{r['image']}"
            rows.append(r)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows from {len(a.parts)} parts -> {a.out}")


if __name__ == "__main__":
    main()

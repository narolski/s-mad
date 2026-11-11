"""Simple-statistics floor (wave 3, control 1; CN0 part b): the 26 cue_floor statistics (smadcvpr/cue_floor.stats,
imported unchanged; Laplacian variance of the whole frame = 'lapvar', of the canonical face box = 'lapvar_face') plus
PNG byte size, for every image of the named lists; cached per list as OUT/cues/<list>.npz.
  python3 -I cues_all.py ar1 bench_s h1 af0_w1 af0_h --workers 2
"""
import argparse
import os
import pathlib
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")


def one(p):
    import cv2
    import cue_floor as CF
    cv2.setNumThreads(1)
    return np.r_[CF.stats(cv2.imread(p)[:, :, ::-1]), os.path.getsize(p)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lists", nargs="+")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    import cue_floor as CF
    from multiprocessing import Pool
    for n in a.lists:
        out = L.OUT / "cues" / f"{n}.npz"
        if out.exists():
            continue
        R = L.rows(n)
        with Pool(a.workers) as p:
            C = np.stack(p.map(one, [r["path"] for r in R], chunksize=8))
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(out, ids=np.array([r["id"] for r in R]), cues=C, names=np.array(list(CF.NAMES) + ["png_bytes"]))
        print(n, C.shape, flush=True)


if __name__ == "__main__":
    main()

"""PD1 landmark: simple-statistic floor inputs. The 26 cue_floor statistics (smadcvpr/cue_floor.stats, imported
unchanged; RGB 512 x 512 frame as stored) plus PNG file size, per image. Values already computed by the alpha-field
probe (AF0, OUT/cues/<list>.npz, same function, same order of names) are copied by id; only missing ids are computed.

  python3 -I cues.py ar1 [--only-rung R2wm] [--limit 8] [--workers 2]
-> OUT/cues/<list>[_<rung>].npz (ids, cues (n, 27), names, source = 'af0' | 'pd1')
"""
import argparse
import os
import pathlib
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402

sys.path.insert(0, str(K.MC / "smadcvpr"))


def one(p):
    import cv2
    import cue_floor as CF
    cv2.setNumThreads(1)
    return np.r_[CF.stats(cv2.imread(p)[:, :, ::-1]), os.path.getsize(p)]


def af0_cache():
    have = {}
    d = K.AF0 / "cues"
    for f in d.glob("*.npz"):
        if "smoke" in f.name:
            continue
        z = np.load(f)
        for i, c in zip(z["ids"], z["cues"]):
            have[str(i)] = c
    return have


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("list")
    ap.add_argument("--only-rung", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    import cue_floor as CF
    from multiprocessing import Pool
    rr = K.rows(K.OUT / "lists" / f"{a.list}.csv")
    if a.only_rung:
        rr = [r for r in rr if r["rung"] in a.only_rung.split(",")]
    rr = rr[: a.limit or None]
    tag = a.list + (f"_{a.only_rung.replace(',', '-')}" if a.only_rung else "") + (f"_limit{a.limit}" if a.limit else "")
    have = af0_cache()
    todo = [r["path"] for r in rr if r["id"] not in have]
    with Pool(a.workers) as p:
        new = dict(zip(todo, p.map(one, todo, chunksize=8))) if todo else {}
    C = np.stack([have[r["id"]] if r["id"] in have else new[r["path"]] for r in rr])
    src = np.array(["af0" if r["id"] in have else "pd1" for r in rr])
    out = K.OUT / "cues" / f"{tag}.npz"
    np.savez(out, ids=np.array([r["id"] for r in rr]), cues=C, names=np.array(list(CF.NAMES) + ["png_bytes"]),
             source=src)
    print(tag, C.shape, "from af0:", int((src == "af0").sum()), "computed:", len(todo), flush=True)


if __name__ == "__main__":
    main()

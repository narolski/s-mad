"""RZ1 CPU reads, printed only (prereg section 12, M3 and m1). No score is read; no image is written.
  floors : the 26 cue_floor statistics + PNG bytes (the 27 statistics of AB1's floor, via AF0's cues_all path: cue_floor
           .stats on a 512 x 512 RGB array) of the FFHQ landmark_combined rows (1,000 morphs, 2,000 resmatch genuine),
           computed on what each arm's input carries:
             pil_bilinear / pil_nearest: the stored frame resized to 224 with that kernel (rz1_kernels.Transform),
             crop: the 224 interior window (crop:144:160);
           each 224 image is enlarged back to 512 with PIL BILINEAR only so that the 512-frame statistics apply (the
           enlargement adds no information). PNG bytes = the stored file's size (unchanged).
           Out: /mnt/t7/smad_next/RZ1/floors/floor_<tag>.npz (ids, cues, names), the AF0 format.
  hull   : the share of each splice hull (AR1 splice.hull, imported unchanged; R4 geometry = mean of H and B .tem, as
           BD1) that lies inside the interior window x 144-367, y 160-383; for the OpenCV splice_nat rows of training and
           development hosts (the test ladder is not used). Out: /mnt/t7/smad_next/RZ1/floors/hull_coverage.json.
  python3 -I rz1_cpu.py floors|hull [--limit 8]"""
import argparse
import csv
import json
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = pathlib.Path("/mnt/t7/smad_next/RZ1/floors")
DATA = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data")
X_EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv")
X0, Y0, S = 144, 160, 224


def _one(args):
    path, tag = args
    import cv2
    from PIL import Image
    import rz1_kernels as K
    sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
    import cue_floor as CF
    cv2.setNumThreads(1)
    im = Image.open(DATA / path).convert("RGB")
    spec = {"pil_bilinear": "fixed:pil_bilinear", "pil_nearest": "fixed:pil_nearest", "crop": f"crop:{X0}:{Y0}"}[tag]
    small = K.Transform(spec, S)(im)
    big = np.asarray(small.resize((512, 512), Image.BILINEAR))
    return np.r_[CF.stats(big), os.path.getsize(DATA / path)]


def floors(limit):
    from multiprocessing import Pool
    sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
    import cue_floor as CF
    M = [r for r in csv.DictReader(open(X_EVAL)) if r["fam"] == "ffhq_lcomb"]
    assert len(M) == 3000
    M = M[: limit or None]
    OUT.mkdir(parents=True, exist_ok=True)
    for tag in ("pil_bilinear", "pil_nearest", "crop"):
        f = OUT / (f"floor_{tag}" + (f"_limit{limit}" if limit else "") + ".npz")
        if f.exists():
            print("exists", f)
            continue
        with Pool(2) as p:
            C = np.stack(p.map(_one, [(r["path"], tag) for r in M], chunksize=16))
        np.savez(f, ids=np.array([r["id"] for r in M]), cues=C, names=np.array(list(CF.NAMES) + ["png_bytes"]))
        print("DONE", tag, C.shape, flush=True)


def hull(limit):
    import cv2
    sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
    import splice as ARS
    sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
    import pn1lib as PL
    lad, _ = PL.split_tables()
    pool = {r["pid"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv"))}
    rows = [r for r in csv.DictReader(open("/mnt/t7/smad_next/PN1/lists/splice_nat.csv"))
            if r["tool"] == "opencv" and r["rung"] == "S4" and lad.get(r["p1"], {}).get("role") in ("train", "dev")]
    rows = rows[: limit or None]
    cov = {"train": [], "dev": []}
    for r in rows:
        P = pool[r["p1"]]
        m = ARS.hull(P["H"][:-4] + ".tem", P["B"][:-4] + ".tem", (512, 512, 3))
        cov[lad[r["p1"]]["role"]].append(float(m[Y0:Y0 + S, X0:X0 + S].sum() / m.sum()))
    res = {k: dict(n=len(v), mean=float(np.mean(v)), q=[float(x) for x in np.percentile(v, [0, 10, 25, 50, 75, 90, 100])])
           for k, v in cov.items() if v}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("hull_coverage" + (f"_limit{limit}" if limit else "") + ".json")).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("floors", "hull"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    floors(a.limit) if a.what == "floors" else hull(a.limit)

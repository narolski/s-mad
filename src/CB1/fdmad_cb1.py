"""CB1: re-score the A45 FD-MAD re-implementation (global branch) on the CB1 image list.

Imports a45_fdmad.py unchanged (job-root copy /mnt/t7/smad_next/CB1/code_a45_jobroot/smadcvpr/a45_fdmad.py, sha256
aa41b5a1..., identical to /home/narolski/mambamorph-code-a45/smadcvpr/a45_fdmad.py) and repeats its train-score step
exactly (same SMDD rows of train.csv, same subsample draw rng([20261107, 45, seed]), same featurize / Global classes and
the registered loader), then scores every row of the CB1 image list instead of eval.csv. The gate rows and FRLL-Morphs
rows of the list are eval.csv rows, so the stored A45 scores (/mnt/t7/smad_heldout/a45/fdmad/fdmad_global_r<res>_s<seed>/
scores_eval.npz) must be reproduced on them (check C1-F).
  python3 -I fdmad_cb1.py --images IMAGES.csv --res 256 --seed 1 --out OUT.npz [--workers 2]
"""
import argparse
import csv
import hashlib
import pathlib
import sys

import numpy as np

JR = pathlib.Path("/mnt/t7/smad_next/CB1/code_a45_jobroot/smadcvpr")
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--res", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--smoke", action="store_true", help="50 + 50 training rows, 8 list rows")
    a = ap.parse_args()
    sys.path.insert(0, str(JR))
    import a45_fdmad as F
    assert hashlib.sha256(pathlib.Path(F.__file__).read_bytes()).hexdigest().startswith("aa41b5a1")
    tr, tr_sha = F.manifest_rows(DATA, "train.csv")
    assert tr_sha == F.REG["train.csv"], tr_sha
    smdd = [r for r in tr if r["source"] == "smdd" and r.get("val", "0") == "0"]
    rng = np.random.default_rng([20261107, 45, a.seed])
    n = 50 if a.smoke else F.N_PER_CLASS
    b = [r for r in smdd if r["label"] == "0"]
    m = [r for r in smdd if r["label"] == "1"]
    pick = [b[i] for i in sorted(rng.choice(len(b), n, replace=False))] + \
           [m[i] for i in sorted(rng.choice(len(m), n, replace=False))]
    items = [(str(DATA / r["path"]), int(r["label"])) for r in pick]
    y = np.array([1 - int(r["label"]) for r in pick])
    G, _ = F.featurize(items, a.res, a.workers, None, "train")
    g = F.Global(a.seed).fit(G, y)
    rows = list(csv.DictReader(open(a.images)))
    rows = rows[:8] if a.smoke else rows
    eitems = [(r["path"], int(r["label"])) for r in rows]
    Ge, _ = F.featurize(eitems, a.res, a.workers, None, "cb1")
    s = g.p_bona(Ge)
    np.savez(a.out, id=np.array([r["id"] for r in rows]), score=(1.0 - s).astype(np.float64), s_global=s,
             res=a.res, seed=a.seed, script_sha256=hashlib.sha256(pathlib.Path(F.__file__).read_bytes()).hexdigest(),
             train_paths_sha256=hashlib.sha256("\n".join(r["path"] for r in pick).encode()).hexdigest(),
             images_sha256=hashlib.sha256(pathlib.Path(a.images).read_bytes()).hexdigest())
    print("WRITTEN", a.out, len(rows))


if __name__ == "__main__":
    main()

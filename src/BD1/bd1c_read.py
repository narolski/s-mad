"""BD1 amendment 4: descriptive read of the least- and most-similar same-person splices (cos_HS quintiles), per block.
Printed only. Development data only.   python -I bd1c_read.py --out bd1c_read.json"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bd1_read import BLOCKS, auc, sha  # noqa: E402

MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
FF = pathlib.Path("/mnt/t7/smad_next/BD1/d_feats.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    for f in (DF, FF):
        assert sha(f) == pathlib.Path(str(f) + ".sha256").read_text().split()[0]
    man = {r["id"]: r for r in csv.DictReader(open(MAN)) if r["fam"] == "splice" and r["role"] in ("dev", "test")}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    for r in csv.DictReader(open(FF)):
        D[r["id"]].update(r)
    S3 = sorted([i for i, r in man.items() if r["rung"] == "S3"])
    S4 = sorted([i for i, r in man.items() if r["rung"] == "S4"])
    cos = np.array([float(pool[man[i]["host"]]["cos_HS"]) for i in S3])
    lo, hi = np.quantile(cos, [0.2, 0.8])
    Q = {"bottom": [i for i, c in zip(S3, cos) if c <= lo], "top": [i for i, c in zip(S3, cos) if c >= hi]}
    out = dict(edges=[float(lo), float(hi)], n={k: len(v) for k, v in Q.items()},
               db={k: {d: sum(1 for i in v if pool[man[i]["host"]]["db"] == d) for d in ("frgc", "feret")} for k, v in Q.items()},
               med={k: {x: float(np.median([float(D[i][x]) for i in v])) for x in ("D", "D_dc", "D_lin")} for k, v in Q.items()},
               blocks={})
    for blk, nets in BLOCKS.items():
        res = {}
        for path, name, arm, s in nets:
            if arm != "Sb":
                continue
            assert sha(path) == pathlib.Path(path + ".sha256").read_text().split()[0]
            with tarfile.open(path) as tf:
                z = np.load(io.BytesIO(tf.extractfile(f"{name}/scores_eval.npz").read()))
            L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            p4 = np.array([L[i] for i in S4])
            res[f"Sb_s{s}"] = {k: dict(flag=float(np.mean([L[i] > 0 for i in v])), auc_S4_vs_this=auc(p4, np.array([L[i] for i in v])))
                               for k, v in Q.items()}
        out["blocks"][blk] = res
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("edges", "n", "db", "med")}))
    for blk, res in out["blocks"].items():
        for k, r in res.items():
            print(blk, k, {q: {m: round(x, 3) for m, x in v.items()} for q, v in r.items()})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

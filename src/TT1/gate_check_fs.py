"""TT1 FS1 block: platform gate per network (draft prereg_fs1_block_draft.md). numpy only.
Gate rows: every row of the FS1 development evaluation manifest pn1_eval.csv (19,797 rows, sha256 f0f29f22...), scored
in the manifest order, batch 64, TF32 on (as pn1_score.py did for the stored scores_eval.npz of each fit), with
rescore.py's model build. Criterion per network: byte identity (float32) of the logit on every row against the stored
scores_eval.npz logit. A network that fails is not scored on TT1 rows.
  python gate_check_fs.py --scores DIR --nets DIR --out gate.json   (DIR/<net>__fsgate.npz; nets/<net>/scores_eval.npz)"""
import argparse
import json
import pathlib
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = dict(rule="byte identity on all FS1 eval rows (TF32 on, batch 64, manifest order)", nets={})
    for d in sorted(pathlib.Path(a.nets).iterdir()):
        n = d.name
        f = pathlib.Path(a.scores) / f"{n}__fsgate.npz"
        if not f.exists():
            res["nets"][n] = dict(ok=False, why="no gate scores")
            continue
        z0, z1 = np.load(d / "scores_eval.npz"), np.load(f)
        m1 = dict(zip(z1["id"].tolist(), z1["logit"].astype(np.float32).tolist()))
        ids = z0["id"].tolist()
        if set(ids) != set(m1):
            res["nets"][n] = dict(ok=False, why="row sets differ")
            continue
        s0 = z0["logit"].astype(np.float32)
        s1 = np.array([m1[i] for i in ids], np.float32)
        dd = np.abs(s1.astype(np.float64) - s0.astype(np.float64))
        res["nets"][n] = dict(n=len(ids), max_abs=float(dd.max()), n_differ=int((dd > 0).sum()),
                              flips=int(((s0 > 0) != (s1 > 0)).sum()), ok=bool(dd.max() == 0))
    res["passed"] = [n for n, v in res["nets"].items() if v["ok"]]
    res["failed"] = [n for n, v in res["nets"].items() if not v["ok"]]
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print("FSGATE passed", len(res["passed"]), "failed", res["failed"])
    sys.exit(0)


if __name__ == "__main__":
    main()

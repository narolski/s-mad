"""PR1 GD reproduction gate per network (prereg.md section 6; the C2P gate criterion). numpy only.
Rows: all 19,797 FS1 development evaluation rows, re-scored on pn1fs in manifest order, batch 64, TF32 on, against the
network's stored scores_eval.npz. Pass: 99th percentile |dlogit| <= 0.05 AND max |dlogit| <= 0.10 AND own-rule
decisions agree on >= 99.5% of rows. Byte identity printed.
  python gate_gd.py --scores DIR --nets DIR --out gate.json [--test]"""
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
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    res = dict(rule="p99|d|<=0.05 and max|d|<=0.10 and own-rule agreement>=0.995 on all FS1 eval rows (TF32 on)",
               test=a.test, nets={})
    for d in sorted(pathlib.Path(a.nets).iterdir()):
        n = d.name
        f = pathlib.Path(a.scores) / f"{n}__gate.npz"
        if not f.exists():
            res["nets"][n] = dict(ok=False, why="no gate scores")
            continue
        z0, z1 = np.load(d / "scores_eval.npz"), np.load(f)
        m0 = dict(zip(z0["id"].tolist(), z0["logit"].astype(np.float32).tolist()))
        ids = z1["id"].tolist()
        if (not a.test and set(ids) != set(m0)) or not set(ids) <= set(m0):
            res["nets"][n] = dict(ok=False, why="row sets differ")
            continue
        s0 = np.array([m0[i] for i in ids], np.float32)
        s1 = z1["logit"].astype(np.float32)
        if not np.isfinite(s1).all():
            res["nets"][n] = dict(ok=False, why="non-finite")
            continue
        dd = np.abs(s1.astype(np.float64) - s0.astype(np.float64))
        agree = float(((s0 > 0) == (s1 > 0)).mean())
        ok = bool(np.percentile(dd, 99) <= 0.05 and dd.max() <= 0.10 and agree >= 0.995)
        res["nets"][n] = dict(n=len(ids), p99_abs=float(np.percentile(dd, 99)), max_abs=float(dd.max()),
                              n_differ=int((dd > 0).sum()), byte_identical=bool(dd.max() == 0), agree=agree,
                              flips=int(((s0 > 0) != (s1 > 0)).sum()), ok=ok)
    res["passed"] = [n for n, v in res["nets"].items() if v["ok"]]
    res["failed"] = [n for n, v in res["nets"].items() if not v["ok"]]
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print("GDGATE passed", len(res["passed"]), "failed", res["failed"],
          "byte_identical", sum(1 for v in res["nets"].values() if v.get("byte_identical")))
    sys.exit(0)


if __name__ == "__main__":
    main()

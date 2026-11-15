"""Threshold transfer on unseen genuine sources (TT1): platform equivalence gate (registered rule; numpy only).
For every network: new logits of the 3,417 gate rows (R_cam 417, R_ffhq 2,000, M_ffhq 1,000) against the stored A100
logits (gate_ref/<task>.npz). PASS for a network iff all of (registration TT1-S section 4, G-DGX tolerances):
  max |dlogit| <= 0.02 over the 3,417 rows;
  zero own-rule decision (logit > 0) changes;
  |AUC(R_ffhq vs R_cam) new - stored| <= 0.002 (mid-ranks);
  Kendall tau-b(new, stored) on R_cam (417) >= 0.99.
The gate passes iff every network passes. Exit 0 on pass, 2 on fail (the caller then scores no TT1 row).
  python gate_check.py --scores DIR --ref DIR --manifest tt1_score.csv --out gate.json"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

TOL = dict(max_abs=0.02, max_flips=0, d_auc=0.002, kendall_cam=0.99)


def kendall_b(x, y):
    """Kendall tau-b, O(n^2) (n = 417)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    dx = np.sign(x[:, None] - x[None, :])
    dy = np.sign(y[:, None] - y[None, :])
    iu = np.triu_indices(len(x), 1)
    dx, dy = dx[iu], dy[iu]
    num = float((dx * dy).sum())
    den = np.sqrt(float((dx != 0).sum()) * float((dy != 0).sum()))
    return num / den if den else float("nan")


def auc(pos, neg):
    x = np.concatenate([pos, neg])
    r = np.empty(len(x))
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    i = 0
    while i < len(x):                       # average ranks for ties
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    n1, n0 = len(pos), len(neg)
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pool = {r["id"]: r["rung"] for r in csv.DictReader(open(a.manifest)) if r["fam"] == "gate"}
    res, ok_all = dict(tolerance=TOL, nets={}), True
    refs = sorted(pathlib.Path(a.ref).glob("*.npz"))
    assert refs, "no gate references"
    for rf in refs:
        task = rf.stem
        z0 = np.load(rf)
        sf = pathlib.Path(a.scores) / f"{task}__gate.npz"
        if not sf.exists():
            res["nets"][task] = dict(ok=False, why="no new scores")
            ok_all = False
            continue
        z1 = np.load(sf)
        m1 = dict(zip(z1["id"].tolist(), z1["logit"].tolist()))
        ids = z0["id"].tolist()
        assert set(ids) == set(pool) and set(m1) == set(pool), task
        s0 = z0["logit"].astype(np.float64)
        s1 = np.array([m1[i] for i in ids], np.float64)
        d = np.abs(s1 - s0)
        flip = (s0 > 0) != (s1 > 0)
        pl = np.array([pool[i] for i in ids])
        a0 = auc(s0[pl == "R_ffhq"], s0[pl == "R_cam"])
        a1 = auc(s1[pl == "R_ffhq"], s1[pl == "R_cam"])
        kc = kendall_b(s1[pl == "R_cam"], s0[pl == "R_cam"])
        r = dict(n=len(ids), max_abs=float(d.max()), median_abs=float(np.median(d)), flips=int(flip.sum()),
                 flips_max_abs_stored=float(np.abs(s0[flip]).max()) if flip.any() else 0.0,
                 auc_ffhq_cam_stored=a0, auc_ffhq_cam_new=a1, d_auc=abs(a1 - a0), kendall_cam=kc)
        r["ok"] = bool(r["max_abs"] <= TOL["max_abs"] and r["flips"] <= TOL["max_flips"]
                       and r["d_auc"] <= TOL["d_auc"] and kc >= TOL["kendall_cam"])
        ok_all &= r["ok"]
        res["nets"][task] = r
    res["pass"] = bool(ok_all)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print("GATE", "PASS" if ok_all else "FAIL", json.dumps({k: v.get("ok") for k, v in res["nets"].items()}))
    sys.exit(0 if ok_all else 2)


if __name__ == "__main__":
    main()

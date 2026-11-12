"""Threshold transfer on unseen genuine sources (TT1): platform gate of deviation TT1-D1 (rented A100, the stack of the
stored scores). numpy only. For each of the 12 networks, new logits of the 3,417 gate rows against the stored logits:
  FFHQ rows (R_ffhq 2,000 + M_ffhq 1,000; stored by the same script rescore.py on A100s): byte identity required,
      max |dlogit| == 0 (float32 equality);
  R_cam rows (417; stored by pn1_score.py, which enables TF32 and scores the whole evaluation manifest in other
      batches, so bit identity is not expected): max |dlogit| <= 0.02, zero own-rule decision changes, Kendall tau-b
      >= 0.99;
  |AUC(R_ffhq vs R_cam) new - stored| <= 0.002 (mid-ranks).
The gate passes iff every network passes. Exit 0 on pass, 2 on fail.
  python gate_check_a100.py --scores DIR --ref DIR --manifest tt1_score.csv --out gate.json"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

TOL = dict(ffhq_max_abs=0.0, cam_max_abs=0.02, cam_flips=0, cam_kendall=0.99, d_auc=0.002)


def kendall_b(x, y):
    dx = np.sign(x[:, None] - x[None, :])
    dy = np.sign(y[:, None] - y[None, :])
    iu = np.triu_indices(len(x), 1)
    dx, dy = dx[iu], dy[iu]
    den = np.sqrt(float((dx != 0).sum()) * float((dy != 0).sum()))
    return float((dx * dy).sum()) / den if den else float("nan")


def auc(pos, neg):
    neg = np.sort(neg)
    lo = np.searchsorted(neg, pos, "left")
    hi = np.searchsorted(neg, pos, "right")
    return float((lo + 0.5 * (hi - lo)).sum() / (len(pos) * len(neg)))


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
    assert len(refs) == 12, len(refs)
    for rf in refs:
        task = rf.stem
        sf = pathlib.Path(a.scores) / f"{task}__gate.npz"
        if not sf.exists():
            res["nets"][task] = dict(ok=False, why="no new scores")
            ok_all = False
            continue
        z0, z1 = np.load(rf), np.load(sf)
        m1 = dict(zip(z1["id"].tolist(), z1["logit"].astype(np.float32).tolist()))
        ids = z0["id"].tolist()
        assert set(ids) == set(pool) == set(m1), task
        s0 = z0["logit"].astype(np.float32)
        s1 = np.array([m1[i] for i in ids], np.float32)
        pl = np.array([pool[i] for i in ids])
        fq = (pl == "R_ffhq") | (pl == "M_ffhq")
        cam = pl == "R_cam"
        d = np.abs(s1.astype(np.float64) - s0.astype(np.float64))
        r = dict(ffhq_n=int(fq.sum()), ffhq_max_abs=float(d[fq].max()), ffhq_n_differ=int((d[fq] > 0).sum()),
                 cam_n=int(cam.sum()), cam_max_abs=float(d[cam].max()), cam_median_abs=float(np.median(d[cam])),
                 cam_flips=int(((s0[cam] > 0) != (s1[cam] > 0)).sum()),
                 cam_kendall=kendall_b(s1[cam].astype(float), s0[cam].astype(float)),
                 auc_ffhq_cam_stored=auc(s0[pl == "R_ffhq"], s0[cam]), auc_ffhq_cam_new=auc(s1[pl == "R_ffhq"], s1[cam]))
        r["d_auc"] = abs(r["auc_ffhq_cam_new"] - r["auc_ffhq_cam_stored"])
        r["ok"] = bool(r["ffhq_max_abs"] <= TOL["ffhq_max_abs"] and r["cam_max_abs"] <= TOL["cam_max_abs"]
                       and r["cam_flips"] <= TOL["cam_flips"] and r["cam_kendall"] >= TOL["cam_kendall"]
                       and r["d_auc"] <= TOL["d_auc"])
        ok_all &= r["ok"]
        res["nets"][task] = r
    res["pass"] = bool(ok_all)
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print("GATE", "PASS" if ok_all else "FAIL", json.dumps({k: v.get("ok") for k, v in res["nets"].items()}))
    sys.exit(0 if ok_all else 2)


if __name__ == "__main__":
    main()

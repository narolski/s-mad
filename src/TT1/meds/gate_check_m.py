"""TT1 MEDS extension gate (per network): the 3,417 TT1 fam-gate rows scored on the new host by rescore.py unchanged
(PyTorch defaults, batch 64, tt1_score.csv order) against the same rows scored on pn1fs (gate_ref/<net>.npz): byte
identity (float32) required. A failing network is not scored on MEDS rows. numpy only.
  python gate_check_m.py --scores DIR --ref DIR --out gate.json"""
import argparse, json, pathlib, sys
import numpy as np
ap = argparse.ArgumentParser(); ap.add_argument("--scores", required=True); ap.add_argument("--ref", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
res = dict(rule="byte identity on the 3,417 TT1 fam-gate rows against pn1fs", nets={})
for rf in sorted(pathlib.Path(a.ref).glob("*.npz")):
    n = rf.stem; f = pathlib.Path(a.scores) / f"{n}__gate.npz"
    if not f.exists():
        res["nets"][n] = dict(ok=False, why="no scores"); continue
    z0, z1 = np.load(rf), np.load(f)
    if z0["id"].tolist() != z1["id"].tolist():
        res["nets"][n] = dict(ok=False, why="row order differs"); continue
    d = np.abs(z1["logit"].astype(np.float64) - z0["logit"].astype(np.float64))
    res["nets"][n] = dict(n=len(d), max_abs=float(d.max()), n_differ=int((d > 0).sum()),
                          flips=int(((z0["logit"] > 0) != (z1["logit"] > 0)).sum()), ok=bool(d.max() == 0))
res["passed"] = [n for n, v in res["nets"].items() if v["ok"]]; res["failed"] = [n for n, v in res["nets"].items() if not v["ok"]]
pathlib.Path(a.out).write_text(json.dumps(res, indent=1)); print("MGATE passed", len(res["passed"]), "failed", res["failed"]); sys.exit(0)

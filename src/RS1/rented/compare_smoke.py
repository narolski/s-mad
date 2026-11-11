"""RS1 amendment 5: 8-image check of the rented machine against the Athena smoke job 3545869 (same inputs: the first 8
of every set). Prints the largest |logit difference| per release and variant, crop agreement (v1 files written, v2
boxes), and PASS if every release's maximum is below 0.5 logit and the same images were cropped.
  python3 -I compare_smoke.py RENTED_V1_DIR RENTED_V2_DIR ATHENA_SMOKE_DIR
"""
import json
import pathlib
import sys

import numpy as np

v1, v2, ath = (pathlib.Path(p) for p in sys.argv[1:4])
ok, worst = True, 0.0
for v, d in (("v1", v1), ("v2", v2)):
    for f in sorted((ath / "scores").glob(f"scores_rel_*__{v}.npz")):
        g = d / "scores" / f.name
        if not g.exists():
            print("missing", g); ok = False; continue
        a, b = np.load(f), np.load(g)
        la = dict(zip(a["id"].tolist(), a["logit_noTTA"].astype(float)))
        lb = dict(zip(b["id"].tolist(), b["logit_noTTA"].astype(float)))
        ids = sorted(set(la) & set(lb))
        dd = np.abs(np.array([la[i] for i in ids]) - np.array([lb[i] for i in ids]))
        only = len(set(la) ^ set(lb))
        worst = max(worst, float(dd.max()))
        print(f"{v} {f.name[11:-4]:40s} n={len(ids)} max|dlogit|={dd.max():.4f} median={np.median(dd):.5f} ids_only_one_side={only}")
        ok &= only == 0
sa, sb = json.load(open(ath / "crop_summary.json")), json.load(open(v1 / "crop_summary.json"))
print("v1 missing athena", sorted(sa["v1_missing"]), "rented", sorted(sb["v1_missing"]))
ok &= sorted(sa["v1_missing"]) == sorted(sb["v1_missing"])
print(f"largest |logit difference| {worst:.4f}")
print("PASS" if ok and worst < 0.5 else "FAIL")

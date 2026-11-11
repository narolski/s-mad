"""C1c: draw the eye-label sample (40 FERET + 20 FRGC probe-clear pairs, seed 20261111) and write a BLIND list
(pair id and frame paths only; no probe values) for labelling by eye.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1c/c1c_eye_sample.py
"""
import csv, pathlib
import numpy as np
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1c_smiling-half-expression-or-detail")
rng = np.random.default_rng(20261111)
rows = []
for name, k in (("feret", 40), ("frgc", 20)):
    L = [o for o in csv.DictReader(open(OUT / f"c1c_{name}_pairs.csv")) if o["probe_clear"] == "1"]
    for i in sorted(rng.choice(len(L), k, replace=False)):
        o = L[i]
        rows.append({"pool": o["pool"], "pair": o["pair"], "path_a": o["path_a"], "path_b": o["path_b"]})
with open(OUT / "c1c_eye_sample_blind.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["pool"], r["pair"], r["path_a"].rsplit("/", 1)[1], r["path_b"].rsplit("/", 1)[1])

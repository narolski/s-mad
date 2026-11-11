"""Wave 3, control 1 on AF0's own validation images: uniform-0.5 morph against its own two warped halves (and against
zero-field images and unprocessed photos), every head's AUC beside the Laplacian-variance floor and the best simple
statistic (cue_floor's 26 + PNG bytes, folded). Validation persons only; person bootstrap.
  python3 -I wave3_floor.py cues          (list 'valcmp' + its cue statistics)
  python3 -I wave3_floor.py read --specs dinov3_512:full,clip224:full,clip224:w2_alpha,clip224:w2_g,...
"""
import argparse
import csv
import json
import pathlib
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import metrics as M  # noqa: E402

LISTS = ("af0_w1", "af0_w2", "af0_h")


def make(a):
    rows = []
    for n in LISTS:
        for r in L.rows(n):
            if r["cell"] != "val":
                continue
            if r["rung"] in ("u50", "zero", "photo") or (r["rung"] in ("halfA", "halfB") and "_u50_" in r["id"]):
                rows.append(r)
    with open(L.OUT / "lists" / "valcmp.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("valcmp", len(rows))
    subprocess.run(["/home/narolski/mambamorph-code/.venv-spark/bin/python", "-I", "cues_all.py", "valcmp", "--workers", "1"],
                   check=True, cwd=str(pathlib.Path(__file__).resolve().parent))


def read(a):
    M._ROWS["valcmp"] = {r["id"]: r for r in L.rows("valcmp")}
    out = {}
    for spec in a.specs.split(","):
        bb, tag = spec.split(":")
        d = L.OUT / "heads" / bb / tag
        heads = sorted({p.name[5:].split("_af0_")[0] for p in d.glob("pred_*_af0_w1.npz")})
        for h in heads:
            S = {}
            for n in LISTS:
                P = M.load(bb, tag, h, n)
                if P:
                    S.update(P[0])
            if not S:
                continue
            r = {}
            for name, neg in (("u50_vs_own_halves", ("halfA", "halfB")), ("u50_vs_zero_field", ("zero",)),
                              ("u50_vs_photo", ("photo",))):
                r[name] = M.contrast(S, "valcmp", lambda x: x["rung"] == "u50", lambda x, neg=neg: x["rung"] in neg)
            out[f"{bb}/{tag}/{h}"] = r
            c = r["u50_vs_own_halves"]
            print(bb, tag, h, c and (c["auc"], c.get("lapvar_floor"), c.get("best_simple"), c.get("best_simple_auc")), flush=True)
    json.dump(out, open(L.RES / "wave3_floor_valcmp.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("cues", "read"))
    ap.add_argument("--specs", default="dinov3_512:full,clip224:full")
    a = ap.parse_args()
    make(a) if a.cmd == "cues" else read(a)

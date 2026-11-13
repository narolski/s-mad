"""Sealed MAD22 read (FINAL): platform gate. For every network of final_config.json: the gate rows (final_gate.csv,
whole 64-row batches of the FS1 evaluation manifest, manifest order, batch 64, TF32 on) scored on the read's host
against the same rows of the network's stored fit-time scores_eval.npz. Criterion: byte identity (float32) on every
row, every network. Prints only counts and maxima (no score). Exit 0 = all pass, 3 = any network fails or is missing.
  python gate_check_final.py --config CFG --manifest final_gate.csv --scores DIR --nets DIR --out gate.json"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    for k in ("config", "manifest", "scores", "nets", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    want = [r["id"] for r in csv.DictReader(open(a.manifest))]
    res = dict(rule=cfg["gate"]["criterion"], n_rows=len(want), nets={})
    for n in (x["name"] for x in cfg["networks"]):
        f = pathlib.Path(a.scores) / f"{n}__gate.npz"
        ref = pathlib.Path(a.nets) / n / "scores_eval.npz"
        if not f.exists() or not ref.exists():
            res["nets"][n] = dict(ok=False, why="missing gate or reference scores")
            continue
        z1, z0 = np.load(f), np.load(ref)
        ids1 = z1["id"].tolist()
        if ids1 != want:
            res["nets"][n] = dict(ok=False, why="gate rows differ from the gate manifest (order or set)")
            continue
        if "manifest_sha256" in z0.files and str(z0["manifest_sha256"]) != cfg["gate"]["source_manifest_sha256"]:
            res["nets"][n] = dict(ok=False, why="stored scores were made on another development manifest")
            continue
        m0 = dict(zip(z0["id"].tolist(), z0["logit"].astype(np.float32).tolist()))
        if any(i not in m0 for i in want):
            res["nets"][n] = dict(ok=False, why="gate row missing in the stored scores")
            continue
        s0 = np.array([m0[i] for i in want], np.float32)
        s1 = z1["logit"].astype(np.float32)
        d = np.abs(s1.astype(np.float64) - s0.astype(np.float64))
        res["nets"][n] = dict(n=len(d), max_abs=float(d.max()), n_differ=int((d > 0).sum()),
                              flips=int(((s0 > 0) != (s1 > 0)).sum()), ok=bool((s0.tobytes() == s1.tobytes())))
    res["passed"] = [n for n, v in res["nets"].items() if v["ok"]]
    res["failed"] = [n for n, v in res["nets"].items() if not v["ok"]]
    res["all_pass"] = not res["failed"] and len(res["passed"]) == len(cfg["networks"])
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print("FINALGATE passed", len(res["passed"]), "of", len(cfg["networks"]), "failed", res["failed"],
          "max_abs", max([v.get("max_abs", -1) for v in res["nets"].values()] + [-1]))
    sys.exit(0 if res["all_pass"] else 3)


if __name__ == "__main__":
    main()

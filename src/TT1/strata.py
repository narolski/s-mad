"""Threshold transfer on unseen genuine sources (TT1): fixed strata edges for the scoring registration, computed from
the manifests only (no score exists). Aligned images (aligned=1) only.
  lap_var quintile edges per verification pack (lfw, calfw, cfp_ff, agedb_30) and over the four anti-spoofing sets pooled;
  enlargement quintile edges over all aligned images; border_frac quintile edges over all aligned images.
Edges: numpy.quantile(x, [0, .2, .4, .6, .8, 1]) (linear); stratum k = [edge k, edge k+1), the last closed.
  python3 -I strata.py  -> experiments/TT1_.../strata_edges.json"""
import csv
import hashlib
import json
import pathlib

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/TT1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine")
Q = [0, .2, .4, .6, .8, 1]


def main():
    raw = {r["id"]: r for r in csv.DictReader(open(OUT / "raw_manifest.csv"))}
    rows = [{**raw[a["id"]], **a} for a in csv.DictReader(open(OUT / "aligned_manifest.csv")) if a["aligned"] == "1"]
    out = dict(raw_manifest_sha256=hashlib.sha256((OUT / "raw_manifest.csv").read_bytes()).hexdigest(),
               aligned_manifest_sha256=hashlib.sha256((OUT / "aligned_manifest.csv").read_bytes()).hexdigest(),
               quantiles=Q, lap_var={}, n={})
    groups = {s: [r for r in rows if r["source"] == s] for s in ("lfw", "calfw", "cfp_ff", "agedb_30")}
    groups["antispoof_pooled"] = [r for r in rows if r["source"] in ("replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd")]
    for g, rs in groups.items():
        out["lap_var"][g] = [float(x) for x in np.quantile([float(r["lap_var"]) for r in rs], Q)]
        out["n"][g] = len(rs)
    out["enlarge_all"] = [float(x) for x in np.quantile([float(r["enlarge"]) for r in rows], Q)]
    out["border_frac_all"] = [float(x) for x in np.quantile([float(r["border_frac"]) for r in rows], Q)]
    out["n"]["all_aligned"] = len(rows)
    (RES / "strata_edges.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

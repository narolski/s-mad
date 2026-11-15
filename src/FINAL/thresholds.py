"""Sealed MAD22 read (FINAL): the development threshold of every detector, fixed BEFORE the read from development
scores only (no benchmark score exists or is read here).
Rule (EV1): t = the smallest score value c with share(FFHQ genuine score > c) <= alpha, alpha = 0.05.
- Our networks: the stored fit-time scores (scores_eval.npz in each network tar, TF32 on) of the 2,000 FFHQ genuine
  development photos (pn1_eval.csv fam ffhq, rung ffhq_bona_orig); FFHQ was never a training source of these networks.
- Released detectors: their existing RS1 scores of the same FFHQ photos on their own crop path (FF_orig; variant 1
  primary, variant 2 printed), SelfMAD from RS1's DGX own-preprocessing run.
Out: experiments/FINAL_sealed-benchmark-read/final_thresholds.json
  python3 -I thresholds.py"""
import csv
import hashlib
import io
import json
import pathlib
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.load(open(HERE / "final_config.json"))
OUT = pathlib.Path("/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/final_thresholds.json")
REL = pathlib.Path("/mnt/t7/smad_next/FINAL/release_scores_existing.npz")


def thr(s, alpha):
    s = np.asarray(s, np.float64)
    for c in np.unique(s):
        if (s > c).mean() <= alpha:
            return float(c), float((s > c).mean())
    raise AssertionError


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    q = CFG["ffhq_threshold_rows"]
    G = CFG["gate"]
    man = pathlib.Path(G["source_tree"]) / G["source_manifest"]
    assert sha(man) == G["source_manifest_sha256"]
    ids = [r["id"] for r in csv.DictReader(open(man)) if r["fam"] == q["fam"] and r["rung"] == q["rung"] and r["label"] == q["label"]]
    out = dict(rule="smallest c with share(FFHQ genuine > c) <= alpha", alpha=q["alpha"], n_ffhq_rows=len(ids), nets={}, releases={})
    for n in CFG["networks"]:
        assert sha(n["tar"]) == n["sha256"]
        with tarfile.open(n["tar"]) as t:
            z = np.load(io.BytesIO(t.extractfile(f"{n['name']}/scores_eval.npz").read()))
        m = dict(zip(z["id"].tolist(), z["logit"].astype(np.float32).tolist()))
        s = [m[i] for i in ids]
        c, sh = thr(s, q["alpha"])
        out["nets"][n["name"]] = dict(tau_ffhq=c, share_above=sh, n=len(s))
    r = np.load(REL)
    assert sha(REL) == (REL.parent / (REL.name + ".sha256")).read_text().split()[0]
    out["release_scores_sha256"] = sha(REL)
    for det in sorted(set(r["det"].tolist())):
        for v in sorted(set(r["variant"][r["det"] == det].tolist())):
            k = (r["det"] == det) & (r["variant"] == v) & (r["pool"] == "FF_orig")
            c, sh = thr(r["logit"][k], q["alpha"])
            out["releases"][f"{det}/{v}"] = dict(tau_ffhq=c, share_above=sh, n=int(k.sum()))
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

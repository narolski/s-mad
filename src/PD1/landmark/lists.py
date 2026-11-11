"""PD1 landmark: image lists (read-only sources; nothing is built or copied).

  ar1   : landmark ladder (AR1) rungs R0, R2w, R2wm, R3m, R3, R4 of both engines, primary pool and FRLL pool
          (ids = 'ar1_' + AR1 manifest id, the ids of AF0's feature caches)
  ar1g  : AR1 graded FaceMorpher set (300 hosts x m = 0 ... 0.5)
  af0   : AF0 images photo / zero / u25 / u50 (OpenCV-style engine, persons disjoint from AR1)
  smdd  : 1,500 SMDD bona fide renders and their existing a47e7 stored-small copies (seed 20261111; 1,000 fit, 500 test)
  bench : AF0's benchmark subsample list bench_s (FRLL-Morphs and corrected MAD22 landmark cells, genuine native, E7)
  h1    : AF0's list of the approved Poisson set (orig variant)

  python3 -I lists.py
"""
import collections
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402

COLS = ["id", "path", "set", "pool", "tool", "rung", "p1", "p2", "level", "split"]


def row(**kw):
    return {c: kw.get(c, "") for c in COLS}


def main():
    out = {}
    m = K.rows(K.AR1 / "manifest.csv") + K.rows(K.AR1 / "manifest_extra.csv")
    out["ar1"] = [row(id="ar1_" + r["id"], path=r["path"], set="ar1", pool=r["pool"], tool=r["tool"], rung=r["rung"],
                      p1=r["p1"], p2=r["p2"]) for r in m
                  if r["pool"] in ("frgcferet", "frll") and r["rung"] in K.RUNGS]
    out["ar1g"] = [row(id="ar1_" + r["id"], path=r["path"], set="ar1g", pool=r["pool"], tool=r["tool"], rung="G",
                       p1=r["p1"], p2=r["p2"], level=r["level"]) for r in m if r["pool"] == "frgcferet" and r["rung"] == "G"]
    out["af0"] = [row(id=r["id"], path=r["path"], set="af0", pool=r["tool"], tool="opencv", rung=r["rung"], p1=r["p1"],
                      p2=r["p2"], split=r["cell"]) for r in K.rows(K.AF0 / "lists/af0.csv")
                  if r["rung"] in ("photo", "zero", "u25", "u50")]
    sm = [r for r in K.rows(K.A47 / "manifests/train.csv")]
    bona = [r["path"] for r in sm if r["label"] == "0"]
    copy = {r["path"].replace("train/smdd_a47e7/", "train/smdd/") for r in sm if r["label"] == "1"}
    bona = sorted(p for p in bona if p in copy)
    sel = np.random.default_rng(K.SEED).choice(len(bona), 1500, replace=False)
    sr = []
    for j, i in enumerate(sel):
        rel = bona[i]
        stem = pathlib.Path(rel).stem
        split = "fit" if j < 1000 else "test"
        sr.append(row(id=f"smdd_render_{stem}", path=str(K.SMDD_ROOT / rel), set="smdd", pool="smdd", tool="smdd",
                      rung="render", p1="smdd:" + stem, p2="smdd:" + stem, split=split))
        sr.append(row(id=f"smdd_small_{stem}", path=str(K.A47 / rel.replace("train/smdd/", "train/smdd_a47e7/")),
                      set="smdd", pool="smdd", tool="smdd", rung="small", p1="smdd:" + stem, p2="smdd:" + stem,
                      split=split))
    out["smdd"] = sr
    out["bench"] = [row(id=r["id"], path=r["path"], set="bench", pool=r["cell"], tool=r["tool"], rung=r["rung"],
                        p1=r["p1"], p2=r["p2"]) for r in K.rows(K.AF0 / "lists/bench_s.csv")]
    out["h1"] = [row(id=r["id"], path=r["path"], set="h1", pool="h1poisson", tool="poisson", rung=r["rung"],
                     p1=r["p1"], p2=r["p2"]) for r in K.rows(K.AF0 / "lists/h1.csv")]
    summ = {}
    for n, rr in out.items():
        for r in rr:
            assert not K.forbidden(r["path"]), r["path"]
            assert pathlib.Path(r["path"]).exists(), r["path"]
        ids = [r["id"] for r in rr]
        dup = len(ids) - len(set(ids))
        if dup:                       # AF0's h1 list repeats some genuine ids (a genuine photo per pair); keep first
            seen, keep = set(), []
            for r in rr:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    keep.append(r)
            rr = out[n] = keep
        K.write_rows(K.OUT / "lists" / f"{n}.csv", rr)
        summ[n] = dict(n=len(rr), duplicates_dropped=dup,
                       cells={"|".join(k): v for k, v in sorted(collections.Counter(
                           (r["pool"], r["tool"], r["rung"], r["split"]) for r in rr).items())})
    # FRLL persons must never be fitted: record which lists contain them
    summ["frll_persons_in_lists"] = {n: sum(r["p1"].startswith("frll:") for r in rr) for n, rr in out.items()}
    json.dump(summ, open(K.RES / "lists_summary.json", "w"), indent=1)
    print(json.dumps({n: v["n"] for n, v in summ.items() if isinstance(v, dict) and "n" in v}))


if __name__ == "__main__":
    main()

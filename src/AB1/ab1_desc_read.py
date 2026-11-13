"""AB1 amendment 6 (post hoc, zero GPU, DESCRIPTIVE ONLY, no verdict): three reads on existing fit-job scores.
Networks: A, B, Sb, Sp at seeds 408-412 (AB1 H100 tars, ab1_read.load) and A, B, Sb at 403-407 plus Sp at 403-405 (FS1 A100
tars, ab1_pm2_read.load_fs1). Host set: 100 development hosts + 80 clean test hosts (as amendment 4), split into the two
parts. D = BD1's d_values (S4 splice D for R4/S4 rows, S3 splice D for R3/S3 rows; pinned).
  1. D cue: Spearman(logit, log D) within the pooled S4 + S3 rows and within the pooled R4 + R3 rows (OpenCV), and within
     each class separately, per network.
  2. Breakdown of the development versus clean-host difference: unstratified R4-vs-R3 (OpenCV) AUC per network and the
     paired differences Sb - B, Sb - Sp, Sp - B, in cells part (dev, clean80) x database (frgc, feret) and part x D tercile
     (tercile edges of log D over the pooled R4 + R3 rows of both parts); a cell with < 20 rows of either class prints None.
  Run with /home/narolski/mambamorph-code/.venv-spark/bin/python -I (numpy only; no scipy needed).
  3. Own-rule (logit > 0) flag rates on R3 (OpenCV, FaceMorpher), R4 (OpenCV, FaceMorpher), S3, S0, S4 per part.
  python3 -I ab1_desc_read.py --out OUT.json
  python3 -I ab1_desc_read.py --mock --out MOCK.json"""
import argparse
import csv
import importlib.util
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P2 = _mod("ab1_pm2_read", HERE / "ab1_pm2_read.py")
PM, A, C2, K = P2.PM, P2.A, P2.C2, P2.K
P2_SHA = "77ace4b3e98668adbb842b8a5aebac23c2bb19f0f8486911807bce9291395b1d"


def _rank(v):
    v = np.asarray(v, float)
    o = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    """Spearman with average ranks for ties (numpy only; amendment 6b A6-1)."""
    return float(np.corrcoef(_rank(x), _rank(y))[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_pm2_read.py") == P2_SHA
    lad, _ = K.split_tables()
    dev = sorted(h for h, x in lad.items() if x["role"] == "dev")
    clean = sorted(r["host"] for r in csv.DictReader(open(PM.CLEAN)))
    assert len(dev) == 100 and len(clean) == 80
    D = {(r["rung"], r["host"]): float(r["D"]) for r in csv.DictReader(open(PM.DVAL))}
    rows = {}
    for r in csv.DictReader(open(A.EVAL)):
        if r["strength"] != "":
            continue
        if r["fam"] == "ladder" and r["rung"] in ("R4", "R3") and r["tool"] in ("opencv", "facemorpher"):
            rows[(r["rung"], r["tool"], r["host"])] = r["id"]
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3", "S0"):
            rows[(r["rung"], "opencv", r["host"])] = r["id"]
    nets = {}
    if a.mock:
        r0 = np.random.default_rng(5)
        for arm in ("A", "B", "Sb", "Sp"):
            for s in (408, 409, 410, 411, 412, 403, 404, 405, 406, 407):
                nets[(arm, s)] = {i: float(r0.normal()) for i in rows.values()}
    for arm in ("A", "B", "Sb", "Sp") if not a.mock else ():
        for s in (408, 409, 410, 411, 412):
            x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)
            assert x is not None, (arm, s, why)
            nets[(arm, s)] = x
        for s in (403, 404, 405, 406, 407):
            if arm == "Sp" and s > 405:
                continue
            x, why = P2.load_fs1(arm, s)
            assert x is not None, (arm, s, why)
            nets[(arm, s)] = x
    parts = {"dev": dev, "clean80": clean}
    db = lambda h: h.split(":")[0]
    ld_all = np.log([D[("S4" if rk == "R4" else "S3", h)] for (rk, tool, h) in rows if rk in ("R4", "R3") and tool == "opencv"
                     and h in set(dev + clean) and ("S4" if rk == "R4" else "S3", h) in D])
    terc = np.quantile(ld_all, [1 / 3, 2 / 3])
    tof = lambda v: int(np.searchsorted(terc, np.log(v), side="right"))
    out = dict(networks=sorted(f"{k[0]}_s{k[1]}" for k in nets), d_cue={}, breakdown={}, flags={})
    for (arm, s), x in nets.items():
        key = f"{arm}_s{s}"
        hs = dev + clean
        rec = {}
        for name, (pr, nr, tool) in (("S4S3", ("S4", "S3", "opencv")), ("R4R3", ("R4", "R3", "opencv"))):
            pl = [(x[rows[(pr, tool, h)]], D[("S4", h)]) for h in hs if (pr, tool, h) in rows and ("S4", h) in D]
            nl = [(x[rows[(nr, tool, h)]], D[("S3", h)]) for h in hs if (nr, tool, h) in rows and ("S3", h) in D]
            allp = pl + nl
            rec[name] = dict(pooled_includes_class_separation=spearman([v for v, _ in allp], np.log([d for _, d in allp])),
                             positive_class=spearman([v for v, _ in pl], np.log([d for _, d in pl])),
                             negative_class=spearman([v for v, _ in nl], np.log([d for _, d in nl])))
        out["d_cue"][key] = rec
        fl = {}
        for pname, ph in parts.items():
            for rk, tool in (("R3", "opencv"), ("R3", "facemorpher"), ("R4", "opencv"), ("R4", "facemorpher"),
                             ("S3", "opencv"), ("S0", "opencv"), ("S4", "opencv")):
                v = [x[rows[(rk, tool, h)]] > 0 for h in ph if (rk, tool, h) in rows]
                fl[f"{pname}|{rk}_{tool}"] = float(np.mean(v)) if v else None
        out["flags"][key] = fl
    # breakdown cells
    def cell_auc(x, hosts):
        p = [x[rows[("R4", "opencv", h)]] for h in hosts if ("R4", "opencv", h) in rows]
        n = [x[rows[("R3", "opencv", h)]] for h in hosts if ("R3", "opencv", h) in rows]
        return (C2.fauc(p, n), len(p), len(n)) if len(p) >= 20 and len(n) >= 20 else (None, len(p), len(n))
    cells = {}
    for pname, ph in parts.items():
        for d in ("frgc", "feret"):
            cells[f"{pname}|db={d}"] = [h for h in ph if db(h) == d]
        for t in range(3):
            # a host enters the tercile of its own R4 row's D for positives and of its R3 row's D for negatives: done per row below
            cells[f"{pname}|Dtercile={t}"] = (ph, t)
    for cname, spec in cells.items():
        res = {}
        for (arm, s), x in nets.items():
            if isinstance(spec, tuple):
                ph, t = spec
                p = [x[rows[("R4", "opencv", h)]] for h in ph if ("R4", "opencv", h) in rows and ("S4", h) in D and tof(D[("S4", h)]) == t]
                n = [x[rows[("R3", "opencv", h)]] for h in ph if ("R3", "opencv", h) in rows and ("S3", h) in D and tof(D[("S3", h)]) == t]
                auc = (C2.fauc(p, n) if len(p) >= 20 and len(n) >= 20 else None, len(p), len(n))
            else:
                auc = cell_auc(x, spec)
            res[f"{arm}_s{s}"] = dict(auc=auc[0], n_pos=auc[1], n_neg=auc[2])
        diffs = {}
        for f, o in (("Sb", "B"), ("Sb", "Sp"), ("Sp", "B")):
            for block, ss in (("408-412", (408, 409, 410, 411, 412)), ("403-407", (403, 404, 405, 406, 407))):
                vals = [res[f"{f}_s{s}"]["auc"] - res[f"{o}_s{s}"]["auc"] for s in ss
                        if f"{f}_s{s}" in res and f"{o}_s{s}" in res and res[f"{f}_s{s}"]["auc"] is not None and res[f"{o}_s{s}"]["auc"] is not None]
                diffs[f"{f}-{o}|{block}"] = dict(per_seed=vals, mean=float(np.mean(vals)) if vals else None,
                                                 seed_sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else None, n_seeds=len(vals))
        out["breakdown"][cname] = dict(per_network=res, paired=diffs)
    out["d_tercile_edges_logD"] = terc.tolist()
    out["label"] = ("descriptive, post hoc, no verdict, no direction tested; development plus clean test hosts; not held-out. "
                    "Pooled Spearman includes class separation: read the within-class values only. Cells with fewer than 20 rows "
                    "of either class print None; cells under about 30 rows per class are noise-dominated (seed SD printed). "
                    "Sp at 403-405: 3 seeds, A100 PCIe, pack 76528f16; Sb - Sp and Sp - B means in the 403-407 block are over these 3 seeds only.")
    json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print("written", a.out, len(out["networks"]), "networks")


if __name__ == "__main__":
    main()

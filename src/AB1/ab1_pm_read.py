"""AB1 amendment 4 (post hoc): Sb - B and Sb - A at seeds 408-412 on pipeline-matched contrasts (AB1 H100 fit-job scores,
provenance-checked by ab1_read.load). Development data only.

Host set (primary): the 100 development-ladder hosts + the 80 test hosts clean of development persons
(/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv, sha256 pinned below). Printed beside: the 191 read test
hosts and the 159 of them that are not shape-linked (the 32 test hosts that are pool partners of training hosts, derived
from the PN1 ladder split: training host with partner_B a read test host).
Contrasts (OpenCV-style engine decides):
  primary    R4 vs R3 (two-person against same-person whole-frame morph), D-stratified AUC
  secondary  S4 vs S3 (face splices), D-stratified AUC, on the same host set; printed on development hosts alone
  printed    FaceMorpher R4 vs R3; unstratified AUCs
D-stratified AUC (BD1's primary statistic, unchanged): D = BD1's blend-difference energy of the host's S4 (for R4 and S4
rows) or S3 (for R3 and S3 rows) splice (/mnt/t7/smad_next/BD1/d_values.csv, pinned); quintile edges of log D over the
pooled rows of the contrast; AUC within each stratum; mean weighted by n_pos x n_neg over strata with >= 10 rows of each
class; readable if those strata hold >= 50% of the rows (else the seed counts as not readable).
Rule per contrast (fixed before any score is opened): paired gain g_s = stat(Sb_s) - stat(X_s), X in {B, A}. Joint
person-component bootstrap (components of the host-partner graph within the host set; 2,000 draws, rng 20261120; the
same draws for all networks and seeds) of the seed-mean gain. "present" if seed-mean >= +0.03 AND lower 95% bound > 0
AND g_s > 0 on >= 4 of 5 seeds; "absent" if the upper 95% bound < +0.03; otherwise "inconclusive". Fewer than 4 readable
seeds: "not read".
Printed: the adversary's floors (src/adversary/check.exceeds, all-cue and nuisance) for ri_R4_vs_R3, ri_S4_vs_S3,
dev_S4_vs_S3, test_cv_R4_vs_R3, test_fm_R4_vs_R3, test_S4_vs_S3 per network; the same-data transfer learner per arm if
--learner is given (committed file).
  python3 -I ab1_pm_read.py --out OUT.json [--learner F --learner-sha H]
  python3 -I ab1_pm_read.py --mock --out MOCK.json"""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ab1_read", HERE / "ab1_read.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
C2 = A.C2
sys.path.insert(0, str(HERE.parent / "PN1"))
sys.path.insert(0, str(HERE.parent / "adversary"))
import pn1lib as K  # noqa: E402

AB1_READ_SHA = "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"
CLEAN = pathlib.Path("/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv")
DVAL = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
SEEDS = A.SEEDS
ADV_CONTRASTS = ("ri_R4_vs_R3", "ri_S4_vs_S3", "dev_S4_vs_S3", "test_cv_R4_vs_R3", "test_fm_R4_vs_R3", "test_S4_vs_S3")


def strat_auc(pos_s, pos_d, neg_s, neg_d):
    """BD1 primary statistic: D-quintile AUC, weighted by n_pos*n_neg over strata with >= 10 of each class."""
    ld = np.log(np.concatenate([pos_d, neg_d]))
    edges = np.quantile(ld, [0.2, 0.4, 0.6, 0.8])
    qp = np.searchsorted(edges, np.log(pos_d), side="right")
    qn = np.searchsorted(edges, np.log(neg_d), side="right")
    num = den = 0.0
    used = 0
    for k in range(5):
        a, b = pos_s[qp == k], neg_s[qn == k]
        if len(a) >= 10 and len(b) >= 10:
            w = len(a) * len(b)
            num += w * C2.fauc(a, b)
            den += w
            used += len(a) + len(b)
    if den == 0 or used < 0.5 * (len(pos_s) + len(neg_s)):
        return None
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--learner"); ap.add_argument("--learner-sha")
    ap.add_argument("--clean-sha", default="814c44861d706553bd827e5dd5634817ee289c0b12bc45a553c5d759b8362358")
    ap.add_argument("--dval-sha", default="cf2ba3fa87f434f72d195a6c6e96df6ad9b99ee0b7f887ff44625b9712177725")
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA
    sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    if a.clean_sha:
        assert sha(CLEAN) == a.clean_sha
    if a.dval_sha:
        assert sha(DVAL) == a.dval_sha
    lad, _ = K.split_tables()
    dev = sorted(h for h, x in lad.items() if x["role"] == "dev")
    test = sorted(h for h, x in lad.items() if x["role"] == "test" and x["test_read"] == "1")
    clean = sorted(r["host"] for r in csv.DictReader(open(CLEAN)))
    assert len(dev) == 100 and len(test) == 191 and len(clean) == 80 and set(clean) <= set(test)
    linked = sorted({lad[h]["partner_B"] for h, x in lad.items() if x["role"] == "train" and lad[h]["partner_B"] in set(test)})
    assert len(linked) == 32
    test159 = sorted(set(test) - set(linked))
    D = {}
    for r in csv.DictReader(open(DVAL)):
        D[(r["rung"], r["host"])] = float(r["D"])
    M = list(csv.DictReader(open(A.EVAL)))
    row = {}
    for r in M:
        if r["strength"] != "":
            continue
        if r["fam"] == "ladder" and r["rung"] in ("R4", "R3") and r["tool"] in ("opencv", "facemorpher"):
            row[(r["rung"], r["tool"], r["host"])] = r["id"]
        if r["fam"] == "splice" and r["rung"] in ("S4", "S3"):
            row[(r["rung"], "opencv", r["host"])] = r["id"]
    clean69 = [h for h in clean if h not in set(linked)]
    sets = {"dev+clean80": dev + clean, "dev": dev, "clean80": clean, "dev+clean69": dev + clean69, "test191": test,
            "test159": test159}   # check A4 F2: clean80 and dev+clean69 printed
    contrasts = {"R4_vs_R3_opencv": ("R4", "R3", "opencv"), "S4_vs_S3": ("S4", "S3", "opencv"),
                 "R4_vs_R3_facemorpher": ("R4", "R3", "facemorpher")}
    # person components of the host-partner graph (within each host set)
    def components(hosts):
        hs = set(hosts)
        par = {h: h for h in hosts}

        def f(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for h in hosts:
            p = lad[h]["partner_B"]
            if p in hs:
                par[f(h)] = f(p)
        comp = {}
        for h in hosts:
            comp.setdefault(f(h), []).append(h)
        return list(comp.values())
    R = dict(mock=a.mock, host_sets={k: len(v) for k, v in sets.items()}, shape_linked=linked, status={}, networks={})
    nets = {}
    allids = {v for v in row.values()}
    for arm in ("A", "B", "Sb"):
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 10 + {"A": 1, "B": 2, "Sb": 3}[arm])   # check A4 F6
                x = {}
                for (rung, tool, h), i in row.items():
                    x[i] = float(r.normal((1.0 if arm == "Sb" else 0.4) if rung in ("R4", "S4") else 0.0, 1.0))
                x = {k: v for k, v in x.items()}
            else:
                x, _, why = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                if x is None:
                    R["status"][key] = why
                    continue
            assert all(i in x and math.isfinite(x[i]) for i in allids)
            R["status"][key] = "read"
            nets[(arm, s)] = x

    def arrays(hosts, cname, x):
        pr, nr, tool = contrasts[cname]
        dp = "S4" if pr in ("R4", "S4") else pr
        dn = "S3"
        ph = [h for h in hosts if (pr, tool, h) in row and (dp, h) in D]
        nh = [h for h in hosts if (nr, tool, h) in row and (dn, h) in D]
        return (ph, nh, np.array([x[row[(pr, tool, h)]] for h in ph]), np.array([D[(dp, h)] for h in ph]),
                np.array([x[row[(nr, tool, h)]] for h in nh]), np.array([D[(dn, h)] for h in nh]))
    rng = np.random.default_rng(20261120)
    R["contrasts"] = {}
    for cname in contrasts:
        for sname, hosts in sets.items():
            comps = components(hosts)
            decides = (cname == "R4_vs_R3_opencv" and sname == "dev+clean80") or (cname == "S4_vs_S3" and sname == "clean80")   # lead: S4 vs S3 decided on clean80
            draws = [rng.integers(0, len(comps), len(comps)) for _ in range(2000)] if decides else []
            res = dict(per_seed={}, n_components=len(comps))
            for (arm, s), x in nets.items():
                ph, nh, ps, pd, ns, nd = arrays(hosts, cname, x)
                res["per_seed"][f"{arm}_s{s}"] = dict(strat=strat_auc(ps, pd, ns, nd), unstrat=C2.fauc(ps, ns), n_pos=len(ps), n_neg=len(ns))
            for other in ("B", "A"):
                rd = [s for s in SEEDS if (("Sb", s) in nets and (other, s) in nets and res["per_seed"][f"Sb_s{s}"]["strat"] is not None
                                           and res["per_seed"][f"{other}_s{s}"]["strat"] is not None)]
                g = {s: res["per_seed"][f"Sb_s{s}"]["strat"] - res["per_seed"][f"{other}_s{s}"]["strat"] for s in rd}
                gu = {s: res["per_seed"][f"Sb_s{s}"]["unstrat"] - res["per_seed"][f"{other}_s{s}"]["unstrat"] for s in rd}
                out = dict(read_seeds=rd, gain=g, seed_mean=float(np.mean(list(g.values()))) if g else None,
                           unstrat_gain=gu, unstrat_seed_mean=float(np.mean(list(gu.values()))) if gu else None)
                if draws and len(rd) >= 4:
                    bm = []
                    for dr in draws:
                        hs = [h for k in dr for h in comps[k]]
                        vals = []
                        for s in rd:
                            sv = []
                            for arm in ("Sb", other):
                                ph, nh, ps, pd, ns, nd = arrays(hs, cname, nets[(arm, s)])
                                sv.append(strat_auc(ps, pd, ns, nd))
                            if None not in sv:
                                vals.append(sv[0] - sv[1])
                        if len(vals) == len(rd):
                            bm.append(np.mean(vals))
                    lo, hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
                    npos = sum(v > 0 for v in g.values())
                    present = (out["seed_mean"] >= 0.03 and lo > 0 and ((len(rd) == 5 and npos >= 4) or (len(rd) == 4 and npos == 4))
                               and out["unstrat_seed_mean"] > 0)          # check A4 F3
                    v = "present" if present else ("absent" if hi < 0.03 else "inconclusive")
                    out.update(ci=[lo, hi], ci_half_width=(hi - lo) / 2, n_boot_used=len(bm), n_positive=npos, verdict=v)
                elif draws:
                    out["verdict"] = "not read (fewer than 4 readable seeds)"
                res[f"Sb_minus_{other}"] = out
            R["contrasts"][f"{cname}|{sname}"] = res
    # check A4 F2: sign disagreement between the 100 development hosts and the 80 clean test hosts caps the primary at inconclusive
    for o in ("B", "A"):
        prim = R["contrasts"]["R4_vs_R3_opencv|dev+clean80"][f"Sb_minus_{o}"]
        md = R["contrasts"]["R4_vs_R3_opencv|dev"][f"Sb_minus_{o}"]["seed_mean"]
        mc = R["contrasts"]["R4_vs_R3_opencv|clean80"][f"Sb_minus_{o}"]["seed_mean"]
        prim["dev_vs_clean80_seed_means"] = [md, mc]
        if md is not None and mc is not None and (md > 0) != (mc > 0) and prim.get("verdict") in ("present", "absent"):
            prim["verdict_before_cap"] = prim["verdict"]
            prim["verdict"] = "inconclusive (sign disagreement between development and clean test hosts)"
    # within-D floors (printed; different row sets, context only)
    import json as _j
    R["within_D_floors"] = {c: _j.loads((pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors") / f"{c}_withinD.json").read_text())
                            for c in ("ri_R4_vs_R3", "test_cv_R4_vs_R3")}
    # adversary floors (printed)
    if not a.mock:
        import check
        R["adv_floors"] = {f"{arm}_s{s}": {c: dict(all=check.exceeds(c, x), nuisance=check.exceeds(c, x, floor="nuisance"))
                                          for c in ADV_CONTRASTS} for (arm, s), x in nets.items()}
        if a.learner:
            assert sha(a.learner) == a.learner_sha
            d = str(pathlib.Path(a.learner).parent)
            assert subprocess.run(["git", "-C", d, "ls-files", "--error-unmatch", pathlib.Path(a.learner).name], capture_output=True).returncode == 0
            R["same_data_learner"] = json.loads(pathlib.Path(a.learner).read_text())
    V = {k: {o: R["contrasts"][k][f"Sb_minus_{o}"].get("verdict") for o in ("B", "A")}
         for k in ("R4_vs_R3_opencv|dev+clean80", "S4_vs_S3|clean80")}
    R["verdicts"] = dict(primary_R4_vs_R3=V["R4_vs_R3_opencv|dev+clean80"], secondary_S4_vs_S3_clean80=V["S4_vs_S3|clean80"],
                         label="recipe at replication seeds 408-412, development plus clean test hosts, post hoc, not held-out; "
                               "not a property of the frozen networks 403-407")
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps(R["verdicts"], indent=1))


if __name__ == "__main__":
    main()

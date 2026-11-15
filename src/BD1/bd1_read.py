"""Blend-difference attribution (BD1) reader (experiments/BD1_blend-difference-attribution/prereg.md). Zero GPU.
Blocks, each read separately, never pooled: FS1 (registered; PN1_<arm>_s403-407, A100), AB1 (replication; AB1_Sb_s408-412,
H100), SE1 (replication; SE1_Sb_s408-411, A100). Scores from each tar's scores_eval.npz after a sha256 check.
  python -I bd1_read.py --out bd1_read.json
  python -I bd1_read.py --mock --dfile FILE --out mock.json   (random logits and a given D file; code test only)"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np
from scipy.stats import rankdata, spearmanr

DFILE = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
BLOCKS = {
    "FS1": [(f"/mnt/t7/smad_next/PN1/results_fs/PN1_{a}_s{s}.tar", f"PN1_{a}_s{s}", a, s) for a in ("A", "B", "Sb") for s in range(403, 408)],
    "AB1": [(f"/mnt/t7/smad_next/AB1/results/AB1_Sb_s{s}.tar", f"AB1_Sb_s{s}", "Sb", s) for s in range(408, 413)],
    "SE1": [(f"/mnt/t7/smad_next/SE1/results/SE1_Sb_s{s}.tar", f"SE1_Sb_s{s}", "Sb", s) for s in range(408, 412)],
}
B = 2000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def auc(p, n):
    p, n = np.asarray(p, float), np.asarray(n, float)
    r = rankdata(np.r_[p, n])[: len(p)]
    return float((r.sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n)))


def strat_auc(p, n, dp, dn, q=5):
    lp, ln_ = np.log(dp), np.log(dn)
    e = np.quantile(np.r_[lp, ln_], np.linspace(0, 1, q + 1))
    bp = np.clip(np.searchsorted(e, lp, side="right") - 1, 0, q - 1)
    bn = np.clip(np.searchsorted(e, ln_, side="right") - 1, 0, q - 1)
    good, num, den, cov = [], 0.0, 0.0, 0
    for b in range(q):
        pp, nn = p[bp == b], n[bn == b]
        good.append(dict(stratum=b, n_pos=int(len(pp)), n_neg=int(len(nn)), auc=(auc(pp, nn) if len(pp) and len(nn) else None)))
        if len(pp) >= 10 and len(nn) >= 10:
            w = len(pp) * len(nn)
            num += auc(pp, nn) * w
            den += w
            cov += len(pp) + len(nn)
    cover = cov / (len(p) + len(n))
    return (num / den if den else None), cover, good


def window_auc(p, n, dp, dn, width=0.05):
    pct = rankdata(np.r_[dp, dn]) / (len(dp) + len(dn))
    pp, pn = pct[: len(dp)], pct[len(dp):]
    num = den = 0.0
    for i in range(len(p)):
        m = np.abs(pn - pp[i]) <= width
        if m.any():
            num += (p[i] > n[m]).sum() + 0.5 * (p[i] == n[m]).sum()
            den += m.sum()
    return (num / den if den else None), int(den)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dfile", default=str(DFILE))
    a = ap.parse_args()
    D = {r["id"]: r for r in csv.DictReader(open(a.dfile))}
    if not a.mock:
        assert sha(a.dfile) == pathlib.Path(a.dfile + ".sha256").read_text().split()[0]
    out = dict(mock=a.mock, dfile_sha256=sha(a.dfile), blocks={})
    for r in D.values():
        for k in ("D", "D_int", "D_band"):
            if k in r:
                assert float(r[k]) > 0 or r["rung"] == "S0" or k != "D", ("D must be > 0", r["id"])
    RG = ("S4", "S3", "S0")
    test = {rg: sorted([i for i, r in D.items() if r["role"] == "test" and r["rung"] == rg], key=lambda i: D[i]["host"]) for rg in RG}
    dev = {rg: sorted([i for i, r in D.items() if r["role"] == "dev" and r["rung"] == rg], key=lambda i: D[i]["host"]) for rg in RG}
    dv = lambda L, k="D": np.array([float(D[i][k]) for i in L])   # noqa: E731
    # amendment 1: pure-D reference (D itself as the score), same rows and same functions
    ref_q = strat_auc(dv(test["S4"]), dv(test["S3"]), dv(test["S4"]), dv(test["S3"]))
    ref_w = window_auc(dv(test["S4"]), dv(test["S3"]), dv(test["S4"]), dv(test["S3"]))
    out["reference_pure_D"] = dict(quintile=ref_q[0], quintile_cover=ref_q[1], window=ref_w[0], window_pairs=ref_w[1])
    out["D_by_db"] = {f"{rg}:{hd}-{pd}": float(np.median([float(D[i]["D"]) for i in test[rg] if D[i]["db_host"] == hd and D[i]["db_partner"] == pd]))
                      for rg in RG for hd in ("frgc", "feret") for pd in ("frgc", "feret")
                      if any(D[i]["db_host"] == hd and D[i]["db_partner"] == pd for i in test[rg])}
    out["rho_DS3_G"] = float(spearmanr(dv(test["S3"]), dv(test["S3"], "G")).correlation)
    a0 = auc(dv(test["S4"]), dv(test["S3"]))
    out["D_alone_test_S4_vs_S3"] = max(a0, 1 - a0)
    out["D_median_test"] = {rg: float(np.median(dv(test[rg]))) for rg in test}
    out["n"] = {k: len(v) for k, v in test.items()}
    for blk, nets in BLOCKS.items():
        res = {}
        flags = {}
        for path, name, arm, s in nets:
            try:
                if not a.mock:
                    want = pathlib.Path(path + ".sha256").read_text().split()[0]
                    assert sha(path) == want, "sha"
                if a.mock:                               # review F4: the mock opens no tar
                    rng = np.random.default_rng(s)
                    L = {i: float(rng.normal(-1, 2)) for i in D}
                else:
                    with tarfile.open(path) as tf:
                        z = np.load(io.BytesIO(tf.extractfile(f"{name}/scores_eval.npz").read()))
                    L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                assert all(i in L for v in list(test.values()) + list(dev.values()) for i in v)
            except Exception as ex:                      # missing or off-pin: counts as not meeting
                res[f"{arm}_s{s}"] = dict(error=repr(ex))
                continue
            v = lambda ids: np.array([L[i] for i in ids])   # noqa: E731
            p, n = v(test["S4"]), v(test["S3"])
            sa, cover, strata = strat_auc(p, n, dv(test["S4"]), dv(test["S3"]))
            wa, npairs = window_auc(p, n, dv(test["S4"]), dv(test["S3"]))
            readable_q, readable_w = cover >= 0.5, npairs >= 1000
            primary = sa if readable_q else (wa if readable_w else None)
            rng = np.random.default_rng(20261151)
            hs = len(test["S4"])
            assert [D[i]["host"] for i in test["S4"]] == [D[i]["host"] for i in test["S3"]], "host order"
            bs, low = [], 0
            for _ in range(B):
                ix = rng.integers(0, hs, hs)
                if readable_q:
                    x, cv_, _ = strat_auc(p[ix], n[ix], dv(test["S4"])[ix], dv(test["S3"])[ix])
                    low += int(cv_ < 0.5)
                else:
                    x = window_auc(p[ix], n[ix], dv(test["S4"])[ix], dv(test["S3"])[ix])[0]
                if x is not None:
                    bs.append(x)
            pd_, nd_ = v(dev["S4"]), v(dev["S3"])
            ref = ref_q[0] if readable_q else (ref_w[0] if readable_w else None)
            extra = {}
            for kk in ("D_int", "D_band", "D_Y"):
                extra[f"strat_auc_{kk}"] = strat_auc(p, n, dv(test["S4"], kk), dv(test["S3"], kk))[0]
                extra[f"rho_logit_{kk}_S3"] = float(spearmanr(n, dv(test["S3"], kk)).correlation)
            s0 = v(test["S0"])
            res[f"{arm}_s{s}"] = dict(
                auc_test=auc(p, n), strat_auc_test=sa, cover=cover, strata=strata, window_auc_test=wa, window_pairs=npairs,
                primary=primary, primary_kind=("quintile" if readable_q else ("window" if readable_w else "not readable")),
                primary_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
                rho_logit_D_S3=float(spearmanr(n, dv(test["S3"])).correlation),
                rho_logit_D_S4=float(spearmanr(p, dv(test["S4"])).correlation),
                auc_dev=auc(pd_, nd_), strat_auc_dev=strat_auc(pd_, nd_, dv(dev["S4"]), dv(dev["S3"]))[0],
                S3_flag_test=float((n > 0).mean()), reference=ref,
                primary_minus_ref=(primary - ref) if (primary is not None and ref is not None) else None,
                boot_low_cover_draws=low, rho_logit_D_S0=float(spearmanr(s0, dv(test["S0"])).correlation),
                S0_flag_test=float((s0 > 0).mean()), rho_logit_G_S3=float(spearmanr(n, dv(test["S3"], "G")).correlation), **extra)
            if arm == "Sb":
                flags[s] = (n > 0).astype(int)
        V = {}
        sb = [k for k in res if k.startswith("Sb_")]
        nseed = len([x for x in nets if x[2] == "Sb"])
        need = 4
        prim = [res[k].get("primary") for k in sb]
        rel = [res[k].get("primary_minus_ref") for k in sb]
        r3 = [res[k].get("rho_logit_D_S3") for k in sb]
        if flags:
            kcount = np.sum(list(flags.values()), axis=0)
            rho_p = float(spearmanr(dv(test["S3"]), kcount).correlation) if kcount.std() > 0 else None
            persist_all = int((kcount == len(flags)).sum())
            persist_all_but1 = int((kcount >= len(flags) - 1).sum())
            rho_p_var = {kk: (float(spearmanr(dv(test["S3"], kk), kcount).correlation) if kcount.std() > 0 else None)
                         for kk in ("D_int", "D_band", "D_Y", "G")}
        else:
            rho_p, persist_all, persist_all_but1, rho_p_var = None, 0, 0, {}
        # amendment 1 rule: relative to the pure-D reference, with the within-S3 co-condition
        npass = sum(1 for x in rel if x is not None and x <= 0.05)
        n_r3 = sum(1 for x in r3 if x is not None and x >= 0.2)
        nfail = sum(1 for x in rel if x is not None and x >= 0.12)
        ver = ("pass: no S4-vs-S3 signal beyond pixel-difference magnitude D" if npass >= need and n_r3 >= need
               and rho_p is not None and rho_p >= 0.4 else
               "fail: a residual beyond D (identity or content D misses)" if nfail >= need else "inconclusive")
        V["Sb"] = dict(n_seeds=nseed, primary=prim, primary_minus_ref=rel, rho_logit_D_S3=r3, n_rel_le_005=npass,
                       n_rho_S3_ge_02=n_r3, n_rel_ge_012=nfail, rho_D_persistence=rho_p, rho_persistence_variants=rho_p_var,
                       n_S3_flagged_all_seeds=persist_all, n_S3_flagged_all_but_one=persist_all_but1, verdict=ver,
                       role=("registered" if blk == "FS1" else "replication"))
        out["blocks"][blk] = dict(per_net=res, verdicts=V)
    reg = out["blocks"]["FS1"]["verdicts"]["Sb"]["verdict"]
    for blk in ("AB1", "SE1"):
        v = out["blocks"][blk]["verdicts"]["Sb"]
        v["replicates_registered"] = (v["verdict"] == reg)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(D_alone=out["D_alone_test_S4_vs_S3"], D_median=out["D_median_test"], n=out["n"],
                          reference=out["reference_pure_D"], rho_DS3_G=out["rho_DS3_G"], D_by_db=out["D_by_db"]), default=float))
    for blk in out["blocks"]:
        print(blk, json.dumps(out["blocks"][blk]["verdicts"], default=float))
        for k, r in out["blocks"][blk]["per_net"].items():
            if "error" in r:
                print("  ", k, r["error"])
            else:
                print("  ", k, {x: (round(r[x], 3) if isinstance(r[x], float) else r[x]) for x in ("auc_test", "strat_auc_test", "cover", "window_auc_test", "primary_kind", "primary_minus_ref", "rho_logit_D_S3", "rho_logit_D_S0", "S3_flag_test", "strat_auc_D_int", "strat_auc_D_band")})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

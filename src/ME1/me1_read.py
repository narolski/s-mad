"""Layer misregistration echo (ME1) reader, amendment 1 (pre-run check c23f7e0: O1-O4, S1-S5, L1, M1). Zero GPU.
Development data only. Parts: --part oracle (may be read now) | --part single (refuses to run until the adversary's
dev_S4_vs_S3 and test_S4_vs_S3 floor files exist) | --part all.
  python -I me1_read.py --part oracle --out me1_oracle.json
  python -I me1_read.py --mock --part all --ffile F --out mock.json   (every real quantity randomised; no tar opened)"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
sys.path.insert(0, "/home/narolski/smad-next/src/TB1")
sys.path.insert(0, "/home/narolski/smad-next/src/RI1")
from bd1_read import auc, sha, strat_auc  # noqa: E402
from tb1_amend2 import components, tem  # noqa: E402

EMPTY = {"folds": 0}


def cf_scores(X1, X0, comp, seed=20261181, folds=5):
    """code fix after the ME1 oracle outcome: like tb1_amend2.cf_scores, but empty folds are skipped and counted"""
    from sklearn.linear_model import LogisticRegression
    cs = sorted(set(comp))
    rng = np.random.default_rng(seed)
    f = dict(zip(cs, rng.permutation(len(cs)) % folds))
    g = np.array([f[c] for c in comp] * 2)
    X = np.r_[X1, X0]
    y = np.r_[np.ones(len(X1)), np.zeros(len(X0))]
    s = np.zeros(len(y))
    for k in range(folds):
        tr, te = g != k, g == k
        if te.sum() == 0 or len(set(y[tr])) < 2:
            EMPTY["folds"] += 1
            continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=5000).fit((X[tr] - mu) / sd, y[tr])
        s[te] = m.decision_function((X[te] - mu) / sd)
    return s[: len(X1)], s[len(X1):]
from ri1_read import crossfit_best_single  # noqa: E402

FFILE = pathlib.Path("/mnt/t7/smad_next/ME1/me1_feats.csv")
TB1F = pathlib.Path("/mnt/t7/smad_next/TB1/tb1_feats.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
TONE = pathlib.Path("/mnt/t7/smad_next/PN1/cues/tone_splice.npz")
RATIO = pathlib.Path("/mnt/t7/smad_next/PN1/cues/ratio_splice.npz")
ADV = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000
SEED = 20261191
SENT = ("A pass means that two-person blends show more between-landmark misregistration than same-person blends, at equal "
        "D. It does not separate this from FR dissimilarity or W (cos_HB <= 0.65 < 0.68 <= cos_HS). It holds for landmark "
        "morphs on one engine only, and it is not a detector. An oracle pass licenses nothing about one image.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--part", choices=("oracle", "single", "all"), required=True)
    ap.add_argument("--ffile", default=str(FFILE))
    a = ap.parse_args()
    if a.part != "oracle" and not a.mock:                       # pre-run S3: adversary floors must exist
        for c in ("dev_S4_vs_S3", "test_S4_vs_S3"):
            assert (ADV / f"{c}.json").exists(), f"ADV floor {c} pending"
    if not a.mock:
        for f in (a.ffile, str(TB1F), str(DF)):
            assert sha(f) == pathlib.Path(f + ".sha256").read_text().split()[0]
    R = list(csv.DictReader(open(a.ffile)))
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    T = {r["host"]: r for r in csv.DictReader(open(TB1F))}
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    hosts = [r["host"] for r in R]
    cmap = components(hosts, pool)
    comp = [cmap[h] for h in hosts]
    db = np.array([pool[h]["db"] for h in hosts])
    role = np.array([r["role"] for r in R])
    n = len(R)
    num = lambda k: np.array([float(r[k]) if r[k] not in ("", "nan") else np.nan for r in R])   # noqa: E731
    E4 = np.log(np.array([float(T[h]["P4_Etot"]) for h in hosts]))
    E3 = np.log(np.array([float(T[h]["P3_Etot"]) for h in hosts]))
    W4 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["B"]), axis=1).mean() for h in hosts]))
    W3 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["S"]), axis=1).mean() for h in hosts]))
    Gc = np.array([np.linalg.norm(0.5 * (tem(pool[h]["H"]) + tem(pool[h]["B"])) - 0.5 * (tem(pool[h]["H"]) + tem(pool[h]["S"])), axis=1).mean()
                   for h in hosts])                              # O2: landmark distance |mean(H,B) - mean(H,S)|
    D4 = np.array([float(D[r["S4_id"]]["D"]) for r in R])
    D3 = np.array([float(D[r["S3_id"]]["D"]) for r in R])
    O4, O3 = np.log(num("O4_gated") + 1e-6), np.log(num("O3_gated") + 1e-6)
    Q4, Q3 = np.log(num("O4_resp")), np.log(num("O3_resp"))
    C = num("C_gated")
    rungs = ("S4", "S3", "S0", "R2w4", "R2w", "R4", "R3", "R0", "R0_61", "R0_m7")
    ech = {k: np.log(num(f"{k}_echo_ratio")) for k in rungs}
    if a.mock:
        rng = np.random.default_rng(11)
        E4, E3, W4, W3, O4, O3, Q4, Q3, C, Gc = (rng.normal(size=n) for _ in range(10))
        D4, D3 = np.exp(rng.normal(size=n)), np.exp(rng.normal(size=n))
        ech = {k: rng.normal(size=n) for k in ech}
    out = dict(mock=a.mock, part=a.part, n=n, n_components=len(set(comp)), by_db={d: int((db == d).sum()) for d in ("frgc", "feret")},
               strata_vary_per_class=dict(W=bool(not np.allclose(W4, W3)), E=bool(not np.allclose(E4, E3)), D=bool(not np.allclose(D4, D3))),
               licence_sentence=SENT)

    def strat_db(x4, x3, s4, s3, idx=None):
        """O4: quintiles inside each database, combined with weights n_pos x n_neg; coverage over both"""
        idx = np.arange(n) if idx is None else np.asarray(idx)
        num_ = den = 0.0
        cov = 0
        for d_ in ("frgc", "feret"):
            m = idx[db[idx] == d_]
            ok = m[np.isfinite(x4[m]) & np.isfinite(x3[m])]
            if len(ok) < 20:
                continue
            q = np.quantile(np.r_[s4[ok], s3[ok]], np.linspace(0, 1, 6))
            b4 = np.clip(np.searchsorted(q, s4[ok], side="right") - 1, 0, 4)
            b3 = np.clip(np.searchsorted(q, s3[ok], side="right") - 1, 0, 4)
            for k in range(5):
                p, ng = x4[ok][b4 == k], x3[ok][b3 == k]
                if len(p) >= 10 and len(ng) >= 10:
                    w = len(p) * len(ng)
                    num_ += auc(p, ng) * w
                    den += w
                    cov += len(p) + len(ng)
        c = cov / (2 * len(idx))
        return dict(auc=(num_ / den if den else None), cover=c, coverage_ok=bool(c >= 0.50))

    def cfgain(b4, b3, x4, x3, idx=None):
        idx = np.arange(n) if idx is None else np.asarray(idx)
        cp = [comp[i] for i in idx]
        a0 = auc(*cf_scores(b4[idx], b3[idx], cp, SEED))
        a1 = auc(*cf_scores(np.c_[b4[idx], x4[idx]], np.c_[b3[idx], x3[idx]], cp, SEED))
        return a1 - a0, a0, a1

    cs = sorted(set(comp))
    mem = {c_: [i for i, x in enumerate(comp) if x == c_] for c_ in cs}

    def comp_boot(fn, draws=B):
        rng = np.random.default_rng(20261192)
        v, fail = [], 0
        for _ in range(draws if not a.mock else 30):
            idx = np.array([i for p in rng.choice(len(cs), len(cs)) for i in mem[cs[p]]])
            try:
                x = fn(idx)
                if x is None or not np.isfinite(x):
                    raise ValueError
                v.append(x)
            except Exception:
                fail += 1
        return ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if v else [None, None]), fail

    def gain_rule(g, ci, fail, draws):
        if fail > 0.01 * draws:
            return "inconclusive (> 1% bootstrap failures)"
        return "no (gain < +0.02)" if g < 0.02 else ("yes (gain >= +0.03, lower bound > 0)" if g >= 0.03 and ci[0] is not None and ci[0] > 0 else "inconclusive")

    if a.part in ("oracle", "all"):
        ok = np.isfinite(O4) & np.isfinite(O3) & np.isfinite(Q4) & np.isfinite(Q3)
        idx = np.where(ok)[0]
        O = dict(n_finite=int(ok.sum()), n_dropped=int((~ok).sum()))
        O["calibration"] = dict(spearman=float(spearmanr(C[np.isfinite(C)], Gc[np.isfinite(C)]).correlation),
                                n=int(np.isfinite(C).sum()))
        valid = O["calibration"]["spearman"] >= 0.5
        O["auc"] = auc(O4[idx], O3[idx])
        O["auc_ci"], _ = comp_boot(lambda ix: auc(O4[ix][np.isfinite(O4[ix]) & np.isfinite(O3[ix])], O3[ix][np.isfinite(O4[ix]) & np.isfinite(O3[ix])]))
        O["W_alone"], O["E_alone"] = auc(W4, W3), auc(E4, E3)
        O["ungated_auc_printed"] = auc(np.log(num("O4_ungated") + 1e-6), np.log(num("O3_ungated") + 1e-6)) if not a.mock else None
        O["frac_above_null_median"] = dict(two=float(np.nanmedian(num("O4_frac"))), same=float(np.nanmedian(num("O3_frac")))) if not a.mock else None
        O["within_W"] = strat_db(O4, O3, np.exp(W4), np.exp(W3), idx)
        O["within_W_ci"], _ = comp_boot(lambda ix: strat_db(O4, O3, np.exp(W4), np.exp(W3), ix)["auc"], draws=500)
        O["within_E"] = strat_db(O4, O3, np.exp(E4), np.exp(E3), idx)
        O["within_D"] = strat_db(O4, O3, D4, D3, idx)
        b4, b3 = np.c_[E4, W4, Q4], np.c_[E3, W3, Q3]                # O3: base includes the median response
        g = cfgain(b4, b3, O4[:, None], O3[:, None], idx)

        def bfn(ix):
            ix = ix[ok[ix]]
            cp = [comp[i] for i in ix]
            return (auc(*cf_scores(np.c_[b4[ix], O4[ix]], np.c_[b3[ix], O3[ix]], cp, SEED))
                    - auc(*cf_scores(b4[ix], b3[ix], cp, SEED)))
        ci, fail = comp_boot(bfn)
        O["gain_over_logE_logW_resp"] = dict(gain=g[0], base=g[1], plus=g[2], ci_95pct_percentile=ci, failed=fail,
                                             rule=gain_rule(g[0], ci, fail, B))
        O["gain_over_logE_logW_printed"] = cfgain(np.c_[E4, W4], np.c_[E3, W3], O4[:, None], O3[:, None], idx)[0]
        for d_ in ("frgc", "feret"):
            m = idx[db[idx] == d_]
            O[d_] = dict(auc=auc(O4[m], O3[m]), within_W=strat_db(O4, O3, np.exp(W4), np.exp(W3), m))
        if not valid:
            O["verdict"] = "invalid (estimator): calibration Spearman < 0.5"
        elif not O["within_W"]["coverage_ok"]:
            O["verdict"] = "inconclusive (coverage)"
        elif O["auc"] <= 0.65 or (O["within_W"]["auc"] is not None and O["within_W"]["auc"] <= 0.55):
            O["verdict"] = "killed"
        elif O["auc"] >= 0.75 and (O["frgc"]["within_W"]["auc"] or 0) >= 0.60:
            O["verdict"] = "premise holds (>= 0.75 overall, >= 0.60 within W on FRGC)"
        else:
            O["verdict"] = "inconclusive"
        out["oracle"] = O
    if a.part in ("single", "all"):
        S = {}

        def drop(x, y):
            m = np.isfinite(x) & np.isfinite(y)
            return x[m], y[m], int((~m).sum())
        notm = [k for k in rungs if np.mean(~np.isfinite(ech[k])) > 0.05]
        S["rungs_not_measured_over_5pct_missing"] = notm
        e4, e3 = ech["S4"], ech["S3"]
        S["S4_vs_S3"] = dict(auc=auc(*drop(e4, e3)[:2]), within_D=strat_db(e4, e3, D4, D3),
                             pure_D_reference=strat_auc(D4, D3, D4, D3)[0])
        S["S4_vs_S3_within_D_ci"], _ = comp_boot(lambda ix: strat_db(e4, e3, D4, D3, ix)["auc"], draws=500)
        S["one_vs_two_layers"] = dict(S4_vs_R2w4=auc(*drop(ech["S4"], ech["R2w4"])[:2]), S3_vs_R2w=auc(*drop(ech["S3"], ech["R2w"])[:2]))
        d4_, d3_ = ech["S4"] - ech["R2w4"], ech["S3"] - ech["R2w"]
        S["paired_difference_within_D"] = strat_db(d4_, d3_, D4, D3)
        ctrl = {k: auc(*drop(ech[x], ech[y])[:2]) for k, (x, y) in dict(
            R0_61_vs_R0=("R0_61", "R0"), R2w4_vs_R0m7=("R2w4", "R0_m7"), S0_vs_R2w4=("S0", "R2w4"), R2w4_vs_R2w=("R2w4", "R2w")).items()}
        ctrl["R2w4_vs_R0_mH_printed"] = auc(*drop(ech["R2w4"], ech["R0"])[:2])
        ctrl["S0_vs_R0_printed"] = auc(*drop(ech["S0"], ech["R0"])[:2])
        ctrl["border"] = "not controlled"
        S["controls"] = ctrl
        bad = [k for k in ("R0_61_vs_R0", "R2w4_vs_R0m7", "S0_vs_R2w4", "R2w4_vs_R2w") if not (0.42 <= ctrl[k] <= 0.58)]
        S["controls_bad"] = bad
        cs_ = np.load(CUE_SPL)
        Cc = {str(i): c for i, c in zip(cs_["ids"], cs_["cues"])}
        zt, zr = np.load(TONE), np.load(RATIO)
        tone = {str(i): v for i, v in zip(zt["ids"], zt["tone"])}
        rat = {str(i): float(v) for i, v in zip(zr["ids"], zr["ratio"])}
        tbr = lambda h, s_: np.array([float(T[h][f"{s_}_r{k}"]) for k in range(1, 6)])       # noqa: E731   (TB1 band features)
        X4 = np.array([np.r_[Cc[r["S4_id"]], tone[r["S4_id"]], np.log(rat[r["S4_id"]] + 1e-6), tbr(r["host"], "S4")] for r in R])
        X3 = np.array([np.r_[Cc[r["S3_id"]], tone[r["S3_id"]], np.log(rat[r["S3_id"]] + 1e-6), tbr(r["host"], "S3")] for r in R])
        if a.mock:
            rng = np.random.default_rng(12)
            X4, X3 = rng.normal(size=X4.shape), rng.normal(size=X3.shape)
        okS = np.where(np.isfinite(e4) & np.isfinite(e3))[0]
        g = cfgain(X4, X3, e4[:, None], e3[:, None], okS)

        def sfn(ix):
            ix = ix[np.isfinite(e4[ix]) & np.isfinite(e3[ix])]
            cp = [comp[i] for i in ix]
            return (auc(*cf_scores(np.c_[X4[ix], e4[ix]], np.c_[X3[ix], e3[ix]], cp, SEED)) - auc(*cf_scores(X4[ix], X3[ix], cp, SEED)))
        ci, fail = comp_boot(sfn)
        S["shortcut_gain"] = dict(gain=g[0], base=g[1], plus=g[2], ci_95pct_percentile=ci, failed=fail, rule=gain_rule(g[0], ci, fail, B))
        S["adversary_floors"] = {c: json.load(open(ADV / f"{c}.json")) for c in ("dev_S4_vs_S3", "test_S4_vs_S3")} if not a.mock else None
        S["floor_27stat_best_single"] = crossfit_best_single(X4[okS][:, :27], X3[okS][:, :27], [hosts[i] for i in okS], [hosts[i] for i in okS])
        inc = {}
        for s in range(403, 408):
            if a.mock:
                rr = np.random.default_rng(s)
                l4, l3 = rr.normal(size=n), rr.normal(size=n)
            else:
                t_ = FS / f"PN1_Sb_s{s}.tar"
                assert sha(t_) == pathlib.Path(str(t_) + ".sha256").read_text().split()[0]
                with tarfile.open(t_) as tf:
                    z = np.load(io.BytesIO(tf.extractfile(f"PN1_Sb_s{s}/scores_eval.npz").read()))
                L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                l4, l3 = np.array([L[r["S4_id"]] for r in R]), np.array([L[r["S3_id"]] for r in R])
            inc[str(s)] = dict(all=cfgain(l4[:, None], l3[:, None], e4[:, None], e3[:, None], okS)[0],
                               test=cfgain(l4[:, None], l3[:, None], e4[:, None], e3[:, None], okS[role[okS] == "test"])[0])
        S["sb_increment"] = inc
        S["per_database"] = {d_: dict(S4_vs_S3_within_D=strat_db(e4, e3, D4, D3, np.where(db == d_)[0])) for d_ in ("frgc", "feret")}
        wd = S["S4_vs_S3"]["within_D"]
        pdw = S["paired_difference_within_D"]["auc"]
        if notm:
            S["verdict"] = f"not measured ({', '.join(notm)} > 5% missing)"
        elif bad:
            S["verdict"] = f"invalid (control): {', '.join(bad)} outside [0.42, 0.58]"
        elif S["one_vs_two_layers"]["S4_vs_R2w4"] <= 0.55 and S["one_vs_two_layers"]["S3_vs_R2w"] <= 0.55:
            S["verdict"] = "closed: the statistic does not see a second layer"
        elif not wd["coverage_ok"]:
            S["verdict"] = "inconclusive (coverage)"
        elif wd["auc"] is not None and wd["auc"] <= 0.60:
            S["verdict"] = "killed: S4 vs S3 within D <= 0.60"
        elif (wd["auc"] or 0) >= 0.65 and (pdw or 0) >= 0.65 and (S["S4_vs_S3_within_D_ci"][0] or 0) > 0.60:
            S["verdict"] = "readable: two-person blends show more between-landmark echo than same-person blends at equal D"
        else:
            S["verdict"] = "inconclusive"
        S["arm_condition"] = dict(sb_increment_seeds=sum(v["all"] >= 0.03 for v in inc.values()),
                                  shortcut_gain_rule=S["shortcut_gain"]["rule"], note="no arm before the look-alike set (LA1) exists")
        out["single"] = S
    out["empty_folds"] = EMPTY["folds"]
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=0, default=float)[:3000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

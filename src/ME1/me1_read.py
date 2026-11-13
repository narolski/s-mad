"""Layer misregistration echo (ME1) reader (experiments/ME1_layer-misregistration-echo/prereg.md). Zero GPU.
Development data only. Parts: --part oracle | --part single | --part all (the single-image part waits for ADVERSARY's
floor if one is announced as pending).
  python -I me1_read.py --part all --out me1_read.json
  python -I me1_read.py --mock --part all --ffile F --out mock.json   (every real quantity randomised; no tar opened)"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
sys.path.insert(0, "/home/narolski/smad-next/src/TB1")
sys.path.insert(0, "/home/narolski/smad-next/src/RI1")
from bd1_read import auc, sha, strat_auc  # noqa: E402
from tb1_amend2 import cf_scores, components, tem  # noqa: E402
from ri1_read import crossfit_best_single  # noqa: E402

FFILE = pathlib.Path("/mnt/t7/smad_next/ME1/me1_feats.csv")
TB1F = pathlib.Path("/mnt/t7/smad_next/TB1/tb1_feats.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
TONE = pathlib.Path("/mnt/t7/smad_next/PN1/cues/tone_splice.npz")
RATIO = pathlib.Path("/mnt/t7/smad_next/PN1/cues/ratio_splice.npz")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--part", choices=("oracle", "single", "all"), required=True)
    ap.add_argument("--ffile", default=str(FFILE))
    a = ap.parse_args()
    if not a.mock:
        for f in (a.ffile, str(TB1F), str(DF)):
            assert sha(f) == pathlib.Path(f + ".sha256").read_text().split()[0]
    R = list(csv.DictReader(open(a.ffile)))
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    T = {r["host"]: r for r in csv.DictReader(open(TB1F))}
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    hosts = [r["host"] for r in R]
    comp = [components(hosts, pool)[h] for h in hosts]
    db = np.array([pool[h]["db"] for h in hosts])
    role = np.array([r["role"] for r in R])
    n = len(R)
    num = lambda k: np.array([float(r[k]) for r in R])        # noqa: E731
    E4 = np.log(np.array([float(T[h]["P4_Etot"]) for h in hosts]))
    E3 = np.log(np.array([float(T[h]["P3_Etot"]) for h in hosts]))
    W4 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["B"]), axis=1).mean() for h in hosts]))
    W3 = np.log(np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["S"]), axis=1).mean() for h in hosts]))
    D4 = np.array([float(D[r["S4_id"]]["D"]) for r in R])
    D3 = np.array([float(D[r["S3_id"]]["D"]) for r in R])
    O4, O3 = np.log(num("O4_shift") + 1e-6), np.log(num("O3_shift") + 1e-6)
    ech = {k: np.log(num(f"{k}_echo_ratio")) for k in ("S4", "S3", "S0", "R2w4", "R2w", "R4", "R3", "R0", "R0_61")}
    if a.mock:                                     # every real quantity randomised
        rng = np.random.default_rng(11)
        E4, E3, W4, W3, O4, O3 = (rng.normal(size=n) for _ in range(6))
        D4, D3 = np.exp(rng.normal(size=n)), np.exp(rng.normal(size=n))
        ech = {k: rng.normal(size=n) for k in ech}
    out = dict(mock=a.mock, part=a.part, n=n, n_components=len(set(comp)), by_db={d: int((db == d).sum()) for d in ("frgc", "feret")},
               strata_vary_per_class=dict(W=bool(not np.allclose(W4, W3)), E=bool(not np.allclose(E4, E3)), D=bool(not np.allclose(D4, D3))),
               statement="a pass means 'two shapes were superimposed', not 'two people', until look-alike pairs (LA1) exist")

    def strat(x4, x3, s4, s3, m=None):
        m = np.ones(n, bool) if m is None else m
        sa, cov, _ = strat_auc(x4[m], x3[m], s4[m], s3[m])
        return dict(auc=sa, cover=cov)

    def gain(b4, b3, x4, x3, m=None, seed=20261191):
        idx = np.arange(n) if m is None else np.where(m)[0]
        cp = [comp[i] for i in idx]
        a0 = auc(*cf_scores(b4[idx], b3[idx], cp, seed))
        a1 = auc(*cf_scores(np.c_[b4[idx], x4[idx]], np.c_[b3[idx], x3[idx]], cp, seed))
        return a1 - a0, a0, a1

    def comp_boot(fn):
        cs = sorted(set(comp))
        mem = {c: [i for i, x in enumerate(comp) if x == c] for c in cs}
        rng = np.random.default_rng(20261192)
        v, fail = [], 0
        for _ in range(B if not a.mock else 40):
            idx = np.array([i for p in rng.choice(len(cs), len(cs)) for i in mem[cs[p]]])
            try:
                v.append(fn(idx))
            except Exception:
                fail += 1
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], fail

    BW4, BW3 = np.c_[E4, W4], np.c_[E3, W3]
    if a.part in ("oracle", "all"):
        Ora = dict(auc=auc(O4, O3), W_alone=auc(W4, W3), E_alone=auc(E4, E3))
        Ora["within_W"] = strat(O4, O3, np.exp(W4), np.exp(W3))
        Ora["within_E"] = strat(O4, O3, np.exp(E4), np.exp(E3))
        Ora["within_D"] = strat(O4, O3, D4, D3)
        Ora["ci"], _ = comp_boot(lambda ix: auc(O4[ix], O3[ix]))
        g = gain(BW4, BW3, O4[:, None], O3[:, None])
        ci, fail = comp_boot(lambda ix: (lambda c: auc(*cf_scores(np.c_[BW4[ix], O4[ix]], np.c_[BW3[ix], O3[ix]], c))
                                         - auc(*cf_scores(BW4[ix], BW3[ix], c)))([comp[i] for i in ix]))
        Ora["gain_over_logE_logW"] = dict(gain=g[0], base=g[1], plus=g[2], ci_95pct_percentile=ci, failed=fail)
        for d_ in ("frgc", "feret"):
            m = db == d_
            Ora[d_] = dict(auc=auc(O4[m], O3[m]), within_W=strat(O4, O3, np.exp(W4), np.exp(W3), m),
                           gain_over_logE_logW=gain(BW4, BW3, O4[:, None], O3[:, None], m)[0])
        killed = Ora["auc"] <= 0.65 or (Ora["within_W"]["auc"] is not None and Ora["within_W"]["auc"] <= 0.55)
        holds = Ora["auc"] >= 0.75 and (Ora["frgc"]["within_W"]["auc"] or 0) >= 0.60
        Ora["verdict"] = ("killed" if killed else "premise holds (>= 0.75 overall, >= 0.60 within W on FRGC)" if holds else "inconclusive")
        Ora["adds_beyond_E_W"] = ("inconclusive (> 1% bootstrap failures)" if fail > 0.01 * B else
                                  "no (gain < +0.02)" if g[0] < 0.02 else "yes (gain >= +0.03, lower bound > 0)" if g[0] >= 0.03 and ci[0] > 0 else "inconclusive")
        out["oracle"] = Ora
    if a.part in ("single", "all"):
        S = {}
        e4, e3 = ech["S4"], ech["S3"]
        S["S4_vs_S3"] = dict(auc=auc(e4, e3), within_D=strat(e4, e3, D4, D3), pure_D_reference=strat_auc(D4, D3, D4, D3)[0],
                             within_W=strat(e4, e3, np.exp(W4), np.exp(W3)), within_E=strat(e4, e3, np.exp(E4), np.exp(E3)))
        S["R4_vs_R3_within_D"] = strat(ech["R4"], ech["R3"], D4, D3)
        ctrl = {k: auc(ech[x], ech[y]) for k, (x, y) in dict(R0_61_vs_R0=("R0_61", "R0"), R2w4_vs_R0=("R2w4", "R0"),
                                                               S0_vs_R2w4=("S0", "R2w4"), R2w4_vs_R2w=("R2w4", "R2w")).items()}
        ctrl["S0_vs_R0_printed"] = auc(ech["S0"], ech["R0"])
        ctrl["border"] = "not controlled (no clean border-blanked set among these rows)"
        S["controls"] = ctrl
        bad = [k for k in ("R0_61_vs_R0", "R2w4_vs_R0", "S0_vs_R2w4", "R2w4_vs_R2w") if not (0.42 <= ctrl[k] <= 0.58)]
        S["controls_bad"] = bad
        cs = np.load(CUE_SPL)
        C = {str(i): c for i, c in zip(cs["ids"], cs["cues"])}
        zt, zr = np.load(TONE), np.load(RATIO)
        tone = {str(i): v for i, v in zip(zt["ids"], zt["tone"])}
        rat = {str(i): float(v) for i, v in zip(zr["ids"], zr["ratio"])}
        sc = lambda i: np.r_[C[i], tone[i], np.log(rat[i] + 1e-6)]      # noqa: E731
        X4 = np.array([sc(r["S4_id"]) for r in R])
        X3 = np.array([sc(r["S3_id"]) for r in R])
        if a.mock:
            rng = np.random.default_rng(12)
            X4, X3 = rng.normal(size=X4.shape), rng.normal(size=X3.shape)
        g = gain(X4, X3, e4[:, None], e3[:, None])
        S["shortcut_gain"] = dict(gain=g[0], base=g[1], plus=g[2])
        S["floor_27stat_best_single"] = crossfit_best_single(X4[:, :27], X3[:, :27], hosts, hosts)
        per = {}
        for d_ in ("frgc", "feret"):
            m = db == d_
            per[d_] = dict(S4_vs_S3_within_D=strat(e4, e3, D4, D3, m), shortcut_gain=gain(X4, X3, e4[:, None], e3[:, None], m)[0],
                           controls={k: auc(ech[x][m], ech[y][m]) for k, (x, y) in dict(R0_61_vs_R0=("R0_61", "R0"), R2w4_vs_R2w=("R2w4", "R2w"),
                                                                                         S0_vs_R2w4=("S0", "R2w4")).items()})
        S["per_database"] = per
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
            rec = {}
            for tag, m in (("all", None), ("test", role == "test")):
                rec[tag] = gain(l4[:, None], l3[:, None], e4[:, None], e3[:, None], m)[0]
            inc[str(s)] = rec
        S["sb_increment"] = inc
        ninc = sum(v["all"] >= 0.03 for v in inc.values())
        wd = S["S4_vs_S3"]["within_D"]["auc"]
        if bad:
            S["verdict"] = f"killed: a control outside [0.42, 0.58] ({', '.join(bad)})"
        elif wd is not None and wd <= 0.60:
            S["verdict"] = "killed: S4 vs S3 within D <= 0.60"
        elif wd is not None and wd >= 0.65:
            S["verdict"] = "single image reads two superimposed shapes (>= 0.65 within D, controls in band)"
        else:
            S["verdict"] = "inconclusive"
        S["arm_condition"] = dict(sb_increment_seeds=ninc, shortcut_gain_ok=bool(g[0] >= 0.03),
                                  note="no arm before the look-alike set (LA1) exists, whatever the numbers")
        out["single"] = S
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=0, default=float)[:4000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

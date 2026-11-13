"""Texture band profile (TB1) reader, amendment 1 version (prereg.md; pre-run check 3f9f136, fixes T1-T5). Zero GPU.
Development data only. Parts: --part premise (may be read after amendment 1) | --part s (S4-vs-S3 and controls; waits
for ADVERSARY's floor commit, lead's hold) | --part all.
  python -I tb1_read.py --part premise --out tb1_premise.json
  python -I tb1_read.py --mock --ffile FILE --part all --out mock.json   (random features; no score tar opened)"""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
sys.path.insert(0, "/home/narolski/smad-next/src/RI1")
from bd1_read import auc, sha, strat_auc  # noqa: E402
from ri1_read import crossfit_auc, crossfit_best_single  # noqa: E402

FFILE = pathlib.Path("/mnt/t7/smad_next/TB1/tb1_feats.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
GF = pathlib.Path("/mnt/t7/smad_next/BD1/d_feats.csv")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
TONE = pathlib.Path("/mnt/t7/smad_next/PN1/cues/tone_splice.npz")
RATIO = pathlib.Path("/mnt/t7/smad_next/PN1/cues/ratio_splice.npz")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000


def folds_of(hosts, seed=20261171, folds=5):
    rng = np.random.default_rng(seed)
    return dict(zip(hosts, rng.permutation(len(hosts)) % folds))


def fold_models(Xp, Xn, hosts, f, folds=5):
    """S4-vs-S3 models per held-out fold (trained on the other folds' S4/S3 rows)"""
    from sklearn.linear_model import LogisticRegression
    g = np.array([f[h] for h in hosts])
    M = {}
    for k in range(folds):
        tr = g != k
        X = np.r_[Xp[tr], Xn[tr]]
        y = np.r_[np.ones(tr.sum()), np.zeros(tr.sum())]
        mu, sd = X.mean(0), X.std(0) + 1e-9
        M[k] = (LogisticRegression(C=1.0, max_iter=5000).fit((X - mu) / sd, y), mu, sd)
    return M, g


def score_oof(M, g, X):
    s = np.zeros(len(X))
    for k, (m, mu, sd) in M.items():
        te = g == k
        if te.any():
            s[te] = m.decision_function((X[te] - mu) / sd)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--part", choices=("premise", "s", "all"), required=True)
    ap.add_argument("--ffile", default=str(FFILE))
    a = ap.parse_args()
    if not a.mock:
        for f in (a.ffile, str(DF), str(GF)):
            assert sha(f) == pathlib.Path(f + ".sha256").read_text().split()[0]
    R = list(csv.DictReader(open(a.ffile)))
    if a.mock:
        rng = np.random.default_rng(3)
        for r in R:
            for k in list(r):
                if k[-1].isdigit() and ("_p" in k or "_r" in k):
                    r[k] = str(abs(rng.normal()) + 0.01)
    hosts = [r["host"] for r in R]
    f = folds_of(hosts)
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    for r in csv.DictReader(open(GF)):
        D[r["id"]].update(r)
    col = lambda pre, n: np.array([[float(r[f"{pre}_{n}{k}"]) for k in range(1, 6)] for r in R])   # noqa: E731
    dv = lambda img, key: np.array([float(D[r[f"{img}_id"]][key]) for r in R])                    # noqa: E731
    role = np.array([r["role"] for r in R])
    out = dict(mock=a.mock, part=a.part, n_hosts=len(R), by_db={d: sum(r["db"] == d for r in R) for d in ("frgc", "feret")})
    D4, D3 = dv("S4", "D"), dv("S3", "D")
    if a.part in ("premise", "all"):
        P = {}
        for tag, n in (("hull", "p"), ("hull_eroded16", "pe")):
            lp4, lp3 = np.log(col("P4", n) + 1e-12), np.log(col("P3", n) + 1e-12)
            M, g = fold_models(lp4, lp3, hosts, f)
            sp, sn = score_oof(M, g, lp4), score_oof(M, g, lp3)
            rec = dict(auc=auc(sp, sn))
            for key in ("D", "D_lin", "D_dc", "G"):
                x4, x3 = dv("S4", key) + 1e-9, dv("S3", key) + 1e-9
                sa, cov, _ = strat_auc(sp, sn, x4, x3)
                rec[f"within_{key}"] = dict(auc=sa, cover=cov, pure_reference=strat_auc(x4, x3, x4, x3)[0])
            if tag == "hull":
                rr = np.random.default_rng(20261172)
                bs = []
                for _ in range(B):
                    ix = rr.integers(0, len(R), len(R))
                    v = strat_auc(sp[ix], sn[ix], D4[ix], D3[ix])[0]
                    if v is not None:
                        bs.append(v)
                rec["within_D_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
                for db in ("frgc", "feret"):
                    m = np.array([r["db"] == db for r in R])
                    rec[f"auc_{db}"] = auc(sp[m], sn[m])
                G4 = dv("S4", "G")
                t = np.quantile(np.r_[D4, D3], [1 / 3, 2 / 3])
                joint = []
                for lo, hi in ((-np.inf, t[0]), (t[0], t[1]), (t[1], np.inf)):
                    for gm in (G4 <= np.median(G4), G4 > np.median(G4)):
                        pm, nm = (D4 > lo) & (D4 <= hi) & gm, (D3 > lo) & (D3 <= hi) & gm
                        if pm.sum() >= 10 and nm.sum() >= 10:
                            joint.append(dict(n_pos=int(pm.sum()), n_neg=int(nm.sum()), auc=auc(sp[pm], sn[nm])))
                rec["joint_DxG_strata"] = joint
            P[tag] = rec
        pD = P["hull"]["within_D"]["auc"]
        P["verdict"] = ("premise holds (>= 0.70 within D)" if pD is not None and pD >= 0.70 else
                        "no band-profile difference of the luminance half-difference in AS0's five octave bands at equal D; other texture statistics are not tested"
                        if pD is not None and pD <= 0.62 else "inconclusive")
        out["P"] = P
    if a.part in ("s", "all"):
        S = {}
        r4, r3 = col("S4", "r"), col("S3", "r")
        M, g = fold_models(r4, r3, hosts, f)
        s4, s3 = score_oof(M, g, r4), score_oof(M, g, r3)
        sa, cov, _ = strat_auc(s4, s3, D4, D3)
        S["S4_vs_S3"] = dict(auc=auc(s4, s3), within_D=sa, cover=cov)
        G4, G3 = dv("S4", "G") + 1e-9, dv("S3", "G") + 1e-9
        S["S4_vs_S3_within_G"] = strat_auc(s4, s3, G4, G3)[0]
        zt = np.load(TONE)
        tone = {str(i): v for i, v in zip(zt["ids"], zt["tone"])}
        t4 = np.array([abs(tone[r["S4_id"]][0]) for r in R])
        t3 = np.array([abs(tone[r["S3_id"]][0]) for r in R])
        S["S4_vs_S3_within_seam_tone"] = strat_auc(s4, s3, t4 + 1e-9, t3 + 1e-9)[0]
        rg4, rg3 = col("S4", "rg"), col("S3", "rg")
        Mg, gg = fold_models(rg4, rg3, hosts, f)
        S["guard_band_S4_vs_S3_within_D"] = strat_auc(score_oof(Mg, gg, rg4), score_oof(Mg, gg, rg3), D4, D3)[0]
        # T1: controls scored by the S4-vs-S3 fold models (binding), refitted ceilings printed
        ctrl = {}
        for name, (pa, pb, binding) in dict(R0_61_vs_R0=("R0_61", "R0", True), R2w4_vs_R2w=("R2w4", "R2w", True),
                                            S0_vs_R2w4=("S0", "R2w4", True), S0_vs_R0=("S0", "R0", False),
                                            R2w4_vs_R0=("R2w4", "R0", False)).items():
            xa, xb = col(pa, "r"), col(pb, "r")
            v = auc(score_oof(M, g, xa), score_oof(M, g, xb))
            ceil = crossfit_auc(xa, xb, hosts)
            ctrl[name] = dict(auc_by_S4S3_model=v, refit_ceiling=ceil, binding=binding)
        S["controls"] = ctrl
        bad = [k for k, v in ctrl.items() if v["binding"] and not (0.42 <= v["auc_by_S4S3_model"] <= 0.58)]
        S["controls_bad"] = bad
        # T4: binding shortcut gain and 27-statistic logistic baseline
        cs = np.load(CUE_SPL)
        C = {str(i): c for i, c in zip(cs["ids"], cs["cues"])}
        zr = np.load(RATIO)
        rat = {str(i): float(v) for i, v in zip(zr["ids"], zr["ratio"])}
        ok = [i for i, r in enumerate(R) if all(x in C and x in tone and x in rat for x in (r["S4_id"], r["S3_id"]))]
        hh = [hosts[i] for i in ok]
        sc = lambda i: np.r_[C[i], tone[i], np.log(rat[i] + 1e-6)]       # noqa: E731
        Xp = np.array([sc(R[i]["S4_id"]) for i in ok])
        Xn = np.array([sc(R[i]["S3_id"]) for i in ok])
        base27 = crossfit_auc(np.array([C[R[i]["S4_id"]] for i in ok]), np.array([C[R[i]["S3_id"]] for i in ok]), hh)
        base = crossfit_auc(Xp, Xn, hh)
        plus = crossfit_auc(np.c_[Xp, r4[ok]], np.c_[Xn, r3[ok]], hh)
        S["shortcut_gain"] = dict(baseline_27stat_logistic=base27, baseline_27_plus_splice=base, plus_r=plus, gain=plus - base)
        S["floor_27stat_best_single"] = crossfit_best_single(np.array([C[R[i]["S4_id"]] for i in ok]),
                                                             np.array([C[R[i]["S3_id"]] for i in ok]), hh, hh)
        inc = {}
        for s in range(403, 408):
            if a.mock:
                rr = np.random.default_rng(s)
                L = {r[f"{k}_id"]: float(rr.normal()) for r in R for k in ("S4", "S3")}
            else:
                t_ = FS / f"PN1_Sb_s{s}.tar"
                assert sha(t_) == pathlib.Path(str(t_) + ".sha256").read_text().split()[0]
                with tarfile.open(t_) as tf:
                    z = np.load(io.BytesIO(tf.extractfile(f"PN1_Sb_s{s}/scores_eval.npz").read()))
                L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            l4 = np.array([L[r["S4_id"]] for r in R])
            l3 = np.array([L[r["S3_id"]] for r in R])
            rec = {}
            for tag, m in (("all", np.ones(len(R), bool)), ("test", role == "test")):
                hm = [hosts[i] for i in np.where(m)[0]]
                a1 = crossfit_auc(l4[m][:, None], l3[m][:, None], hm)
                a2 = crossfit_auc(np.c_[l4[m], r4[m]], np.c_[l3[m], r3[m]], hm)
                rec[tag] = dict(sb=a1, sb_plus_r=a2, gain=a2 - a1)
            inc[str(s)] = rec
        S["increment"] = inc
        out["S"] = S
    if a.part == "all":
        pD, sD = out["P"]["hull"]["within_D"]["auc"], out["S"]["S4_vs_S3"]["within_D"]
        bad = out["S"]["controls_bad"]
        ninc = sum(v["all"]["gain"] >= 0.03 for v in out["S"]["increment"].values())
        gain = out["S"]["shortcut_gain"]["gain"]
        if bad:
            reading = f"storage, seam or warp reads as the trace ({', '.join(bad)} outside [0.42, 0.58])"
        elif pD is not None and pD >= 0.70 and sD is not None and sD >= 0.65:
            arm = ninc >= 4 and gain >= 0.03
            reading = "a two-person texture trace exists and one image shows it" + (
                "; arm condition met (Sb increment >= +0.03 on >= 4 of 5 seeds and shortcut gain >= +0.03)" if arm else "; arm condition not met")
        elif pD is not None and pD >= 0.70:
            reading = "the trace exists but is too weak or masked in the composite"
        elif pD is not None and pD <= 0.62:
            reading = ("no band-profile difference of the luminance half-difference in AS0's five octave bands at equal D; "
                       "other texture statistics are not tested")
        else:
            reading = "inconclusive (no row of the outcome table)"
        out["outcome"] = dict(P_within_D=pD, S_within_D=sD, controls_bad=bad, n_seeds_gain=ninc, shortcut_gain=gain, reading=reading)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=0, default=float)[:6000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

"""Texture band profile (TB1) reader (experiments/TB1_texture-band-profile/prereg.md). Zero GPU. Development data only.
  python -I tb1_read.py --out tb1_read.json
  python -I tb1_read.py --mock --ffile FILE --out mock.json   (random features over the true hosts; no score tar opened)"""
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
from ri1_read import crossfit_best_single  # noqa: E402

FFILE = pathlib.Path("/mnt/t7/smad_next/TB1/tb1_feats.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
GF = pathlib.Path("/mnt/t7/smad_next/BD1/d_feats.csv")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000


def oof(Xp, Xn, hosts, seed=20261171, folds=5):
    """host-grouped cross-fitted logistic scores; S4/S3 rows of one host share a fold"""
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed)
    f = dict(zip(hosts, rng.permutation(len(hosts)) % folds))
    g = np.array([f[h] for h in hosts] * 2)
    X = np.r_[Xp, Xn]
    y = np.r_[np.ones(len(Xp)), np.zeros(len(Xn))]
    s = np.zeros(len(y))
    for k in range(folds):
        tr, te = g != k, g == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=2000).fit((X[tr] - mu) / sd, y[tr])
        s[te] = m.decision_function((X[te] - mu) / sd)
    return s[: len(Xp)], s[len(Xp):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
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
                if k[-2:-1] in ("p", "r") and k[-1].isdigit():
                    r[k] = str(abs(rng.normal()) + 0.01)
    hosts = [r["host"] for r in R]
    D = {r["id"]: r for r in csv.DictReader(open(DF))}
    for r in csv.DictReader(open(GF)):
        D[r["id"]].update(r)
    col = lambda pre, n: np.array([[float(r[f"{pre}_{n}{k}"]) for k in range(1, 6)] for r in R])   # noqa: E731
    dvals = lambda img, key: np.array([float(D[r[f"{img}_id"]][key]) for r in R])                # noqa: E731
    out = dict(mock=a.mock, n_hosts=len(R), by_db={d: sum(r["db"] == d for r in R) for d in ("frgc", "feret")})
    # ---------------- P (premise): profile of the half-difference, two-person against same-person
    lp4, lp3 = np.log(col("P4", "p") + 1e-12), np.log(col("P3", "p") + 1e-12)
    sp, sn = oof(lp4, lp3, hosts)
    D4, D3 = dvals("S4", "D"), dvals("S3", "D")
    P = dict(auc=auc(sp, sn))
    for key in ("D", "D_lin", "G"):
        x4, x3 = dvals("S4", key), dvals("S3", key)
        sa, cov, _ = strat_auc(sp, sn, x4 + 1e-9, x3 + 1e-9)
        P[f"within_{key}"] = dict(auc=sa, cover=cov, pure_reference=strat_auc(x4 + 1e-9, x3 + 1e-9, x4 + 1e-9, x3 + 1e-9)[0])
    rng = np.random.default_rng(20261172)
    bs = []
    for _ in range(B):
        ix = rng.integers(0, len(R), len(R))
        v = strat_auc(sp[ix], sn[ix], D4[ix], D3[ix])[0]
        if v is not None:
            bs.append(v)
    P["within_D_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    for db in ("frgc", "feret"):
        m = np.array([r["db"] == db for r in R])
        P[f"auc_{db}"] = auc(sp[m], sn[m]) if m.sum() else None
    G4 = dvals("S4", "G")
    t = np.quantile(D4.tolist() + D3.tolist(), [1 / 3, 2 / 3])
    joint = []
    for lo, hi in ((-np.inf, t[0]), (t[0], t[1]), (t[1], np.inf)):
        for gm in (G4 <= np.median(G4), G4 > np.median(G4)):
            pm, nm = (D4 > lo) & (D4 <= hi) & gm, (D3 > lo) & (D3 <= hi) & gm
            if pm.sum() >= 10 and nm.sum() >= 10:
                joint.append(dict(n_pos=int(pm.sum()), n_neg=int(nm.sum()), auc=auc(sp[pm], sn[nm])))
    P["joint_DxG_strata"] = joint
    out["P"] = P
    # ---------------- S (single image): r profile, S4 vs S3 within D; controls
    S = {}
    s4, s3 = oof(col("S4", "r"), col("S3", "r"), hosts)
    sa, cov, _ = strat_auc(s4, s3, D4, D3)
    S["S4_vs_S3"] = dict(auc=auc(s4, s3), within_D=sa, cover=cov)
    for name, (pa, pb) in dict(R0_61_vs_R0=("R0_61", "R0"), S0_vs_R0=("S0", "R0"), R2w4_vs_R0=("R2w4", "R0")).items():
        x, y = oof(col(pa, "r"), col(pb, "r"), hosts)
        S[name] = auc(x, y)
    out["S"] = S
    cs = np.load(CUE_SPL)
    C = {str(i): c for i, c in zip(cs["ids"], cs["cues"])}
    ok = [i for i, r in enumerate(R) if r["S4_id"] in C and r["S3_id"] in C]
    out["floor_27stat_S4_vs_S3"] = crossfit_best_single(np.array([C[R[i]["S4_id"]] for i in ok]),
                                                        np.array([C[R[i]["S3_id"]] for i in ok]),
                                                        [hosts[i] for i in ok], [hosts[i] for i in ok])
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
        a1 = auc(*oof(l4[:, None], l3[:, None], hosts))
        a2 = auc(*oof(np.c_[l4, col("S4", "r")], np.c_[l3, col("S3", "r")], hosts))
        inc[str(s)] = dict(sb=a1, sb_plus_r=a2, gain=a2 - a1)
    out["increment"] = inc
    ninc = sum(v["gain"] >= 0.03 for v in inc.values())
    pD, sD = P["within_D"]["auc"], S["S4_vs_S3"]["within_D"]
    bad = [k for k in ("R0_61_vs_R0", "S0_vs_R0", "R2w4_vs_R0") if S[k] > 0.58]
    if bad:
        reading = f"storage, seam or warp reads as the trace ({', '.join(bad)} > 0.58)"
    elif pD is not None and pD >= 0.70 and sD is not None and sD >= 0.65:
        reading = "a two-person texture trace exists and one image shows it" + (
            "; increment >= +0.03 on >= 4 of 5 seeds" if ninc >= 4 else "; increment not met")
    elif pD is not None and pD >= 0.70:
        reading = "the trace exists but is too weak or masked in the composite"
    elif pD is not None and pD <= 0.62:
        reading = "no texture-level second-identity trace beyond blend energy"
    else:
        reading = "inconclusive (no row of the outcome table)"
    out["outcome"] = dict(P_within_D=pD, S_within_D=sD, controls_over_058=bad, n_seeds_gain=ninc, reading=reading)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=0, default=float))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

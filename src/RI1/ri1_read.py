"""Regional identity disagreement (RI1) reader (experiments/RI1_regional-identity-disagreement/prereg.md). Zero GPU.
Reads the RI1 embeddings (ri1_embed.py), the AR1 pool, BD1's D values, the 27-statistic cue files and Sb's stored
development scores (FS1 seeds 403-407). Development data only.
  python -I ri1_read.py --out ri1_read.json
  python -I ri1_read.py --mock --out mock.json      (random embeddings over the true ids; no score tar opened)"""
import argparse
import csv
import glob
import io
import json
import pathlib
import sys
import tarfile

import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
from bd1_read import auc, sha, strat_auc  # noqa: E402

EMB = pathlib.Path("/mnt/t7/smad_next/RI1")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
CUE_LAD = pathlib.Path("/mnt/t7/smad_next/AF0/cues/ar1.npz")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000


def load_emb(part, mock, ids_wanted=None):
    E, F = {}, {}
    for f in sorted(glob.glob(str(EMB / f"emb_{part}_*of*.npz"))):
        if "limit" in f:
            continue
        z = np.load(f)
        for i, e, ok in zip(z["ids"].tolist(), z["emb"], z["found"]):
            E[i], F[i] = e, bool(ok)
    if mock:
        rng = np.random.default_rng(1)
        for i in ids_wanted:
            e = rng.normal(size=(9, 512)).astype(np.float32)
            E[i] = e / np.linalg.norm(e, axis=1, keepdims=True)
            F[i] = True
    return E, F


def boot(fn, units, seed=20261161):
    rng = np.random.default_rng(seed)
    u = np.array(units)
    v = []
    for _ in range(B):
        x = fn(rng.integers(0, len(u), len(u)))
        if x is not None:
            v.append(x)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def crossfit_best_single(Xp, Xn, hp, hn, seed=20261162):
    """best of the 27 statistics chosen on one host half (direction-free), scored on the other; mean of both halves"""
    hs = sorted(set(hp) | set(hn))
    rng = np.random.default_rng(seed)
    half = dict(zip(hs, rng.permutation(len(hs)) % 2))
    gp, gn = np.array([half[h] for h in hp]), np.array([half[h] for h in hn])
    out = []
    for fit in (0, 1):
        a = [auc(Xp[gp == fit, j], Xn[gn == fit, j]) for j in range(Xp.shape[1])]
        j = int(np.argmax([max(x, 1 - x) for x in a]))
        sgn = 1 if a[j] >= 0.5 else -1
        out.append(auc(sgn * Xp[gp != fit, j], sgn * Xn[gn != fit, j]))
    return float(np.mean(out))


def crossfit_gain(sp, sn, dp, dn, hp, hn, seed=20261163, folds=5):
    from sklearn.linear_model import LogisticRegression
    hs = sorted(set(hp) | set(hn))
    rng = np.random.default_rng(seed)
    f = dict(zip(hs, rng.permutation(len(hs)) % folds))
    g = np.array([f[h] for h in list(hp) + list(hn)])
    y = np.r_[np.ones(len(sp)), np.zeros(len(sn))]
    X1 = np.r_[sp, sn][:, None]
    X2 = np.c_[np.r_[sp, sn], np.r_[dp, dn]]
    res = []
    for X in (X1, X2):
        s = np.zeros(len(y))
        for k in range(folds):
            tr, te = g != k, g == k
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
            m = LogisticRegression(C=1.0, max_iter=2000).fit((X[tr] - mu) / sd, y[tr])
            s[te] = m.decision_function((X[te] - mu) / sd)
        res.append(auc(s[: len(sp)], s[len(sp):]))
    return res[1] - res[0], res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    man = {r["id"]: r for r in csv.DictReader(open(MAN))}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rows_ids = [i for i, r in man.items() if r["role"] in ("dev", "test") and (
        (r["fam"] == "ladder" and r["rung"] in ("R0", "R2w4", "R3", "R4") and (r["strength"] == "" or (r["rung"] == "R0" and r["strength"] == "61")))
        or (r["fam"] == "splice" and r["rung"] in ("S0", "S3", "S4")))]
    E, Fd = load_emb("rows", a.mock, rows_ids)
    hosts = sorted({man[i]["host"] for i in rows_ids})
    src_paths = sorted({pool[h][k] for h in hosts for k in ("H", "S", "B", "R") if pool[h][k]})
    Es, Fs = load_emb("sources", a.mock, src_paths)
    ffhq_ids = sorted([i for i, r in man.items() if r["rung"] == "ffhq_bona_orig"])[:1000]
    Ef, Ff = load_emb("ffhq", a.mock, ffhq_ids)
    out = dict(mock=a.mock, n=dict(rows=len(rows_ids), rows_found=int(sum(Fd.get(i, False) for i in rows_ids)),
                                   sources=len(src_paths), sources_found=int(sum(Fs.get(p, False) for p in src_paths)),
                                   ffhq_found=int(sum(Ff.get(i, False) for i in ffhq_ids))))

    def pick(rung, tool="opencv", strength=""):
        d = {}
        for i in rows_ids:
            r = man[i]
            if r["rung"] == rung and (r["fam"] == "splice" or (r["tool"] in (tool, "none") and r["strength"] == strength)) and Fd.get(i):
                d[r["host"]] = i
        return d
    R0, R061, R2w4, R3, R4 = pick("R0"), pick("R0", strength="61"), pick("R2w4"), pick("R3"), pick("R4")
    R3f, R4f, R2w4f = pick("R3", "facemorpher"), pick("R4", "facemorpher"), pick("R2w4", "facemorpher")
    S0, S3, S4 = pick("S0"), pick("S3"), pick("S4")
    # ---------------- G0: occluded R0 embeddings against the host's independent photo R
    K = 8
    g0 = {}
    hs_r = [h for h in hosts if h in R0 and pool[h]["R"] and Fs.get(pool[h]["R"])]
    for k in range(K + 1):
        gen, imp = [], []
        for h in hs_r:
            ek = E[R0[h]][k]
            gen.append(float(ek @ Es[pool[h]["R"]][0]))
            for g in hs_r:
                if g != h and pool[g]["db"] == pool[h]["db"]:
                    imp.append(float(ek @ Es[pool[g]["R"]][0]))
        g0[k] = auc(gen, imp)
    kept = [k for k in range(1, K + 1) if g0[k] >= 0.90]
    if a.mock:
        kept = list(range(1, K + 1))                 # mock only: random embeddings cannot pass G0; tests the code path
    out["G0"] = dict(auc={str(k): g0[k] for k in g0}, kept=kept, n_hosts=len(hs_r),
                     verdict="pass" if len(kept) >= 5 else "stop: face-recognition regions too weak to test")
    if len(kept) < 5:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
        print(json.dumps(out["G0"]))
        return
    kk = np.array(kept)
    # ---------------- P1 (oracle leaning spread)
    def V(i, sa, sb, divide=True):
        e = E[i]
        L = e @ Es[sa][0] - e @ Es[sb][0]                       # 9 values
        x = float(np.std(L[kk] - L[0]))
        if divide:
            x /= float(np.mean([1 - e[0] @ Es[sa][0], 1 - e[0] @ Es[sb][0]]))
        return x
    P = {}
    hp1 = [h for h in hosts if h in R4 and h in R3 and all(Fs.get(pool[h][k]) for k in ("H", "S", "B"))]
    for tag, fa in (("H", "H"), ("R", "R")):
        hs_ = [h for h in hp1 if pool[h][fa] and Fs.get(pool[h][fa])]
        for div in (True, False):
            v4 = np.array([V(R4[h], pool[h][fa], pool[h]["B"], div) for h in hs_])
            v3 = np.array([V(R3[h], pool[h][fa], pool[h]["S"], div) for h in hs_])
            A = auc(v4, v3)
            P[f"{tag}_{'div' if div else 'nodiv'}"] = dict(auc=A, n=len(hs_),
                                                           ci=boot(lambda ix: auc(v4[ix], v3[ix]), hs_))
    out["P1"] = P
    p1 = P["H_div"]["auc"]
    p1lo = P["H_div"]["ci"][0]
    out["P1_verdict"] = "pass" if (p1 >= 0.70 and p1lo > 0.62) else ("kill" if p1 <= 0.60 else "inconclusive")
    # ---------------- S1 dispersion
    pairs = [(j, k) for ji, j in enumerate(kept) for k in kept[ji + 1:]]

    def disp(e):
        return float(np.mean([1 - e[j] @ e[k] for j, k in pairs]))
    fz = np.array([disp(Ef[i]) for i in ffhq_ids if Ff.get(i)])
    mu, sd = float(fz.mean()), float(fz.std())
    dz = lambda i: (disp(E[i]) - mu) / sd                      # noqa: E731

    def contrast(A_, B_, paired=True):
        hs_ = sorted(set(A_) & set(B_)) if paired else None
        x = np.array([dz(A_[h]) for h in hs_])
        y = np.array([dz(B_[h]) for h in hs_])
        return dict(auc=auc(x, y), n=len(hs_), ci=boot(lambda ix: auc(x[ix], y[ix]), hs_)), hs_, x, y
    S = {}
    for name, (A_, B_) in dict(R4_vs_R3=(R4, R3), S4_vs_S3=(S4, S3), R4_vs_R0=(R4, R0),
                               R061_vs_R0=(R061, R0), R2w4_vs_R0=(R2w4, R0), S0_vs_R0=(S0, R0), R3_vs_R0=(R3, R0),
                               fm_R4_vs_R3=(R4f, R3f), fm_R2w4_vs_R0=(R2w4f, R0)).items():
        S[name] = contrast(A_, B_)[0]
    D = {r["id"]: float(r["D"]) for r in csv.DictReader(open(DF))}
    hs_s = sorted(set(S4) & set(S3))
    x4 = np.array([dz(S4[h]) for h in hs_s])
    x3 = np.array([dz(S3[h]) for h in hs_s])
    d4, d3 = np.array([D[S4[h]] for h in hs_s]), np.array([D[S3[h]] for h in hs_s])
    sa, cov, _ = strat_auc(x4, x3, d4, d3)
    ref = strat_auc(d4, d3, d4, d3)[0]
    S["S4_vs_S3_within_D"] = dict(auc=sa, cover=cov, pure_D_reference=ref)
    out["S1"] = S
    out["ffhq_ref"] = dict(mean=mu, sd=sd, n=int(len(fz)))
    sig = S["R4_vs_R3"]["auc"] >= 0.65 and (sa is not None and sa >= 0.65)
    ctrl_bad = [n for n in ("R061_vs_R0", "R2w4_vs_R0", "S0_vs_R0") if S[n]["auc"] > 0.60]
    # ---------------- floors (27 statistics, cross-fitted by host halves) and Sb increment
    cl, cs = np.load(CUE_LAD), np.load(CUE_SPL)
    C = {str(i): c for i, c in zip(cl["ids"], cl["cues"])}
    C.update({str(i): c for i, c in zip(cs["ids"], cs["cues"])})
    fl = {}
    for name, (A_, B_) in dict(R4_vs_R3=(R4, R3), S4_vs_S3=(S4, S3), R4_vs_R0=(R4, R0)).items():
        hs_ = [h for h in sorted(set(A_) & set(B_)) if A_[h] in C and B_[h] in C]
        fl[name] = dict(floor=crossfit_best_single(np.array([C[A_[h]] for h in hs_]), np.array([C[B_[h]] for h in hs_]), hs_, hs_),
                        n=len(hs_))
    out["floors_27stat_crossfit"] = fl
    inc = {}
    for s in range(403, 408):
        if a.mock:
            rng = np.random.default_rng(s)
            L = {i: float(rng.normal()) for i in man}
        else:
            t = FS / f"PN1_Sb_s{s}.tar"
            assert sha(t) == pathlib.Path(str(t) + ".sha256").read_text().split()[0]
            with tarfile.open(t) as tf:
                z = np.load(io.BytesIO(tf.extractfile(f"PN1_Sb_s{s}/scores_eval.npz").read()))
            L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        sp, sn = np.array([L[S4[h]] for h in hs_s]), np.array([L[S3[h]] for h in hs_s])
        g, (a1, a2) = crossfit_gain(sp, sn, x4, x3, hs_s, hs_s)
        inc[str(s)] = dict(gain=g, auc_sb=a1, auc_sb_plus_disp=a2)
    out["increment_S4_vs_S3"] = inc
    ninc = sum(1 for v in inc.values() if v["gain"] >= 0.03)
    # ---------------- outcome table
    p1v = out["P1_verdict"]
    if ctrl_bad:
        reading = f"the statistic reads the nuisance ({', '.join(ctrl_bad)} > 0.60)"
    elif p1 >= 0.70 and sig:
        reading = "regional identity disagreement exists and is readable in one image" + (
            "; incremental gain >= +0.03 on >= 4 of 5 Sb seeds" if ninc >= 4 else "; incremental gain not met")
    elif p1 >= 0.70:
        reading = "the premise holds but glintr100 occlusions are too coarse to read it"
    elif p1 <= 0.60 and sa is not None and sa >= 0.65 and S["R4_vs_R3"]["auc"] < 0.60:
        reading = "splice-only mechanism (inner blend against outer host)"
    elif p1 <= 0.60 and S["R4_vs_R3"]["auc"] < 0.60 and (sa is None or sa < 0.60):
        reading = "no regional identity disagreement measurable"
    else:
        reading = "inconclusive (no row of the outcome table)"
    out["outcome"] = dict(P1=p1v, signal_met=bool(sig), controls_over_060=ctrl_bad, n_seeds_gain=ninc, reading=reading)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(n=out["n"], G0=out["G0"], P1=out["P1"], S1={k: round(v["auc"], 3) if v["auc"] is not None else None for k, v in S.items()},
                          floors=fl, increment=inc, outcome=out["outcome"]), indent=0, default=float))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

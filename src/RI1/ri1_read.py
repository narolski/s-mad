"""Regional identity disagreement (RI1) reader, amendment 1b version (prereg.md; pre-run check 3f9f136, fixes R1-R6).
Zero GPU. Reads the RI1 embeddings (ri1_embed.py), the AR1 pool, BD1's D values, the 27-statistic cue files, the PN1
splice shortcut features (seam tone luma and R-G step, inside/outside sharpness ratio) and Sb's stored development
scores (FS1 seeds 403-407). Development data only. The read waits for ADVERSARY's floor commit (lead's hold).
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
from scipy.stats import spearmanr

sys.path.insert(0, "/home/narolski/smad-next/src/BD1")
from bd1_read import auc, sha, strat_auc  # noqa: E402

EMB = pathlib.Path("/mnt/t7/smad_next/RI1")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
DF = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")
CUE_LAD = pathlib.Path("/mnt/t7/smad_next/AF0/cues/ar1.npz")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
TONE = pathlib.Path("/mnt/t7/smad_next/PN1/cues/tone_splice.npz")
RATIO = pathlib.Path("/mnt/t7/smad_next/PN1/cues/ratio_splice.npz")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
B = 2000


def load_emb(part, mock, ids_wanted=None):
    E, F = {}, {}
    if not mock:
        for f in sorted(glob.glob(str(EMB / f"emb_{part}_*of*.npz"))):
            if "limit" in f:
                continue
            z = np.load(f)
            for i, e, ok in zip(z["ids"].tolist(), z["emb"], z["found"]):
                E[i], F[i] = e, bool(ok)
    else:                                            # mock: random embeddings only, no real file opened
        rng = np.random.default_rng(1)
        for i in ids_wanted:
            e = rng.normal(size=(9, 512)).astype(np.float32)
            E[i] = e / np.linalg.norm(e, axis=1, keepdims=True)
            F[i] = True
    return E, F


def boot(fn, n, seed=20261161):
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(B):
        x = fn(rng.integers(0, n, n))
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


def crossfit_auc(Xp, Xn, hosts, seed=20261163, folds=5):
    """host-grouped cross-fitted standardised logistic; the two rows of a host share a fold"""
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed)
    f = dict(zip(sorted(set(hosts)), rng.permutation(len(set(hosts))) % folds))
    g = np.array([f[h] for h in hosts] * 2)
    X = np.r_[Xp, Xn]
    y = np.r_[np.ones(len(Xp)), np.zeros(len(Xn))]
    s = np.zeros(len(y))
    for k in range(folds):
        tr, te = g != k, g == k
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=5000).fit((X[tr] - mu) / sd, y[tr])
        s[te] = m.decision_function((X[te] - mu) / sd)
    return auc(s[: len(Xp)], s[len(Xp):])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    man = {r["id"]: r for r in csv.DictReader(open(MAN))}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL))}
    rows_ids = [i for i, r in man.items() if r["role"] in ("dev", "test") and (
        (r["fam"] == "ladder" and r["rung"] in ("R0", "R2w4", "R3", "R4") and (r["strength"] == "" or (r["rung"] == "R0" and r["strength"] == "61")))
        or (r["fam"] == "ladder" and r["rung"] == "R2w" and r["tool"] == "opencv" and r["strength"] == "")
        or (r["fam"] == "splice" and r["rung"] in ("S0", "S3", "S4")))]
    E, Fd = load_emb("rows", a.mock, rows_ids)
    hosts = sorted({man[i]["host"] for i in rows_ids})
    src_paths = sorted({pool[h][k] for h in hosts for k in ("H", "S", "B", "R") if pool[h][k]})
    Es, Fs = load_emb("sources", a.mock, src_paths)
    out = dict(mock=a.mock, n=dict(rows=len(rows_ids), rows_found=int(sum(Fd.get(i, False) for i in rows_ids)),
                                   sources=len(src_paths), sources_found=int(sum(Fs.get(p, False) for p in src_paths))))
    found_rate = {}

    def pick(rung, tool="opencv", strength=""):
        d, tot = {}, 0
        for i in rows_ids:
            r = man[i]
            if r["rung"] == rung and (r["fam"] == "splice" or (r["tool"] in (tool, "none") and r["strength"] == strength)):
                tot += 1
                if Fd.get(i):
                    d[r["host"]] = i
        found_rate[f"{rung}_{tool}_{strength}"] = len(d) / max(tot, 1)
        return d
    R0, R061, R2w, R2w4, R3, R4 = pick("R0"), pick("R0", strength="61"), pick("R2w"), pick("R2w4"), pick("R3"), pick("R4")
    R3f, R4f, R2w4f = pick("R3", "facemorpher"), pick("R4", "facemorpher"), pick("R2w4", "facemorpher")
    S0, S3, S4 = pick("S0"), pick("S3"), pick("S4")
    out["found_rate"] = found_rate
    measured = lambda *keys: all(found_rate[k] >= 0.95 for k in keys)   # noqa: E731   (R6 counting rule)
    # ---------------- G0
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
    D = {r["id"]: r for r in csv.DictReader(open(DF))}

    # ---------------- P1 (R1: projection statistic and validity gate)
    def u_of(sa, sb):
        d = Es[sa][0] - Es[sb][0]
        return d / np.linalg.norm(d)

    def Vproj(i, u):
        e = E[i]
        return float(np.std((e[kk] - e[0]) @ u))

    def Vold(i, sa, sb, divide):
        e = E[i]
        L = e @ Es[sa][0] - e @ Es[sb][0]
        x = float(np.std(L[kk] - L[0]))
        if divide:
            x /= float(np.mean([1 - e[0] @ Es[sa][0], 1 - e[0] @ Es[sb][0]]))
        return x
    hp1 = [h for h in hosts if h in R4 and h in R3 and h in R0 and h in R2w4 and all(Fs.get(pool[h][k]) for k in ("H", "S", "B"))]
    uHB = {h: u_of(pool[h]["H"], pool[h]["B"]) for h in hp1}
    uHS = {h: u_of(pool[h]["H"], pool[h]["S"]) for h in hp1}
    v4 = np.array([Vproj(R4[h], uHB[h]) for h in hp1])
    v3 = np.array([Vproj(R3[h], uHS[h]) for h in hp1])
    g_a = auc(np.array([Vproj(R0[h], uHB[h]) for h in hp1]), np.array([Vproj(R0[h], uHS[h]) for h in hp1]))
    g_b = auc(np.array([Vproj(R2w4[h], uHB[h]) for h in hp1]), np.array([Vproj(R0[h], uHS[h]) for h in hp1]))
    valid = 0.40 <= g_a <= 0.60 and 0.40 <= g_b <= 0.60
    p1 = auc(v4, v3)
    ci = boot(lambda ix: auc(v4[ix], v3[ix]), len(hp1))
    P = dict(auc=p1, ci=ci, n=len(hp1), validity=dict(R0_uHB_vs_R0_uHS=g_a, R2w4_uHB_vs_R0_uHS=g_b, valid=bool(valid)))
    P["printed_old_V"] = {}
    for t in ("H", "R"):
        hh = [h for h in hp1 if pool[h][t] and Fs.get(pool[h][t])]
        for dv in (True, False):
            P["printed_old_V"][f"{t}_{'div' if dv else 'nodiv'}"] = auc(
                np.array([Vold(R4[h], pool[h][t], pool[h]["B"], dv) for h in hh]),
                np.array([Vold(R3[h], pool[h][t], pool[h]["S"], dv) for h in hh]))
    cosHB = np.array([float(pool[h]["cos_HB"]) for h in hp1])
    cosHS = np.array([float(pool[h]["cos_HS"]) for h in hp1])
    P["rho_V_cosHB_R4"] = float(spearmanr(v4, cosHB).correlation)
    P["rho_V_cosHS_R3"] = float(spearmanr(v3, cosHS).correlation)
    # amendment 1c: G is one value per host (no per-class variation); the per-class geometry is W, the mean landmark
    # displacement over the 106 points between the two source photos (H-B for R4, H-S for R3), from the .tem files
    def tem(p):
        ls = open(p[:-4] + ".tem").read().splitlines()
        return np.array([list(map(float, ls[i].split())) for i in range(1, int(ls[0]) + 1)])
    W4 = np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["B"]), axis=1).mean() for h in hp1])
    W3 = np.array([np.linalg.norm(tem(pool[h]["H"]) - tem(pool[h]["S"]), axis=1).mean() for h in hp1])
    sw = strat_auc(v4, v3, W4, W3)
    P["within_W"] = dict(auc=sw[0], cover=sw[1])
    d4p = np.array([float(D[S4[h]]["D"]) for h in hp1]) if all(h in S4 for h in hp1) else None
    d3p = np.array([float(D[S3[h]]["D"]) for h in hp1]) if all(h in S3 for h in hp1) else None
    P["within_D"] = strat_auc(v4, v3, d4p, d3p)[0] if d4p is not None else None
    P["strata_vary_per_class"] = dict(W=bool(not np.allclose(W4, W3)), D=bool(d4p is not None and not np.allclose(d4p, d3p)))
    qs = np.quantile(cosHS, np.linspace(0, 1, 6))
    P["within_cosHS_quintiles_R3_vs_all_R4"] = [auc(v4, v3[(cosHS >= lo) & (cosHS <= hi)]) for lo, hi in zip(qs[:-1], qs[1:])]
    if not valid:
        p1v = "invalid (projection carries scale)"
    else:
        p1v = "pass" if (p1 >= 0.70 and ci[0] > 0.62) else ("kill" if p1 <= 0.60 else "inconclusive")
    P["verdict"] = p1v
    out["P1"] = P
    # ---------------- S1 dispersion (unstandardised; amendment 1a)
    pairs = [(j, k) for ji, j in enumerate(kept) for k in kept[ji + 1:]]
    disp = lambda i: float(np.mean([1 - E[i][j] @ E[i][k] for j, k in pairs]))   # noqa: E731

    def contrast(A_, B_):
        hs_ = sorted(set(A_) & set(B_))
        x, y = np.array([disp(A_[h]) for h in hs_]), np.array([disp(B_[h]) for h in hs_])
        return dict(auc=auc(x, y), n=len(hs_), ci=boot(lambda ix: auc(x[ix], y[ix]), len(hs_)))
    S = {}
    for name, (A_, B_, keys) in dict(
            R4_vs_R3=(R4, R3, ("R4_opencv_", "R3_opencv_")), S4_vs_S3=(S4, S3, ("S4_opencv_", "S3_opencv_")),
            R4_vs_R0=(R4, R0, ("R4_opencv_", "R0_opencv_")),
            R061_vs_R0=(R061, R0, ("R0_opencv_61", "R0_opencv_")), R2w4_vs_R0=(R2w4, R0, ("R2w4_opencv_", "R0_opencv_")),
            S0_vs_R2w4=(S0, R2w4, ("S0_opencv_", "R2w4_opencv_")), R2w4_vs_R2w=(R2w4, R2w, ("R2w4_opencv_", "R2w_opencv_")),
            S0_vs_R0=(S0, R0, ("S0_opencv_", "R0_opencv_")), R3_vs_R0=(R3, R0, ("R3_opencv_", "R0_opencv_")),
            fm_R4_vs_R3=(R4f, R3f, ("R4_facemorpher_", "R3_facemorpher_")),
            fm_R2w4_vs_R0=(R2w4f, R0, ("R2w4_facemorpher_", "R0_opencv_"))).items():
        S[name] = contrast(A_, B_) if measured(*keys) else dict(auc=None, note="not measured (< 95% found)")
    hs_s = sorted(set(S4) & set(S3) & set(R4) & set(R3))
    d4, d3 = np.array([float(D[S4[h]]["D"]) for h in hs_s]), np.array([float(D[S3[h]]["D"]) for h in hs_s])
    ref = strat_auc(d4, d3, d4, d3)[0]
    for name, (A_, B_) in dict(S4_vs_S3_within_D=(S4, S3), R4_vs_R3_within_D=(R4, R3)).items():
        x, y = np.array([disp(A_[h]) for h in hs_s]), np.array([disp(B_[h]) for h in hs_s])
        sa, cov, _ = strat_auc(x, y, d4, d3)
        S[name] = dict(auc=sa, cover=cov, pure_D_reference=ref)
    out["S1"] = S
    sig = all(S[k]["auc"] is not None and S[k]["auc"] >= 0.65 for k in ("R4_vs_R3_within_D", "S4_vs_S3_within_D"))
    ctrl_bad = [n for n in ("R061_vs_R0", "R2w4_vs_R0", "S0_vs_R2w4", "R2w4_vs_R2w")
                if S[n]["auc"] is None or abs(S[n]["auc"] - 0.5) > 0.10]
    # ---------------- floors, binding shortcut gain (R5), Sb increment
    cl, cs = np.load(CUE_LAD), np.load(CUE_SPL)
    C = {str(i): c for i, c in zip(cl["ids"], cl["cues"])}
    C.update({str(i): c for i, c in zip(cs["ids"], cs["cues"])})
    fl = {}
    for name, (A_, B_) in dict(R4_vs_R3=(R4, R3), S4_vs_S3=(S4, S3), R4_vs_R0=(R4, R0)).items():
        hs_ = [h for h in sorted(set(A_) & set(B_)) if A_[h] in C and B_[h] in C]
        fl[name] = dict(floor=crossfit_best_single(np.array([C[A_[h]] for h in hs_]), np.array([C[B_[h]] for h in hs_]), hs_, hs_), n=len(hs_))
    out["floors_27stat_crossfit"] = fl
    zt, zr = np.load(TONE), np.load(RATIO)
    tone = {str(i): v for i, v in zip(zt["ids"], zt["tone"])}
    rat = {str(i): float(v) for i, v in zip(zr["ids"], zr["ratio"])}
    hb = [h for h in hs_s if all(x in C and x in tone and x in rat for x in (S4[h], S3[h]))]
    sc = lambda i: np.r_[C[i], tone[i], np.log(rat[i] + 1e-6)]      # noqa: E731
    Xp, Xn = np.array([sc(S4[h]) for h in hb]), np.array([sc(S3[h]) for h in hb])
    dp, dn = np.array([disp(S4[h]) for h in hb]), np.array([disp(S3[h]) for h in hb])
    base = crossfit_auc(Xp, Xn, hb)
    plus = crossfit_auc(np.c_[Xp, dp], np.c_[Xn, dn], hb)
    out["shortcut_gain_S4_vs_S3"] = dict(baseline=base, plus_disp=plus, gain=plus - base, n=len(hb))
    inc = {}
    test_hosts = [h for h in hs_s if man[S4[h]]["role"] == "test"]
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
        rec = {}
        for tag, hh in (("all", hs_s), ("test", test_hosts)):
            sp, sn = np.array([L[S4[h]] for h in hh]), np.array([L[S3[h]] for h in hh])
            xp, xn = np.array([disp(S4[h]) for h in hh]), np.array([disp(S3[h]) for h in hh])
            a1 = crossfit_auc(sp[:, None], sn[:, None], hh)
            a2 = crossfit_auc(np.c_[sp, xp], np.c_[sn, xn], hh)
            rec[tag] = dict(sb=a1, sb_plus_disp=a2, gain=a2 - a1)
        inc[str(s)] = rec
    out["increment_S4_vs_S3"] = inc
    ninc = sum(1 for v in inc.values() if v["all"]["gain"] >= 0.03)
    # ---------------- outcome table (amendment 1b order: controls first)
    r43 = S["R4_vs_R3_within_D"]["auc"]
    s43 = S["S4_vs_S3_within_D"]["auc"]
    if ctrl_bad:
        reading = f"the statistic reads the nuisance ({', '.join(ctrl_bad)} outside [0.40, 0.60] or not measured)"
    elif p1v.startswith("invalid"):
        reading = "inconclusive: P1 invalid (projection carries scale)"
    elif p1v == "pass" and sig:
        arm = ninc >= 4 and out["shortcut_gain_S4_vs_S3"]["gain"] >= 0.03
        reading = "regional identity disagreement exists and is readable in one image" + (
            "; arm condition met (Sb increment >= +0.03 on >= 4 of 5 seeds and shortcut gain >= +0.03)" if arm else "; arm condition not met")
    elif p1v == "pass":
        reading = "the premise holds but glintr100 occlusions are too coarse to read it"
    elif p1v == "kill" and r43 is not None and r43 >= 0.65:
        reading = "Δ reads something other than regional identity leaning; closed"
    elif p1v == "kill" and s43 is not None and s43 >= 0.65 and r43 is not None and r43 < 0.60:
        reading = "splice-only mechanism (inner blend against outer host)"
    elif p1v == "kill" and (r43 is None or r43 < 0.60) and (s43 is None or s43 < 0.60):
        reading = "no regional identity disagreement measurable"
    else:
        reading = "inconclusive (no row of the outcome table)"
    out["outcome"] = dict(P1=p1v, signal_met=bool(sig), controls_bad=ctrl_bad, n_seeds_gain=ninc,
                          shortcut_gain=out["shortcut_gain_S4_vs_S3"]["gain"], reading=reading)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(n=out["n"], G0=out["G0"]["verdict"], P1=dict(auc=p1, ci=ci, validity=P["validity"], verdict=p1v),
                          S1={k: (round(v["auc"], 3) if v.get("auc") is not None else None) for k, v in S.items()},
                          floors=fl, shortcut_gain=out["shortcut_gain_S4_vs_S3"], outcome=out["outcome"]), indent=0, default=float))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()

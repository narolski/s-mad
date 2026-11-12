"""AG1 / AG2 / AG3 reader (CPU). Prepared before any image or score exists; the registered rules are in
experiments/AG1/prereg.md (including its amendment 1, the pre-run review fixes). Reads only manifests/ag1.csv, the
shard log.csv files, photos.json, the oracle embeddings, rt_check.json and the AG1 score files.

Two stages, in this order:
  gates   (--gate-only stops here; its gates.json is committed before any score file is opened)
          G-b per generator and pool, the RT determinism check, aligned-flag rates, latent distance per rung.
  scores  ladder contrasts, shares, verdicts under reading A and reading B, side readings, matched bins, session-gap
          sensitivity, AG2 (bridge-gated), AG3 / AG3T dose curves with achieved dose, benchmark-threshold flag rates,
          G-a, one-sided p-values and Holm over this experiment's primary cells.
Pools: frll (benchmark-linked, descriptive), primary = feret + frgc pooled (the primary cells), feret and frgc alone
(descriptive). One bootstrap draw per pool (seed depends on the pool name), shared by all contrasts and releases.
Statistics: AUC (Mann-Whitney, ties one half); 95% intervals by the two-way (dyadic) person bootstrap of a41_read.py
(class Draw, copied), B = 10,000; weighted AUC = a36_read.wauc (copied); d' = sqrt(2) Phi^-1(AUC); share of a step =
d'(step) / d'(R0 vs R4). Folded interval of an AUC with interval [lo, hi]: upper bound max(hi, 1 - lo).
Usage: ag1_read.py --data DIR [--scores DIR] [--logs DIR] --photos photos.json --out DIR [--gate-only]
       [--published-eer FILE] [--boot 10000] [--synthetic]
"""
import argparse
import csv
import datetime
import json
import pathlib
import sys
import zlib

import numpy as np

B_DEC = 10000
SEED = 20261111
RELEASES = ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own", "selfmad_hrnet_w18__rel")
PRIMARY_RELEASES = ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own")   # amendment 3, rule 3
SINGLE_SUBJECT = ("R2", "R2i", "R2s", "R3", "R3m", "RT")                                # amendment 3, rule 1
SCALAR_BASELINES = ("bytes", "lapvar", "hfband", "sym")
NOT_SCORED = ("mixfacenet_mad_smdd",)  # no AG1 scorer yet (a46_rgb_score is bound to the A46 plan)
POOLS = {"frll": ("frll",), "primary": ("feret", "frgc"), "feret": ("feret",), "frgc": ("frgc",)}
THR_A23 = 0.239399


# ------------------------------------------------------------------------------------- copied statistics (a41_read)
class Draw:
    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, pa, pb):
        a = np.array([self.pos[p] for p in pa])
        b = np.array([self.pos[p] for p in pb])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        if same.any():
            w[:, same] = self.C[:, a[same]]
        return w


def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    num = (wp * (below + 0.5 * tie)).sum(1)
    return num / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def auc(pos, neg):
    return float(wauc(np.asarray(pos, float), np.asarray(neg, float), np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


def dprime(a):
    from scipy.stats import norm
    return float(np.sqrt(2) * norm.ppf(np.clip(a, 0.005, 0.995)))


def ci(rep):
    rep = np.asarray(rep, float)
    rep = rep[np.isfinite(rep)]
    return [float(x) for x in np.percentile(rep, [2.5, 97.5])] if len(rep) else [None, None]


def eer_thr(b, m):
    b, m = np.sort(np.asarray(b, float)), np.sort(np.asarray(m, float))
    t = np.concatenate([b, m])
    fpr = 1 - np.searchsorted(b, t, "left") / len(b)
    fnr = np.searchsorted(m, t, "left") / len(m)
    i = int(np.argmin(np.abs(fnr - fpr)))
    return float(t[i]), float((fnr[i] + fpr[i]) / 2)


def exact(k, n):
    from scipy.stats import beta
    if n == 0:
        return [None, None, None]
    lo = beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return [k / n, float(lo), float(hi)]


def holm(p):
    """Holm step-down adjusted p-values for a dict name -> p."""
    keys = sorted(p, key=lambda k: p[k])
    m, run, out = len(keys), 0.0, {}
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * p[k]))
        out[k] = run
    return out


# ------------------------------------------------------------------------------------- registered readings
def fold(a):
    return max(a, 1 - a)


def folded_chance(a, lo, hi):
    return fold(a) < 0.60 and max(hi, 1 - lo) < 0.65


def verdict_A(a, lo, hi, share02, share02_lo):
    """reading A (11_AUDIT_PLAN): R2 is a processed genuine image; R0 -> R2 is a benchmark cue."""
    if a >= 0.75 and lo > 0.65 and share02 is not None and share02 <= 0.2:
        return "reads morphing"
    if (share02_lo is not None and share02_lo >= 0.5) or folded_chance(a, lo, hi):
        return "reads the benchmark"
    return "mixed"


def verdict_B(a, lo, hi):
    """reading B (author's position of 11 Nov, 16:00): R0 -> R2 is generated-image detection, not penalised; the
    morph question is decided on R2 vs R4 alone (R3 vs R4 is the identity side reading)."""
    if a >= 0.75 and lo > 0.65:
        return "reads morphing"
    if folded_chance(a, lo, hi):
        return "does not read morphing"
    return "mixed"


def side_verdict(a, lo, hi):
    if folded_chance(a, lo, hi):
        return "no identity reading"
    if a < 0.40 and hi < 0.5:
        return "twin artefact, cell invalid"
    if a >= 0.75 and lo > 0.65:
        return "identity reading"
    return "mixed"


def ag2_verdict(a_cam, a_r2, lo, hi, bridge):
    if bridge is None or not (0.40 <= bridge <= 0.60):
        return "implementation-confounded (bridge AUC outside 0.40-0.60)"
    if a_r2 < 0.40 and hi < 0.5:
        return "reverses: the cell measured generator output vs camera"
    if folded_chance(a_r2, lo, hi):
        return "collapses to chance: the cell measured generator output vs camera"
    if a_r2 >= 0.75 and lo > 0.65 and a_r2 >= a_cam - 0.10:
        return "retained"
    return "mixed"


def dose_verdict(levels, means, a01, a05, lo01, hi01):
    from scipy.stats import spearmanr
    rho = float(spearmanr(levels, means)[0])
    if rho >= 0.8 and a01 < a05 - 0.10 and hi01 < a05:
        return "ramp", rho
    if abs(a01 - a05) <= 0.05 and lo01 > 0.5:
        return "flat", rho
    return "mixed", rho


# ------------------------------------------------------------------------------------- data
def pubname(ph):
    p, slot = ph.split("__")
    return f"{p.split('_')[1]}_{'03' if slot == 's1' else '08'}"


def load_rows(data, logs, photos, synthetic):
    rows = list(csv.DictReader(open(pathlib.Path(data) / "manifests/ag1.csv")))
    lg = {}
    if logs:
        for f in list(pathlib.Path(logs).glob("*/log.csv")) + list(pathlib.Path(logs).glob("AG1_*.log.csv")):
            for r in csv.DictReader(open(f)):
                lg[r["stem"]] = r
    rng = np.random.default_rng(3)
    for r in rows:
        if r["id"] in lg:
            for k in ("loss", "msssim", "perc_x_l1", "latdist", "init_latdist"):
                if lg[r["id"]].get(k) not in (None, ""):
                    r[k] = float(lg[r["id"]][k])
        elif synthetic and r["source"] == "ours":
            r.update(loss=rng.normal(5, 1), msssim=rng.normal(0.3, 0.05), perc_x_l1=rng.normal(2, 0.3),
                     latdist=rng.normal(30, 3), init_latdist=rng.normal(25, 3))
    P = json.load(open(photos))

    def day(ph):
        d = P[ph]["date"]
        for fmt in ("%Y-%m-%d", "%y%m%d"):
            try:
                return datetime.datetime.strptime(d, fmt).date()
            except ValueError:
                pass
        return None
    for r in rows:
        r["day_a"] = day(r["photo_a"]) if r["photo_a"] in P else None
        r["day_b"] = day(r["photo_b"]) if r["photo_b"] in P else None
    return rows, P


def load_scores(rows, scores_dir, synthetic):
    S = {}
    rng = np.random.default_rng(1)
    for rel in RELEASES:
        if synthetic:
            base = {"R0": 0.0, "R1": 0.3, "R2": 0.8, "R2i": 0.8, "R2s": 1.0, "R3": 1.0, "R3m": 0.9, "R4": 1.3, "BR": 1.3, "RT": 1.0, "PUB": 1.4,
                    "AG3": 0.8, "AG3T": 0.8}
            S[rel] = {r["id"]: base[r["rung"]] + (1.0 * float(r["alpha"] or 0) if r["rung"] == "AG3" else 0)
                      + rng.normal() for r in rows}
            continue
        name, mode = (rel.split("__") + ["rel"])[:2]
        f = pathlib.Path(scores_dir) / name / mode / "scores_ag1.npz"       # a41g_out/ag1/<release>/<mode>/
        if not f.exists():
            print(f"missing {f}: release {rel} not read")
            continue
        z = np.load(f, allow_pickle=False)
        key = "logit_noTTA" if "logit_noTTA" in z.files else "score"
        S[rel] = dict(zip(z["id"].tolist(), z[key].astype(float).tolist()))
    return S


def in_pool(r, pool):
    return r["db"] in POOLS[pool]


# ------------------------------------------------------------------------------------- gates (no detector score)
def gates(rows, data, synthetic, out):
    if synthetic:
        rng = np.random.default_rng(2)
        per = sorted({r["pa"] for r in rows} | {r["pb"] for r in rows})
        Pv = {p: rng.normal(size=512) for p in per}
        E = {}
        for r in rows:
            v = Pv[r["pa"]] + Pv[r["pb"]] + 0.8 * rng.normal(size=512)
            E[r["id"]] = v / np.linalg.norm(v)
        rt = []
    else:
        f = pathlib.Path(data) / "oracle_glint.npz"
        if not f.exists():
            sys.exit("gates: no oracle_glint.npz (ag1_manifest.py oracle) - computed before any detector score")
        z = np.load(f)
        E = dict(zip(z["id"].tolist(), z["emb"]))
        rtp = pathlib.Path(data) / "rt_check.json"
        rt = json.load(open(rtp)) if rtp.exists() else None
    cam = {r["photo_a"]: r["id"] for r in rows if r["rung"] == "R0"}
    person_of = {r["id"]: r["pa"] for r in rows if r["rung"] == "R0"}

    def other_slot(ph):
        return ph[:-2] + ("s2" if ph.endswith("s1") else "s1")
    G = {}
    for gen in ("mip1", "mip2"):
        for pool in POOLS:
            R = {k: [r for r in rows if r["gen"] == gen and in_pool(r, pool) and r["rung"] == k and r["id"] in E]
                 for k in ("R2", "R3", "R4")}
            if not R["R3"] or not R["R4"]:
                continue
            camids = [i for p, i in cam.items() if any(p.startswith(d + "_") for d in POOLS[pool]) and i in E]
            M = np.stack([E[i] for i in camids])
            iu = np.triu_indices(len(camids), 1)
            diff = np.array([person_of[camids[i]] != person_of[camids[j]] for i, j in zip(*iu)])
            thr = float(np.quantile((M @ M.T)[iu][diff], 1 - 1e-3))

            def c(img, ph):
                return float(E[img] @ E[cam[ph]])
            a = auc([-c(r["id"], r["photo_a"]) for r in R["R4"]], [-c(r["id"], r["photo_a"]) for r in R["R3"]])
            vb_in = np.mean([min(c(r["id"], r["photo_a"]), c(r["id"], r["photo_b"])) >= thr for r in R["R4"]])
            vb_unseen = np.mean([min(c(r["id"], other_slot(r["photo_a"])), c(r["id"], other_slot(r["photo_b"])))
                                 >= thr for r in R["R4"]])
            v3 = np.mean([c(r["id"], r["photo_a"]) >= thr for r in R["R3"]])
            v3_unseen = np.mean([c(r["id"], other_slot(r["photo_a"])) >= thr for r in R["R3"]])
            Mc = np.stack([E[i] for i in camids])
            pc = np.array([person_of[i] for i in camids])
            fm = [((Mc[pc != r["pa"]] @ E[r["id"]]) >= thr).mean() for r in R["R2"]]
            ok_m, ok_t = a >= 0.90 and vb_in >= 0.70, v3 >= 0.90
            G[f"{gen}/{pool}"] = {
                "oracle_auc_R4_vs_R3": a, "R4_verifies_both_input": float(vb_in),
                "R4_verifies_both_unseen": float(vb_unseen), "R3_verifies_A_input": float(v3),
                "R3_verifies_A_unseen": float(v3_unseen), "R2_false_match_rate": float(np.mean(fm)) if fm else None,
                "thr_fmr1e-3": thr, "thr_A23": THR_A23, "n": {k: len(v) for k, v in R.items()},
                "pass": bool(ok_m and ok_t),
                "label": "pass" if ok_m and ok_t else ("morph construction weak" if not ok_m else
                                                      "twin construction invalid")}
    # RT vs R3: swapping (A, B) changes the floating-point summation order of the symmetric terms, so the two runs
    # diverge (GB10 smoke: mean 3.9, max 133 grey levels). Printed as the run-to-run perturbation; no gate.
    rtg = None
    if rt is not None:
        m = [o["mean"] for o in rt]
        rtg = {"n": len(rt), "median_mean_absdiff": float(np.median(m)) if m else None,
               "max_mean_absdiff": max(m, default=None), "max_absdiff": max((o["max"] for o in rt), default=None)}
    al, ld = {}, {}
    for r in rows:
        k = f"{r['gen']}/{r['rung']}"
        al.setdefault(k, []).append(str(r["aligned"]) == "True")
        if "latdist" in r:
            ld.setdefault(k, {"latdist": [], "init_latdist": []})
            ld[k]["latdist"].append(r["latdist"])
            ld[k]["init_latdist"].append(r.get("init_latdist", float("nan")))     # R2s: render only, no start latent
    res = {"G-b": G, "RT": rtg,
           "aligned_rate": {k: {"rate": float(np.mean(v)), "flag": bool(np.mean(v) < 0.90)} for k, v in al.items()},
           "latdist_median": {k: {kk: float(np.nanmedian(vv)) if np.isfinite(vv).any() else None for kk, vv in v.items()}
                              for k, v in ld.items()}}
    json.dump(res, open(out / "gates.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------- simple baselines
BASE = None          # id -> dict of scalar baselines and the thumbnail (ag1_baselines.py), set in main


def baseline_block(pos, neg, D):
    """AUC of each simple baseline for pos vs neg on the same images: scalar baselines oriented by their point
    estimate; the 32 x 32 thumbnail through a logistic probe, 5-fold grouped by host person, out-of-fold scores."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    pos = [r for r in pos if r["id"] in BASE]
    neg = [r for r in neg if r["id"] in BASE]
    if len(pos) < 10 or len(neg) < 10:
        return None
    wp = D.w([r["pa"] for r in pos], [r["pb"] for r in pos])
    wn = D.w([r["pa"] for r in neg], [r["pb"] for r in neg])
    aucs, reps = {}, {}
    for k in SCALAR_BASELINES:
        sp = np.array([BASE[r["id"]][k] for r in pos])
        sn = np.array([BASE[r["id"]][k] for r in neg])
        a = auc(sp, sn)
        sgn = 1.0 if a >= 0.5 else -1.0
        aucs[k] = max(a, 1 - a)
        reps[k] = wauc(sgn * sp, sgn * sn, wp, wn)
    X = np.stack([BASE[r["id"]]["thumb"] for r in pos + neg])
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    g = np.array([r["pa"] for r in pos + neg])
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)).fit(X[tr], y[tr])
        oof[te] = m.decision_function(X[te])
    aucs["thumb"] = auc(oof[:len(pos)], oof[len(pos):])
    reps["thumb"] = wauc(oof[:len(pos)], oof[len(pos):], wp, wn)
    best = max(aucs, key=aucs.get)
    return {"aucs": aucs, "best": best, "best_auc": aucs[best], "best_rep": reps[best]}


# ------------------------------------------------------------------------------------- scores
def contrast_fn(sc, D):
    def contrast(pos, neg):
        pos = [r for r in pos if r["id"] in sc]
        neg = [r for r in neg if r["id"] in sc]
        if not pos or not neg:
            return None
        sp = np.array([sc[r["id"]] for r in pos])
        sn = np.array([sc[r["id"]] for r in neg])
        rep = wauc(sp, sn, D.w([r["pa"] for r in pos], [r["pb"] for r in pos]),
                   D.w([r["pa"] for r in neg], [r["pb"] for r in neg]))
        return {"auc": auc(sp, sn), "ci": ci(rep), "rep": rep, "n": [len(pos), len(neg)]}
    return contrast


def matched_bins(R3, R4, sc, D):
    """R3 vs R4 within the 3 x 3 cells of pooled tertiles of the MS-SSIM term and the latent distance (non-identity
    terms only; amendment 1); pooled = cell-weighted AUC with fixed weights n3 * n4; read only if cells holding both
    rungs cover >= 50% of R4; bootstrap interval with the pool's draw. Also reported, never the stated reading."""
    R3 = [r for r in R3 if r["id"] in sc and "msssim" in r]
    R4 = [r for r in R4 if r["id"] in sc and "msssim" in r]
    if not R3 or not R4:
        return None
    X = np.array([r["msssim"] for r in R3 + R4])
    Z = np.array([r["latdist"] for r in R3 + R4])
    qx, qz = np.quantile(X, [1 / 3, 2 / 3]), np.quantile(Z, [1 / 3, 2 / 3])

    def cell(r):
        return int(np.searchsorted(qx, r["msssim"])), int(np.searchsorted(qz, r["latdist"]))
    contrast = contrast_fn(sc, D)
    num, rep, den, per = 0.0, 0.0, 0.0, {}
    for k in sorted({cell(r) for r in R3 + R4}):
        c3 = [r for r in R3 if cell(r) == k]
        c4 = [r for r in R4 if cell(r) == k]
        if c3 and c4:
            c = contrast(c4, c3)
            wgt = len(c3) * len(c4)
            per[str(k)] = {"auc": c["auc"], "n": c["n"]}
            num, rep, den = num + wgt * c["auc"], rep + wgt * c["rep"], den + wgt
    cov = sum(v["n"][0] for v in per.values()) / len(R4)
    if not den or cov < 0.5:
        return {"reading": "not matchable", "covered_R4": cov, "cells": per}
    a = num / den
    lo, hi = ci(rep / den)
    return {"pooled_auc": a, "ci": [lo, hi], "covered_R4": cov, "cells": per, "reading": side_verdict(a, lo, hi)}


def session_gap(R3, R4, sc, D):
    """(i) R3 vs R4 restricted to morphs whose B photo is within 60 days of the host's own second photo A'; (ii)
    stratified by tertiles of the session gap |day_b - day_a| (pooled R3 + R4). Sensitivity analysis (amendment 1)."""
    contrast = contrast_fn(sc, D)
    twin_day = {r["pa"]: r["day_b"] for r in R3}
    R3 = [r for r in R3 if r["day_a"] and r["day_b"]]
    R4 = [r for r in R4 if r["day_a"] and r["day_b"]]
    if not R3 or not R4:
        return None
    close = [r for r in R4 if twin_day.get(r["pa"]) and abs((r["day_b"] - twin_day[r["pa"]]).days) <= 60]
    hosts = {r["pa"] for r in close}
    out = {"within60": None}
    c = contrast(close, [r for r in R3 if r["pa"] in hosts])
    if c:
        out["within60"] = {"auc": c["auc"], "ci": c["ci"], "n": c["n"], "reading": side_verdict(c["auc"], *c["ci"])}

    def gap(r):
        return abs((r["day_b"] - r["day_a"]).days)
    q = np.quantile([gap(r) for r in R3 + R4], [1 / 3, 2 / 3])
    st = {}
    for k in range(3):
        c3 = [r for r in R3 if int(np.searchsorted(q, gap(r))) == k]
        c4 = [r for r in R4 if int(np.searchsorted(q, gap(r))) == k]
        c = contrast(c4, c3)
        st[str(k)] = {"auc": c["auc"], "ci": c["ci"], "n": c["n"]} if c else None
    out["gap_tertiles_days"] = q.tolist()
    out["strata"] = st
    return out


def dose(grp, sc, D, E):
    """AG3 (second identity) and AG3T (second photo of the same person): AUC of each alpha level against R2 of the
    host photo s1; alpha 0.5 = R4 / R3 of the same hosts. Achieved dose: glint cosine to A and to B per level."""
    contrast = contrast_fn(sc, D)
    cam = {r["photo_a"]: r["id"] for r in grp["R0"]}
    out = {}
    for arm, top in (("AG3", "R4"), ("AG3T", "R3")):
        rows = [r for r in grp[arm] if r["id"] in sc]
        if not rows:
            continue
        hosts = sorted({r["pa"] for r in rows})
        neg = [r for r in grp["R2"] if r["pa"] in hosts and r["photo_a"].endswith("__s1")]
        lv = {}
        for al in sorted({float(r["alpha"]) for r in rows}):
            lv[al] = [r for r in rows if abs(float(r["alpha"]) - al) < 1e-9]
        lv[0.5] = [r for r in grp[top] if r["pa"] in hosts]
        res = {}
        for al, L in sorted(lv.items()):
            c = contrast(L, neg)
            ach = None
            if E is not None:
                ach = {"cos_A": float(np.mean([E[r["id"]] @ E[cam[r["photo_a"]]] for r in L if r["id"] in E])),
                       "cos_B": float(np.mean([E[r["id"]] @ E[cam[r["photo_b"]]] for r in L if r["id"] in E]))}
            res[str(al)] = {"auc_vs_R2": c["auc"], "ci": c["ci"], "n": c["n"],
                            "mean": float(np.mean([sc[r["id"]] for r in L])), "achieved": ach}
        levels = sorted(lv)
        a01 = res["0.1"]
        v, rho = dose_verdict(levels, [res[str(a)]["mean"] for a in levels], a01["auc_vs_R2"],
                              res["0.5"]["auc_vs_R2"], *a01["ci"])
        out[arm] = {"levels": res, "spearman_levels_means": rho,
                    "reading": v + (" (dose along two-person mixing; the second identity also moves the latent,"
                                    " perceptual and MS-SSIM targets)" if arm == "AG3" else " (twin dose: second photo"
                                                                                           " only)")}
    return out


def read(rows, S, E, out, boot, pub_eer):
    res, ladder, pvals = {}, [], {}
    for pool in POOLS:
        pers = sorted({r["pa"] for r in rows if in_pool(r, pool)} | {r["pb"] for r in rows if in_pool(r, pool)})
        D = Draw(pers, boot, SEED + zlib.crc32(pool.encode()) % 100000)
        for gen in ("mip1", "mip2"):
            sub = [r for r in rows if in_pool(r, pool) and r["gen"] in (gen, "camera")]
            if not any(r["rung"] == "R4" for r in sub):
                continue
            grp = {k: [r for r in sub if r["rung"] == k] for k in
                   ("R0", "R1", "R2", "R2i", "R2s", "R3", "R3m", "R4", "PUB", "BR", "RT", "AG3", "AG3T")}
            bl_cache = {}
            for rel, sc in S.items():
                contrast = contrast_fn(sc, D)
                c = {"R0>R2": contrast(grp["R2"], grp["R0"]), "R2>R3": contrast(grp["R3"], grp["R2"]),
                     "R3>R4": contrast(grp["R4"], grp["R3"]), "R2>R4": contrast(grp["R4"], grp["R2"]),
                     "R0>R4": contrast(grp["R4"], grp["R0"]), "R2>R3m (mirror, own rung)": contrast(grp["R3m"], grp["R2"]),
                     "R3m>R4 (mirror, own rung)": contrast(grp["R4"], grp["R3m"]), "R3>RT (noise floor)": contrast(grp["RT"], [r for r in grp["R3"] if r["pa"] in {x["pa"] for x in grp["RT"]}]),
                     "R2s>R4 (spread-matched one-person render)": contrast(grp["R4"], grp["R2s"])}
                cell = {}
                if pool == "frll":
                    c["R0>R1"] = contrast(grp["R1"], grp["R0"])
                    c["R1>R2"] = contrast(grp["R2"], grp["R1"])
                    c["R0>PUB"] = contrast(grp["PUB"], grp["R0"])
                    c["R2>PUB (AG2)"] = contrast(grp["PUB"], grp["R2"])
                    pub = {frozenset((r["photo_a"], r["photo_b"])): r for r in grp["PUB"]}

                    def key(r):
                        return frozenset((pubname(r["photo_a"]), pubname(r["photo_b"])))
                    br = [r for r in grp["BR"] if key(r) in pub]
                    c["bridge PUB vs BR"] = contrast([pub[key(r)] for r in br], br)
                d04 = dprime(c["R0>R4"]["auc"]) if c["R0>R4"] else None
                sh = {}
                for k in ("R0>R1", "R1>R2", "R0>R2", "R2>R3", "R3>R4", "R2>R4"):
                    if c.get(k) and d04 and d04 > 0:
                        rep = np.array([dprime(x) for x in c[k]["rep"]]) / np.array(
                            [max(dprime(x), 1e-9) for x in c["R0>R4"]["rep"]])
                        sh[k] = {"share": dprime(c[k]["auc"]) / d04, "ci": ci(rep)}
                m24 = c["R2>R4"]
                cell["main_A"] = verdict_A(m24["auc"], *m24["ci"], sh.get("R0>R2", {}).get("share"),
                                           sh.get("R0>R2", {}).get("ci", [None])[0])
                cell["main_B"] = verdict_B(m24["auc"], *m24["ci"])
                cell["side_R3_R4"] = side_verdict(c["R3>R4"]["auc"], *c["R3>R4"]["ci"])
                cell["side_R2_R3"] = side_verdict(c["R2>R3"]["auc"], *c["R2>R3"]["ci"])
                cell["R2_line"] = "R2 = the generator's reconstruction of one photo (MIPGAN with A = B)"
                p_morph = float(np.mean(m24["rep"] <= 0.65))      # H0: R2 vs R4 AUC <= 0.65 (one-sided)
                cell["p_reads_morphing"] = p_morph
                if pool == "primary" and gen == "mip1" and rel in PRIMARY_RELEASES:
                    pvals[rel] = p_morph
                fr = [r for r in rows if r["db"] == "frll" and r["id"] in sc]
                bb = [sc[r["id"]] for r in fr if r["rung"] == "R0"]
                mm = [sc[r["id"]] for r in fr if r["rung"] == "PUB" and r["gen"] == gen]
                if bb and mm:                                       # the corrected MAD22 cell: FRLL R0 vs PUB
                    thr, eer = eer_thr(bb, mm)
                    cell["benchmark_eer_pct"] = 100 * eer
                    ref = (pub_eer or {}).get(rel, {}).get(gen)
                    cell["G-a"] = ("no published number given" if ref is None else
                                   ("reproduced" if abs(100 * eer - ref) <= 3 else "not reproduced, descriptive"))
                    cell["flag_rate_at_benchmark_thr"] = {
                        k: exact(int(sum(sc[r["id"]] >= thr for r in grp[k] if r["id"] in sc)),
                                 sum(r["id"] in sc for r in grp[k])) for k in ("R0", "R2", "R3", "R4") if grp[k]}
                if pool == "frll" and c.get("R2>PUB (AG2)"):
                    cell["AG2"] = ag2_verdict(c["R0>PUB"]["auc"], c["R2>PUB (AG2)"]["auc"], *c["R2>PUB (AG2)"]["ci"],
                                              c["bridge PUB vs BR"]["auc"] if c["bridge PUB vs BR"] else None)
                # amendment 3, rule 5: every contrast as excess over the best simple baseline on the same images
                pairs = {"R0>R2": (grp["R2"], grp["R0"]), "R2>R3": (grp["R3"], grp["R2"]), "R3>R4": (grp["R4"], grp["R3"]),
                         "R2>R4": (grp["R4"], grp["R2"]), "R0>R4": (grp["R4"], grp["R0"]),
                         "R2>R3m (mirror, own rung)": (grp["R3m"], grp["R2"]),
                         "R3m>R4 (mirror, own rung)": (grp["R4"], grp["R3m"]),
                         "R2s>R4 (spread-matched one-person render)": (grp["R4"], grp["R2s"]),
                         "R3>RT (noise floor)": (grp["RT"], [r for r in grp["R3"] if r["pa"] in {x["pa"] for x in grp["RT"]}])}
                if pool == "frll":
                    pairs.update({"R0>R1": (grp["R1"], grp["R0"]), "R1>R2": (grp["R2"], grp["R1"]),
                                  "R0>PUB": (grp["PUB"], grp["R0"]), "R2>PUB (AG2)": (grp["PUB"], grp["R2"]),
                                  "bridge PUB vs BR": ([pub[key(r)] for r in br], br)})
                for k, (pos, neg) in pairs.items():
                    if not c.get(k) or BASE is None:
                        continue
                    if k not in bl_cache:
                        bl_cache[k] = baseline_block(pos, neg, D)
                    b = bl_cache[k]
                    if b is None:
                        continue
                    c[k]["baselines"] = b["aucs"]
                    c[k]["best_baseline"] = b["best"]
                    c[k]["excess_over_best_baseline"] = {"excess": c[k]["auc"] - b["best_auc"],
                                                         "ci": ci(c[k]["rep"] - b["best_rep"])}
                # amendment 3, rule 1: flag rates under both class policies, no verdict word
                if bb and mm:
                    def fr_(L):
                        L = [r for r in L if r["id"] in sc]
                        return exact(int(sum(sc[r["id"]] >= thr for r in L)), len(L))
                    cell["flag_rates_at_benchmark_thr"] = {
                        "genuine error, policy N (reconstruction = non-attack: R0 + R2)": fr_(grp["R0"] + grp["R2"]),
                        "genuine error, policy X (reconstruction inadmissible: R0 only)": fr_(grp["R0"]),
                        "attack detection (R4)": fr_(grp["R4"]),
                        "single-subject table": {k: fr_(grp[k]) for k in SINGLE_SUBJECT if grp[k]}}
                    cell.pop("flag_rate_at_benchmark_thr", None)
                cell["latdist_median"] = {k: float(np.median([r["latdist"] for r in grp[k] if "latdist" in r]))
                                          for k in ("R2", "R2s", "R3", "R4") if any("latdist" in r for r in grp[k])}
                # amendment 4: readings per generation platform (persons of a shard share one platform)
                # platform of a host = platform of its core rows (R2 / R3 / R4 come from one core shard); spread and
                # graded-mixing shards ran on the rented machine for hosts of either platform and do not define it
                core = [r for r in sub if r["rung"] in ("R2", "R3", "R4") and r["source"] == "ours"]
                plats = sorted({r.get("platform", "") for r in core})
                if len(plats) > 1:
                    ps = {}
                    for pl in plats:
                        hosts = {r["pa"] for r in core if r.get("platform") == pl}
                        g2 = {k: [r for r in v if r["pa"] in hosts] for k, v in grp.items()}
                        ps[pl] = {k: ({kk: vv for kk, vv in x.items() if kk != "rep"} if x else None) for k, x in
                                  (("R2>R4", contrast(g2["R4"], g2["R2"])), ("R3>R4", contrast(g2["R4"], g2["R3"])),
                                   ("R2s>R4", contrast(g2["R4"], g2["R2s"])), ("R0>R4", contrast(g2["R4"], g2["R0"])))}
                    cell["platform_sensitivity"] = ps
                cell["R3_R4_matched_bins (also reported)"] = matched_bins(grp["R3"], grp["R4"], sc, D)
                if pool != "frll":
                    cell["R3_R4_session_gap"] = session_gap(grp["R3"], grp["R4"], sc, D)
                if gen == "mip1" and pool != "frll":
                    cell["dose"] = dose(grp, sc, D, E)
                cell.update({k: ({kk: vv for kk, vv in v.items() if kk != "rep"} if v else None) for k, v in c.items()})
                cell["shares"] = sh
                cell["primary"] = pool == "primary" and gen == "mip1" and rel in PRIMARY_RELEASES
                cell["release_row"] = "primary" if rel in PRIMARY_RELEASES else "secondary (printed beside)"
                res[f"{gen}/{pool}/{rel}"] = cell
                ladder.append({"cell": f"{gen}/{pool}/{rel}",
                               **{k: round(v["auc"], 3) if v else "" for k, v in c.items()},
                               "main_A": cell["main_A"], "main_B": cell["main_B"], "side_R3_R4": cell["side_R3_R4"]})
    if pvals:
        for rel, v in holm(pvals).items():
            res[f"mip1/primary/{rel}"]["p_reads_morphing_holm_within_AG1"] = v
    res["_not_scored"] = list(NOT_SCORED)
    json.dump(res, open(out / "ag1_read.json", "w"), indent=1, default=float)
    with open(out / "ag1_ladder.csv", "w", newline="") as fh:
        keys = sorted({k for r in ladder for k in r}, key=lambda k: (k != "cell", k))
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(ladder)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--scores", default=None)
    ap.add_argument("--logs", default=None, help="dir with every shard's <shard>.log.csv (copied from results/AG1)")
    ap.add_argument("--photos", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--published-eer", default=None, help="JSON {release: {mip1: EER%%, mip2: EER%%}} for G-a")
    ap.add_argument("--boot", type=int, default=B_DEC)
    ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    if not a.synthetic and a.boot != B_DEC:
        sys.exit("refused: the registered bootstrap size is 10,000")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, _ = load_rows(a.data, a.logs, a.photos, a.synthetic)
    g = gates(rows, a.data, a.synthetic, out)                       # before any detector score is loaded
    print("GATES", json.dumps({"G-b": {k: v["label"] for k, v in g["G-b"].items()}, "RT": g["RT"]}))
    if a.gate_only:
        return
    E = None
    if not a.synthetic:
        z = np.load(pathlib.Path(a.data) / "oracle_glint.npz")
        E = dict(zip(z["id"].tolist(), z["emb"]))
    global BASE
    bp = pathlib.Path(a.data) / "baselines.npz"
    if bp.exists():
        z = dict(np.load(bp))           # load every array once (indexing an NpzFile re-reads the whole array)
        BASE = {i: {"bytes": z["bytes"][k], "lapvar": z["lapvar"][k], "hfband": z["hfband"][k], "sym": z["sym"][k],
                    "thumb": z["thumb"][k]} for k, i in enumerate(z["id"].tolist())}
    elif a.synthetic:
        rng = np.random.default_rng(4)
        BASE = {r["id"]: {"bytes": rng.normal(), "lapvar": rng.normal(), "hfband": rng.normal(),
                          "sym": rng.normal() + (1.0 if r["rung"] == "R3m" else 0.0),
                          "thumb": rng.normal(size=1024)} for r in rows}
    else:
        sys.exit("no baselines.npz (ag1_baselines.py): amendment 3 requires the baseline block")
    S = load_scores(rows, a.scores, a.synthetic)
    pub = json.load(open(a.published_eer)) if a.published_eer else None
    res = read(rows, S, E, out, a.boot, pub)
    for k, v in res.items():
        if k.startswith("_"):
            continue
        gbk = g["G-b"].get("/".join(k.split("/")[:2]), {}).get("label", "no G-b")
        print(k, "| G-b:", gbk, "| A:", v["main_A"], "| B:", v["main_B"], "| R3 vs R4:", v["side_R3_R4"],
              "| AG2:", v.get("AG2", "-"),
              "| dose:", {kk: vv["reading"].split(" (")[0] for kk, vv in (v.get("dose") or {}).items()} or "-")


if __name__ == "__main__":
    main()

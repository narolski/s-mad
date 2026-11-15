"""Threshold transfer on unseen genuine sources (TT1): registered reader of registration TT1-S (prereg_scoring.md).
Implements sections 3, 5 and 6 exactly; prints every number for every network; no choice of arm, seed or threshold.
Inputs: --scores DIR with <net>__gate.npz and <net>__tt1.npz (rescore.py output); --nets DIR (tt1nets/nets, for the
head floor); the list tt1_score.csv; raw/aligned manifests (tt1common). --mock: random logits (test only).
  python -I tt1_read.py --scores DIR --nets DIR --out OUT.json [--mock]"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

NB = 2000
SEED = 20261122
INFL = {"lfw": 1.18, "calfw": 1.18, "lfw_calfw": 1.18, "cfp_ff": 1.78, "agedb_30": 2.03}
NETS = [f"PN1_{a}_s{s}" for s in (401, 402) for a in ("A", "B", "Bn", "C", "Sb", "Bv")]
GROUP = {s: ("g224" if s in T.ANTISPOOF else "g112") for s in T.SOURCES}
PACKS = ["lfw", "calfw", "cfp_ff", "agedb_30"]
PN1E = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1")
PN1R = pathlib.Path("/mnt/t7/smad_next/PN1/results_rented/unpacked")


# ---------------------------------------------------------------- statistics
def wauc(pos, neg, wp=None, wn=None):
    """AUC P(pos > neg) + 0.5 P(tie), with optional weights (bootstrap multiplicities); mid-rank ties."""
    wp = np.ones(len(pos)) if wp is None else wp
    wn = np.ones(len(neg)) if wn is None else wn
    o = np.argsort(neg, kind="mergesort")
    ns, ws = neg[o], wn[o]
    cw = np.concatenate([[0.0], np.cumsum(ws)])
    lo = np.searchsorted(ns, pos, "left")
    hi = np.searchsorted(ns, pos, "right")
    below = cw[lo]
    eq = cw[hi] - cw[lo]
    tot = cw[-1] * wp.sum()
    return float(((below + 0.5 * eq) * wp).sum() / tot) if tot > 0 else float("nan")


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def spearman(x, y, w=None):
    from scipy.stats import rankdata
    if w is not None:                                   # bootstrap: expand by multiplicity
        idx = np.repeat(np.arange(len(x)), w.astype(int))
        x, y = x[idx], y[idx]
    if len(x) < 3:
        return float("nan")
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def interval(point, draws, k=1.0):
    d = np.asarray([v for v in draws if np.isfinite(v)])
    if not len(d):
        return [float("nan"), float("nan")]
    lo, hi = np.percentile(d, [2.5, 97.5])
    return [float(point - k * (point - lo)), float(point + k * (hi - point))]


# ---------------------------------------------------------------- pools and bootstrap weights
def load_pools():
    lst = list(csv.DictReader(open(T.OUT / "tt1_score.csv")))
    tt = {r["id"]: r for r in T.tt1_rows()}
    P = {}
    for r in lst:
        if r["fam"] == "gate":
            P.setdefault(r["rung"], []).append((r["id"], r["host"] if r["rung"] == "R_cam" else r["id"]))
        elif r["rung"] in T.SOURCES:
            t = tt[r["id"]]
            P.setdefault(f"Uall:{r['rung']}", []).append((r["id"], r["host"]))
            if t["primary"]:
                P.setdefault(f"U:{r['rung']}", []).append((r["id"], r["host"]))
        elif r["rung"] == "R_cam_border":
            P.setdefault(f"Rcb:{r['cell']}", []).append((r["id"], r["host"]))
        elif r["rung"] == "R_ffhq_border":
            P.setdefault("Rfb", []).append((r["id"], r["strength"] and r["id"]))
        elif r["rung"].startswith("R_cam_geo"):
            P.setdefault(f"Rgeo:{r['cell']}", []).append((r["id"], r["host"]))
    return P, tt


def boot_weights(P, rng):
    """per pool: (NB, n_images) multiplicities from resampling persons within the pool, the same for every network.
    R_cam-derived pools (R_cam, Rcb:*, Rgeo:*) share one host resampling, so paired contrasts use the same hosts."""
    W = {}
    hosts = sorted({h for _, h in P["R_cam"]})
    hm = rng.integers(0, len(hosts), size=(NB, len(hosts)))
    hcount = np.zeros((NB, len(hosts)))
    for b in range(NB):
        hcount[b] = np.bincount(hm[b], minlength=len(hosts))
    hidx = {h: i for i, h in enumerate(hosts)}
    for name in sorted(P):
        rows = P[name]
        if name == "R_cam" or name.startswith(("Rcb:", "Rgeo:")):
            W[name] = hcount[:, [hidx[h] for _, h in rows]]
            continue
        ps = sorted({h for _, h in rows})
        pi = {h: i for i, h in enumerate(ps)}
        m = rng.integers(0, len(ps), size=(NB, len(ps)))
        c = np.zeros((NB, len(ps)))
        for b in range(NB):
            c[b] = np.bincount(m[b], minlength=len(ps))
        W[name] = c[:, [pi[h] for _, h in rows]]
    return W


# ---------------------------------------------------------------- per-network reads
def tau_cam(net):
    """tier-1 camera threshold (A, B, Bn, C from tier1 JSON; Sb, Bv by the same rule from scores_eval.npz)."""
    f = PN1E / f"{net[len('PN1_'):]}.json"
    if f.exists():
        return float(json.load(open(f))["thresholds"]["cam"]), "tier1 json"
    ev = list(csv.DictReader(open(T.PN1T / "data" / "manifests" / "pn1_eval.csv")))
    z = np.load(PN1R / net / "scores_eval.npz")
    m = dict(zip(z["id"].tolist(), z["logit"].tolist()))
    pools = {"D_R0": [m[r["id"]] for r in ev if r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0" and r["strength"] == ""],
             "V_photo": [m[r["id"]] for r in ev if r["fam"] == "af0" and r["rung"] == "photo" and r["strength"] == ""]}
    th = []
    for v in pools.values():
        v = np.sort(np.array(v))
        t = next(x for x in v if np.mean(v > x) <= 0.05)
        th.append(float(t))
    return max(th), "computed from scores_eval.npz (rule of tier1)"


def head_floor(netdir):
    import torch
    t = torch.load(pathlib.Path(netdir) / "last_trainable.pt", map_location="cpu", weights_only=True)
    w, b = t["head.cls.weight"].float(), t["head.cls.bias"].float()
    return float(-w.norm() + b[0])


def read_net(L, P, W, tt, floor, tcam):
    def arr(pool):
        return np.array([L[i] for i, _ in P[pool]], np.float64)
    out = dict(floor=floor, tau_cam=tcam, pools={}, auc={}, r4={}, r5={})
    # R1/R2 per pool
    for pool in sorted(P):
        x = arr(pool)
        f = (x > 0).astype(float)
        src = pool.split(":")[1] if ":" in pool else None
        k = INFL.get(src, 1.0) if pool.startswith(("U:", "Uall:")) else 1.0
        Wb = W[pool]
        bf = (Wb @ f) / Wb.sum(1)
        out["pools"][pool] = dict(
            n=len(x), persons=len({h for _, h in P[pool]}), flag=float(f.mean()), flag_cp=cp(int(f.sum()), len(x)),
            flag_boot=interval(float(f.mean()), bf, k), inflation=k, flag_tau_cam=float((x > tcam).mean()),
            median=float(np.median(x)), iqr=[float(np.percentile(x, 25)), float(np.percentile(x, 75))],
            floor_share=float((x <= floor + 0.05).mean()))
    u = out["pools"]["M_ffhq"]["median"] - out["pools"]["R_cam"]["median"]
    out["u"] = u
    out["u_degenerate"] = bool(u < 1)
    cam_med = out["pools"]["R_cam"]["median"]
    for pool in out["pools"]:
        out["pools"][pool]["shift_from_cam"] = out["pools"][pool]["median"] - cam_med
        out["pools"][pool]["shift_from_cam_u"] = (out["pools"][pool]["median"] - cam_med) / u if u else float("nan")

    def auc_read(pa, pb, k=1.0):
        a, b = arr(pa), arr(pb)
        pt = wauc(a, b)
        draws = [wauc(a, b, W[pa][i], W[pb][i]) for i in range(NB)]
        tied = out["pools"][pa]["floor_share"] > 0.5 and out["pools"][pb]["floor_share"] > 0.5
        return dict(auc=pt, ci=interval(pt, draws, k), floor_tied=bool(tied))

    for s in T.SOURCES:
        k = INFL.get(s, 1.0)
        fam = "lfw_calfw" if s in ("lfw", "calfw") else s
        out["auc"][s] = dict(
            a=auc_read(f"U:{s}", "R_cam", k), b=auc_read(f"U:{s}", "R_ffhq", k), c=auc_read(f"U:{s}", f"Rcb:{fam}", k),
            g=auc_read(f"U:{s}", f"Rgeo:{GROUP[s]}", k),
            above_cam_median=float((arr(f"U:{s}") > cam_med).mean()))
    out["auc"]["d_ffhq_border"] = auc_read("Rfb", "R_ffhq")
    out["auc"]["e_cam_border"] = {f: auc_read(f"Rcb:{f}", "R_cam") for f in T.FAMILIES}
    out["auc"]["f_geo"] = {g: auc_read(f"Rgeo:{g}", "R_cam") for g in ("g224", "g112")}
    # R4a/b: sharpness
    lap = {i: float(tt[i]["lap_var"]) for i in tt}
    edges = json.load(open(T.RES / "strata_edges.json"))["lap_var"]
    groups = {s: [s] for s in PACKS}
    groups["antispoof_pooled"] = T.ANTISPOOF
    for g, srcs in groups.items():
        ids = [i for s in srcs for i, _ in P[f"U:{s}"]]
        x = np.array([L[i] for i in ids])
        lv = np.log(np.array([lap[i] for i in ids]))
        wcat = np.concatenate([W[f"U:{s}"] for s in srcs], axis=1)
        rho = spearman(x, lv)
        k = INFL.get(g, 1.0)
        draws = [spearman(x, lv, wcat[b]) for b in range(0, NB, 4)]    # 500 draws (cost); fixed subsample of the draws
        e = edges[g]
        q = np.clip(np.searchsorted(e[1:-1], np.exp(lv), "right"), 0, 4)
        out["r4"][g] = dict(rho=rho, rho_ci=interval(rho, draws, k), floor_share=float((x <= floor + 0.05).mean()),
                            floor_tied=bool((x <= floor + 0.05).mean() > 0.5),
                            quintiles=[dict(flag=float((x[q == j] > 0).mean()) if (q == j).any() else None,
                                            median=float(np.median(x[q == j])) if (q == j).any() else None,
                                            n=int((q == j).sum())) for j in range(5)])
    per_src = [(float(np.median([lap[i] for i, _ in P[f"U:{s}"]])), out["pools"][f"U:{s}"]["flag"]) for s in T.ANTISPOOF]
    out["r4"]["antispoof_source_order_spearman"] = spearman(np.array([a for a, _ in per_src]), np.array([b for _, b in per_src]))
    # R4c/d: OLS
    out["r4"]["lofo"], out["r4"]["full"] = ols_reads(L, P, W, tt, u)
    # R5
    out["r5"] = r5(out, P, W, L)
    return out


def design(ids, tt):
    enl = np.log(np.array([float(tt[i]["enlarge"]) for i in ids]))
    lv = np.log(np.array([float(tt[i]["lap_var"]) for i in ids]))
    bf = np.array([float(tt[i]["border_frac"]) for i in ids])
    gr = np.array([float(tt[i]["greyscale"]) for i in ids])
    return enl, lv, bf, gr


def ols_reads(L, P, W, tt, u):
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    ids = {f: [i for s in fam_src[f] for i, _ in P[f"U:{s}"]] for f in T.FAMILIES}
    wb = {f: np.concatenate([W[f"U:{s}"] for s in fam_src[f]], axis=1) for f in T.FAMILIES}
    allids = [i for f in T.FAMILIES for i in ids[f]]
    enl, lv, bf, gr = design(allids, tt)
    mu = dict(enl=(enl.mean(), enl.std()), lv=(lv.mean(), lv.std()))
    X = {}
    for f in T.FAMILIES:
        e, l, b, g = design(ids[f], tt)
        X[f] = np.column_stack([np.ones(len(e)), (e - mu["enl"][0]) / mu["enl"][1], (l - mu["lv"][0]) / mu["lv"][1], b, g])
    y = {f: np.array([L[i] for i in ids[f]]) for f in T.FAMILIES}

    def fit(fams, wts):
        A = np.zeros((5, 5)); c = np.zeros(5)
        for f in fams:
            w = wts[f] / wts[f].sum()                        # equal family weight
            A += (X[f] * w[:, None]).T @ X[f]; c += (X[f] * w[:, None]).T @ y[f]
        return np.linalg.lstsq(A, c, rcond=None)[0]

    def lofo(wts):
        e = {}
        for f in T.FAMILIES:
            beta = fit([g for g in T.FAMILIES if g != f], wts)
            w = wts[f] / wts[f].sum()
            e[f] = float(((y[f] - X[f] @ beta) * w).sum() / u) if u else float("nan")
        return e

    ones = {f: np.ones(len(y[f])) for f in T.FAMILIES}
    pt = lofo(ones)
    draws = [lofo({f: wb[f][b] for f in T.FAMILIES}) for b in range(0, NB, 4)]   # 500 draws (cost)
    lo = {f: dict(e_u=pt[f], ci=interval(pt[f], [d[f] for d in draws], INFL.get(f, 1.0))) for f in T.FAMILIES}
    # full model with family indicators (reference family: oulu_npu), coefficients in u
    def full(wts):
        cols = [g for g in T.FAMILIES if g != "oulu_npu"]
        A = np.zeros((5 + len(cols),) * 2); c = np.zeros(5 + len(cols))
        for f in T.FAMILIES:
            ind = np.zeros((len(y[f]), len(cols)))
            if f in cols:
                ind[:, cols.index(f)] = 1
            Z = np.column_stack([X[f], ind]); w = wts[f] / wts[f].sum()
            A += (Z * w[:, None]).T @ Z; c += (Z * w[:, None]).T @ y[f]
        return np.linalg.lstsq(A, c, rcond=None)[0], cols
    bp, cols = full(ones)
    bd = [full({f: wb[f][b] for f in T.FAMILIES})[0] for b in range(0, NB, 4)]
    names = ["const", "z_log_enlarge", "z_log_lap_var", "border_frac", "greyscale"] + [f"fam_{c}" for c in cols]
    fu = {n: dict(coef_u=float(bp[j] / u) if u else float("nan"),
                  ci=interval(float(bp[j] / u) if u else float("nan"), [d[j] / u for d in bd],
                              INFL.get(n[4:], 1.0) if n.startswith("fam_") else 1.0)) for j, n in enumerate(names)}
    fu["z_log_enlarge"]["label"] = "identified by within-family detection noise; not interpreted"
    fam_means = np.array([y[f].mean() for f in T.FAMILIES])
    pred_cov = np.array([(X[f] @ fit(T.FAMILIES, ones)).mean() for f in T.FAMILIES])
    fu["between_family_variance_explained_by_covariates"] = float(1 - ((fam_means - pred_cov) ** 2).sum() / ((fam_means - fam_means.mean()) ** 2).sum())
    return lo, fu


def r5(out, P, W, L):
    fams = T.FAMILIES
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in fams}

    def famflag(b=None):
        v = {}
        for f in fams:
            num = den = 0.0
            for s in fam_src[f]:
                x = np.array([L[i] for i, _ in P[f"U:{s}"]]) > 0
                w = np.ones(len(x)) if b is None else W[f"U:{s}"][b]
                num += (w * x).sum(); den += w.sum()
            v[f] = num / den
        return v

    def famauc(b=None):
        v = {}
        cam = np.array([L[i] for i, _ in P["R_cam"]])
        wc = None if b is None else W["R_cam"][b]
        for f in fams:
            x = np.concatenate([np.array([L[i] for i, _ in P[f"U:{s}"]]) for s in fam_src[f]])
            w = None if b is None else np.concatenate([W[f"U:{s}"][b] for s in fam_src[f]])
            v[f] = wauc(x, cam, w, wc)
        return v

    def summ(fl, au):
        fv = np.array([fl[f] for f in fams]); av = np.array([au[f] for f in fams])
        return dict(Fbar=float(fv.mean()), Fbar_noMSU=float(np.mean([fl[f] for f in fams if f != "msu_mfsd"])),
                    Fmax=float(fv.max()), S_F=float(fv.std(ddof=1)), Abar=float(av.mean()), S_A=float(av.std(ddof=1)))
    pt = summ(famflag(), famauc())
    pt["family_flag"] = famflag()
    pt["_draws"] = [summ(famflag(b), famauc(b)) for b in range(0, NB, 4)]      # 500 paired draws (cost)
    return pt


# ---------------------------------------------------------------- hypotheses
def verdicts(R):
    V = {}
    arms_all = ["A", "B", "Bn", "C", "Sb", "Bv"]
    arms = [a for a in arms_all if all(f"PN1_{a}_s{s}" in R for s in (401, 402))]
    missing = {a: [s for s in (401, 402) if f"PN1_{a}_s{s}" not in R] for a in arms_all if a not in arms}
    NA = "not available (failed platform gate)"

    def net(a, s):
        return R[f"PN1_{a}_s{s}"]
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    # TT-H1: family interval from the pooled family? use per-family bootstrap = source-level for single-source families;
    # lfw_calfw: the more conservative (lower) of the two source lower bounds is not registered -> pool by recompute below
    h1 = {}
    for a in arms:
        per = {}
        for s in (401, 402):
            r = net(a, s)
            fails = [f for f in T.FAMILIES if r["fam_flag_ci"][f][0] > 0.05]
            transfers = all(r["fam_flag_ci"][f][1] <= 0.10 for f in T.FAMILIES)
            per[s] = dict(fails=fails, n_fail=len(fails), all_upper_le_10=transfers,
                          cam_share=r["pools"]["R_cam"]["flag"], uninformative=r["pools"]["R_cam"]["flag"] > 0.05)
        need = 4 if a == "A" else 2
        if per[401]["all_upper_le_10"] and per[402]["all_upper_le_10"]:
            v = "falsified (own rule transfers on these sources)"
        elif per[401]["n_fail"] >= need and per[402]["n_fail"] >= need:
            v = f"supported (fails in >= {need} of 7 on both seeds)" if a in ("A", "B", "Sb") else "printed"
        else:
            v = "not supported as predicted" if a in ("A", "B", "Sb") else "printed"
        if per[401]["uninformative"] or per[402]["uninformative"]:
            v += " [uninformative: R_cam share > 5% on a seed]"
        h1[a] = dict(seeds=per, verdict=v)
    for a, ms in missing.items():
        h1[a] = dict(verdict=f"{NA}: " + ", ".join(f"PN1_{a}_s{x}" for x in ms) + "; the other seed is printed alone (one seed)")
    V["TT-H1"] = h1
    # TT-H2
    h2 = {}
    for n, r in R.items():
        a90 = sum(r["auc"][s]["a"]["auc"] >= 0.90 for s in T.SOURCES)
        a75 = sum(r["auc"][s]["a"]["auc"] >= 0.75 for s in T.SOURCES)
        h2[n] = dict(n_ge_090=a90, n_ge_075=a75, floor_tied=[s for s in T.SOURCES if r["auc"][s]["a"]["floor_tied"]],
                     verdict="supported" if a90 >= 6 else ("falsified" if a75 <= 3 else "not supported as predicted"))
    V["TT-H2"] = h2
    # TT-H3
    h3 = {}
    for n, r in R.items():
        famauc_a = {f: np.mean([r["auc"][s]["a"]["auc"] for s in fam_src[f]]) for f in T.FAMILIES}
        famauc_c = {f: np.mean([r["auc"][s]["c"]["auc"] for s in fam_src[f]]) for f in T.FAMILIES}
        e = {f: r["auc"]["e_cam_border"][f]["auc"] for f in T.FAMILIES}
        d = r["auc"]["d_ffhq_border"]["auc"]
        mat = (sum(famauc_c[f] <= famauc_a[f] - 0.10 for f in T.FAMILIES) >= 4 and sum(e[f] >= 0.65 for f in T.FAMILIES) >= 4
               and d >= 0.65)
        notm = (sum(abs(famauc_c[f] - famauc_a[f]) <= 0.03 for f in T.FAMILIES) >= 6
                and sum(e[f] <= 0.55 for f in T.FAMILIES) >= 6 and d <= 0.55)
        h3[n] = dict(verdict="border material" if mat else ("border not material" if notm else "inconclusive"),
                     a_minus_c={f: float(famauc_a[f] - famauc_c[f]) for f in T.FAMILIES}, e=e, d=d,
                     note="lfw_calfw family value = mean of the LFW and CALFW source AUCs")
    V["TT-H3"] = h3
    # TT-H4
    h4 = {}
    for a in arms:
        per = {}
        for s in (401, 402):
            r = net(a, s)
            ok = [p for p in PACKS if not r["r4"][p]["floor_tied"]]
            per[s] = dict(usable=ok, rho={p: r["r4"][p]["rho"] for p in PACKS},
                          n_le_m015=sum(r["r4"][p]["rho"] <= -0.15 for p in ok), n_ge_0=sum(r["r4"][p]["rho"] >= 0 for p in ok))
        usable = all(len(per[s]["usable"]) >= 3 for s in (401, 402))
        if not usable:
            v = "not read (fewer than 3 packs off the floor on a seed)"
        elif all(per[s]["n_ge_0"] >= 3 for s in (401, 402)):
            v = "falsified"
        elif a == "A":
            v = "supported" if all(per[s]["n_le_m015"] >= 3 for s in (401, 402)) else "not supported as predicted"
        elif a in ("B", "Sb"):
            smaller = all(sum(abs(per[s]["rho"][p]) < abs(net("A", s)["r4"][p]["rho"]) for p in PACKS) >= 3 for s in (401, 402))
            v = "supported (|rho| below A's)" if smaller else "not supported as predicted"
        else:
            v = "printed"
        h4[a] = dict(seeds=per, verdict=v)
    for a, ms in missing.items():
        h4[a] = dict(verdict=f"{NA}: " + ", ".join(f"PN1_{a}_s{x}" for x in ms) + "; the other seed is printed alone (one seed)")
    V["TT-H4"] = h4
    # TT-H5
    h5 = {}
    for a in arms:
        per = {}
        for s in (401, 402):
            r = net(a, s)
            g = {x: r["auc"][x]["g"] for x in T.SOURCES}
            matters = sum(g[x]["auc"] >= 0.75 and g[x]["ci"][0] > 0.65 for x in T.SOURCES) >= 2
            explains = sum(0.40 <= g[x]["auc"] <= 0.60 for x in T.SOURCES) >= 6
            weak = any(r["auc"]["f_geo"][gg]["auc"] <= 0.55 for gg in ("g224", "g112"))
            per[s] = dict(v="source matters beyond geometry" if matters else ("geometry explains" if explains else "inconclusive"),
                          weak_geo=weak, g={x: g[x]["auc"] for x in T.SOURCES})
        v = per[401]["v"] if per[401]["v"] == per[402]["v"] else "mixed"
        if per[401]["weak_geo"] or per[402]["weak_geo"]:
            v += " [geo reference weak]"
        h5[a] = dict(seeds=per, verdict=v)
    for a, ms in missing.items():
        h5[a] = dict(verdict=f"{NA}: " + ", ".join(f"PN1_{a}_s{x}" for x in ms) + "; the other seed is printed alone (one seed)")
    V["TT-H5"] = h5
    # TT-H6 (descriptive)
    h6 = {}
    for x, y in (("B", "A"), ("Sb", "A"), ("Sb", "B")):
        per = {}
        for s in (401, 402):
            rx, ry = net(x, s)["r5"], net(y, s)["r5"]
            d = {k: rx[k] - ry[k] for k in ("Fbar", "Fbar_noMSU", "Fmax", "S_F", "Abar", "S_A")}
            ci = {k: interval(d[k], [a[k] - b[k] for a, b in zip(rx["_draws"], ry["_draws"])]) for k in d}
            per[s] = dict(diff=d, ci=ci)
        lower = all(per[s]["diff"]["Fbar"] <= -0.03 and per[s]["ci"]["Fbar"][1] < 0 for s in (401, 402))
        h6[f"{x}-{y}"] = dict(seeds=per, sentence=(f"{x} has lower genuine flag rates than {y} on seeds 401/402" if lower
                                                   else "not distinguished on seeds 401/402"))
    V["TT-H6"] = dict(pairs=h6, label="descriptive on seeds 401/402 (two machines); intervals capture image sampling only; "
                                      "no arm, seed or threshold is chosen from TT1")
    return V


def family_ci(r, P, W, L):
    """family-level own-rule share with person-bootstrap interval (inflated for packs), families pooled over sources."""
    out = {}
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    for f in T.FAMILIES:
        xs = [np.array([L[i] for i, _ in P[f"U:{s}"]]) > 0 for s in fam_src[f]]
        ws = [W[f"U:{s}"] for s in fam_src[f]]
        x = np.concatenate(xs); w = np.concatenate(ws, axis=1)
        pt = float(x.mean())
        out[f] = interval(pt, (w @ x) / w.sum(1), INFL.get(f, 1.0))
    r["fam_flag_ci"] = out
    r["fam_flag"] = {f: float(np.concatenate([np.array([L[i] for i, _ in P[f"U:{s}"]]) > 0 for s in fam_src[f]]).mean())
                     for f in T.FAMILIES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--exclude", nargs="*", default=[], help="networks that failed the platform gate (TT1-D3)")
    a = ap.parse_args()
    P, tt = load_pools()
    rng = np.random.default_rng(SEED)
    W = boot_weights(P, rng)
    R = {}
    for n in [x for x in NETS if x not in a.exclude]:
        if a.mock:
            ids = [i for v in P.values() for i, _ in v]
            mr = np.random.default_rng(abs(hash(n)) % 2**32)
            L = {i: float(np.clip(mr.normal(-3.0, 1.2), -3.87, 3.87)) for i in ids}
            for i, _ in P["M_ffhq"]:
                L[i] = float(np.clip(mr.normal(3.0, 1.0), -3.87, 3.87))
            floor, tc = -3.87, -3.6
        else:
            L = {}
            for fam in ("gate", "tt1"):
                z = np.load(pathlib.Path(a.scores) / f"{n}__{fam}.npz")
                L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            floor = head_floor(pathlib.Path(a.nets) / n)
            tc = tau_cam(n)
        r = read_net(L, P, W, tt, floor, tc[0] if isinstance(tc, tuple) else tc)
        r["tau_cam_source"] = tc[1] if isinstance(tc, tuple) else "mock"
        family_ci(r, P, W, L)
        R[n] = r
        print("read", n, flush=True)
    V = verdicts(R)
    for r in R.values():
        r["r5"].pop("_draws", None)
    res = dict(registration="TT1-S (prereg_scoring.md, commit 01557ce; pins ccd6319; deviations TT1-D1, D2, D3)", mock=a.mock,
               excluded_failed_platform_gate=a.exclude, nets=R, verdicts=V,
               counts={k: len(v) for k, v in P.items()})
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(V, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()

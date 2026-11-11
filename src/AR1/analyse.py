"""AR1 / AR2 / AR3 / AR4 reader. Run only after gate_b.json and gate_c.json exist (the gates are computed first).
Decision key: logit_noTTA (rank-equivalent to score_noTTA; fewer ties for the saturated SelfMAD softmax).
Writes experiments/AR1/result_tables.json and prints the tables used in result.md.
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import stats  # noqa: E402

SC = K.OUT / "scores"
REL = [("SelfMAD", "own_selfmad"), ("MADation ViT-B/16", "rel_madation_vitb16"),
       ("MADation ViT-L/14", "rel_madation_vitl14"), ("MixFaceNet-MAD", "rel_mixfacenet_mad_smdd")]
OURS = [(f"M3 s{s}", f"nets_M3_s{s}") for s in range(1, 9)] + [(f"M3L s{s}", f"nets_M3L_s{s}") for s in range(1, 6)]
B = 2000
STEPS = [("R1->R2", "R2", "R0"), ("R2->R3", "R3", "R2"), ("R3->R4", "R4", "R3")]
BONF = (100 * 0.05 / 12 / 2, 100 * (1 - 0.05 / 12 / 2))


def load(tag):
    p = SC / f"scores_{tag}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    S = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
    pe = SC / f"scores_{tag}__extra.npz"                 # the appended R2wm rows (scored in a second pass)
    if pe.exists():
        ze = np.load(pe)
        S.update(zip(ze["id"].tolist(), ze["logit_noTTA"].astype(float)))
    return S


def neutral(r):
    """FRLL genuine photo rows: True for the neutral file (_03); the smiling file differs in capture detail (lead,
    11 Nov: larger files, noisier backdrop) as well as in expression."""
    return "_03" in pathlib.PurePath(r["path"]).name


def cp(k, n, alpha=0.05):
    from scipy.stats import beta
    return [float(beta.ppf(alpha / 2, k, n - k + 1)) if k > 0 else 0.0,
            float(beta.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.0]


def side_verdict(a, c):
    f = stats.fold(a)
    lo, hi = c
    fhi = max(hi, 1 - lo)
    if a < 0.40 and hi < 0.5:
        return "twin artefact, cell invalid"
    if f < 0.60 and fhi < 0.65:
        return "no identity reading"
    if a >= 0.75 and lo > 0.65:
        return "identity reading"
    return "mixed"


def main_verdict(a, c, sh02, sh02_ci):
    f = stats.fold(a)
    fhi = max(c[1], 1 - c[0])
    if a >= 0.75 and c[0] > 0.65 and sh02 <= 0.2:
        return "reads morphing"
    if (sh02_ci[0] is not None and sh02_ci[0] >= 0.5) or (f < 0.60 and fhi < 0.65):
        return "reads the benchmark"
    return "mixed"


class Pool:
    def __init__(self, man, pool):
        self.pool = pool
        self.man = man
        pers = sorted({r["p1"] for r in man if r["pool"] == pool} | {r["p2"] for r in man if r["pool"] == pool})
        self.D = stats.Draw(pers, B, [20261111, 1])

    def rows(self, tool, rung):
        if rung == "R4" and getattr(self, "top_nn", False):   # FRLL clean ladder: R4 = our neutral+neutral morphs
            return [r for r in self.man if r["pool"] == "frll_bridge" and r["tool"] == tool]
        if rung == "R0":
            return [r for r in self.man if r["pool"] == self.pool and r["rung"] == "R0"]
        return [r for r in self.man if r["pool"] == self.pool and r["tool"] == tool and r["rung"] == rung]


def grp(S, rows):
    rows = [r for r in rows if r["id"] in S]
    return np.array([S[r["id"]] for r in rows]), [(r["p1"], r["p2"]) for r in rows]


def contrast(D, S, pos_rows, neg_rows):
    sp, pp = grp(S, pos_rows)
    sn, pn = grp(S, neg_rows)
    if len(sp) == 0 or len(sn) == 0:
        return float("nan"), np.full(D.B, np.nan), len(sp), len(sn)
    rep = stats.wauc_rep(D, sp, pp, sn, pn)
    return stats.auc(sp, sn), rep, len(sp), len(sn)


def eer_thr(b, m):
    K.add_paths(K.W46 / "smadcvpr")
    import a36_read as R36
    return R36.eer_threshold_w(np.asarray(b, float), np.asarray(m, float), np.ones(len(b)))


def bench_threshold(man, S, tool, retrain, neutral_only=True):
    r0, r4 = ("R0f", "R4f") if retrain else ("R0raw", "R4pub")
    b = [S[r["id"]] for r in man if r["pool"] == "frll_bench" and r["rung"] == r0 and r["id"] in S
         and (neutral(r) or not neutral_only)]
    m = [S[r["id"]] for r in man if r["pool"] == "frll_bench" and r["tool"] == tool and r["rung"] == r4 and r["id"] in S]
    if not b or not m:
        return None, None
    return eer_thr(b, m)


def ladder(P, S, tool, man, retrain, base="R2", twin="R3"):
    """steps R0 -> base -> twin -> R4; main contrast base vs R4 (base = R2 tool-on-one-photo, or R2w warp-only);
    twin = R3 (two photos of one person) or R3m (mirror self-morph)."""
    out = {"base": base, "twin": twin}
    reps = {}
    steps = [("R0->" + base, base, "R0"), (base + "->" + twin, twin, base), (twin + "->R4", "R4", twin)]
    extra = [(base + "vsR4", "R4", base), ("R0vsR4", "R4", "R0"), ("NCvsR3", "NC", "R3"), ("R3mvsR3", "R3m", "R3"),
             (base + "->R3", "R3", base), ("R3->R4", "R4", "R3")]
    for name, pos, neg in steps + extra:
        if name in out:
            continue
        a, rep, n1, n0 = contrast(P.D, S, P.rows(tool, pos), P.rows(tool, neg))
        if n1 == 0 or n0 == 0:
            continue
        reps[name] = rep
        out[name] = dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
    dben = stats.dprime(out["R0vsR4"]["auc"])
    drep = np.array([stats.dprime(x) for x in reps["R0vsR4"]])
    for name, _, _ in steps + [(base + "vsR4", "", "")]:
        d = stats.dprime(out[name]["auc"])
        out[name]["share"] = d / dben if dben > 0 else None
        srep = np.array([stats.dprime(x) for x in reps[name]]) / np.where(drep > 0, drep, np.nan)
        out[name]["share_ci95"] = stats.ci(srep)
    m = base + "vsR4"
    s02 = "R0->" + base
    a, c = out[m]["auc"], out[m]["ci95"]
    out["main_verdict"] = main_verdict(a, c, out[s02]["share"], out[s02]["share_ci95"])
    out["p_auc_main_le_0.65"] = float(np.mean(reps[m] <= 0.65))
    out["main_ci_bonferroni12"] = stats.ci(reps[m], *BONF)
    out["side_twin_vs_R4"] = side_verdict(out[twin + "->R4"]["auc"], out[twin + "->R4"]["ci95"])
    out["side_base_vs_twin"] = side_verdict(out[base + "->" + twin]["auc"], out[base + "->" + twin]["ci95"])
    t, e = bench_threshold(man, S, tool, retrain)
    if t is not None:
        out["bench_threshold"] = dict(t=t, bench_eer=100 * e)
        for g in ("R0", "R2", "R2w", "R2wm", "R3", "R3m", "R4", "NC"):
            s_, _ = grp(S, P.rows(tool, g))
            if len(s_):
                k = int((s_ >= t).sum())
                out["bench_threshold"][f"flag_rate_{g}"] = [k / len(s_), cp(k, len(s_))]
    return out, reps


def bench_block(man, S, tool, retrain):
    P = Pool(man, "frll_bench")
    o = {}
    for gen in ("neutral_only", "all_photos"):
        def rows(g, t=tool):
            return [r for r in man if r["pool"] == "frll_bench" and r["rung"] == g and
                    (r["tool"] == t or g in ("R0raw", "R0f")) and
                    (gen == "all_photos" or g not in ("R0raw", "R0f", "R1f") or neutral(r))]
        pairs = [("R1f_vs_R0f (E7 step)", "R1f", "R0f"), ("R4f_vs_R0f", "R4f", "R0f"), ("R4f_vs_R1f", "R4f", "R1f")]
        if not retrain:
            pairs = [("R4pub_vs_R0raw (benchmark, raw files)", "R4pub", "R0raw")] + pairs
        og = o.setdefault(gen, {})
        for name, pos, neg in pairs:
            a, rep, n1, n0 = contrast(P.D, S, rows(pos), rows(neg))
            og[name] = dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
        a1, a4 = og["R1f_vs_R0f (E7 step)"]["auc"], og["R4f_vs_R0f"]["auc"]
        og["E7_share_of_R4f_vs_R0f"] = stats.dprime(a1) / stats.dprime(a4) if stats.dprime(a4) > 0 else None
        t, e = bench_threshold(man, S, tool, retrain, neutral_only=(gen == "neutral_only"))
        if t is not None:
            og["bench_eer"] = 100 * e
            og["bench_threshold"] = t
    rows = lambda g, t=tool: [r for r in man if r["pool"] == "frll_bench" and r["rung"] == g and r["tool"] == t]  # noqa
    # bridge: published vs our same-pair morphs (published positive)
    PB = Pool(man, "frll_bridge")
    pub = "R4f" if retrain else "R4pub"
    ours = [r for r in man if r["pool"] == "frll_bridge" and r["tool"] == tool]
    pubr = rows(pub)
    pers = sorted({r["p1"] for r in ours + pubr} | {r["p2"] for r in ours + pubr})
    D = stats.Draw(pers, B, [20261111, 4])
    sp, pp = grp(S, pubr)
    so, po = grp(S, ours)
    rep = stats.wauc_rep(D, sp, pp, so, po)
    o["bridge_pub_vs_ours"] = dict(auc=stats.auc(sp, so), ci95=stats.ci(rep), n_pub=len(sp), n_ours=len(so),
                                   frames="published raw-file crops vs our 512 tool-size crops" if not retrain
                                   else "published prep_eval frames vs our 73_delin frames (different frame pipelines)")
    t = o["neutral_only"].get("bench_threshold")
    if t is not None:
        o["detect_rate_published"] = float((sp >= t).mean())
        o["detect_rate_ours"] = float((so >= t).mean())
        o["bridge_ok"] = bool(0.40 <= o["bridge_pub_vs_ours"]["auc"] <= 0.60 and
                              abs(o["detect_rate_published"] - o["detect_rate_ours"]) <= 0.10)
    del PB
    return o


def graded(man, S):
    from scipy.stats import page_trend_test
    P = Pool(man, "frgcferet")
    G = [r for r in man if r["rung"] == "G" and r["id"] in S]
    lv = sorted({float(r["level"]) for r in G})
    hosts = sorted({r["p1"] for r in G})
    M = {(r["p1"], float(r["level"])): S[r["id"]] for r in G}
    X = np.array([[M[(h, m)] for m in lv] for h in hosts])
    pt = page_trend_test(X, predicted_ranks=list(range(1, len(lv) + 1)))
    o = dict(levels=lv, n_hosts=len(hosts), mean_logit=X.mean(0).tolist(), median_logit=np.median(X, 0).tolist(),
             page_L=float(pt.statistic), page_p=float(pt.pvalue), monotone=bool(pt.pvalue < 0.05))
    base = [r for r in G if float(r["level"]) == 0.0]
    o["auc_vs_m0"] = {}
    for m in lv[1:]:
        pos = [r for r in G if float(r["level"]) == m]
        a, rep, _, _ = contrast(P.D, S, pos, base)
        o["auc_vs_m0"][str(m)] = dict(auc=a, ci95=stats.ci(rep))
    return o


def baseline_compare(man, S, P, tool, contrast_name, pos, neg, oofz):
    best, best_rep, best_key = None, None, None
    for b in ("bytes", "border", "background"):
        key = f"{P.pool}|{tool}|{pos}vs{neg}|{b}"
        if key + "|id" not in oofz:
            continue
        sc = dict(zip(oofz[key + "|id"].tolist(), oofz[key + "|score"].astype(float)))
        a, rep, _, _ = contrast(P.D, sc, P.rows(tool, pos), P.rows(tool, neg))
        if a < 0.5:
            a, rep = 1 - a, 1 - rep
        if best is None or a > best:
            best, best_rep, best_key = a, rep, b
    da, drep, _, _ = contrast(P.D, S, P.rows(tool, pos), P.rows(tool, neg))
    diff = drep - best_rep
    return dict(best_noncontent=best_key, best_auc=best, detector_auc=da, diff=da - best, diff_ci95=stats.ci(diff),
                beats=bool(stats.ci(diff)[0] > 0))


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    assert (K.RES / "gate_b.json").exists() and (K.RES / "gate_c.json").exists(), "gates first"
    oofz = dict(np.load(SC / "baselines_oof.npz"))
    pools = {p: Pool(man, p) for p in ("frgcferet", "frll")}
    res = {}
    for block, dets in (("released", REL), ("our_retrain", OURS)):
        for name, tag in dets:
            S = load(tag)
            if S is None:
                print("missing", tag)
                continue
            retrain = block == "our_retrain"
            r = res.setdefault(name, dict(block=block, tag=tag))
            for pool, P in pools.items():
                for tool in ("opencv", "facemorpher"):
                    for base, twin in (("R2", "R3"), ("R2w", "R3"), ("R2w", "R3m"), ("R2wm", "R3m")):
                        lad, _ = ladder(P, S, tool, man, retrain, base, twin)
                        if pool == "frll":
                            lad["label"] = ("confounded by capture detail and expression (R4 partner, and R2w / R3 "
                                            "where used, involve a smiling FRLL file); verdict rules not applied")
                            lad["main_verdict"] = lad["side_twin_vs_R4"] = lad["side_base_vs_twin"] = "not applied"
                        else:
                            lad["vs_best_noncontent_main"] = baseline_compare(man, S, P, tool, base + "vsR4", "R4",
                                                                              base, oofz)
                        r[f"{pool}/{tool}/{base}-{twin}"] = lad
                    if pool == "frll":
                        PC = Pool(man, "frll")
                        PC.top_nn = True
                        lad, _ = ladder(PC, S, tool, man, retrain, "R2wm", "R3m")
                        lad["label"] = ("FRLL clean ladder, neutral files only: R0 neutral photo, R2wm warp toward its "
                                        "own mirrored shape, R3m mirror self-morph, R4 = our neutral+neutral two-person "
                                        "morphs of the published pairs (bridge set); secondary pool, descriptive")
                        r[f"frll_clean/{tool}/R2wm-R3m-R4nn"] = lad
            for tool in ("opencv", "facemorpher"):
                r[f"frll_bench/{tool}"] = bench_block(man, S, tool, retrain)
            r["AR2_graded_fm"] = graded(man, S)
            if not retrain:
                for v in ("bg", "face"):
                    Sv = load(f"{tag}__{v}")
                    if Sv is None:
                        continue
                    for tool in ("opencv", "facemorpher"):
                        P = pools["frgcferet"]
                        o = {}
                        for cn, pos, neg in (("R2vsR4", "R4", "R2"), ("R2wvsR4", "R4", "R2w"), ("R0vsR4", "R4", "R0"),
                                             ("R3vsR4", "R4", "R3"), ("R0vsR2w", "R2w", "R0")):
                            a, rep, n1, n0 = contrast(P.D, Sv, P.rows(tool, pos), P.rows(tool, neg))
                            o[cn] = dict(auc=a, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
                        o["works"] = bool(o["R2wvsR4"]["auc"] >= 0.75 and o["R2wvsR4"]["ci95"][0] > 0.65)
                        r[f"AR4_{v}_blanked/frgcferet/{tool}"] = o
            print("done", name, flush=True)
    json.dump(res, open(K.RES / "result_tables.json", "w"), indent=1)


if __name__ == "__main__":
    main()

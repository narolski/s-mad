"""AD1 step 1: post hoc ladder re-read of the A43 MorDIFF scores (no new images, no rescoring).

Bootstrap = the pigeonhole (dyadic) person bootstrap of mambamorph-code smadcvpr/a41_read.py (class Draw), weighted
Mann-Whitney AUC of a36_read.wauc, both re-implemented here verbatim; checked against A43's printed numbers.
Run: python3 -I src/AD1/ad1_read.py [--smoke] (uses the spark venv's numpy/scipy).
"""
import csv, hashlib, json, math, pathlib, re, sys
import numpy as np
from scipy.stats import norm, beta

MC = pathlib.Path("/home/narolski/mambamorph-code")
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
MAN = A43 / "data/manifests/a43.csv"
MAN_SHA = "ce3a264adb30928d6ae3abfb63619ed4b35fcb0ebb7fcca7e5001b212a5df4b8"
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/AD1")
SEED = [20261107, 43, 1]          # the A43 reader's draw (to reproduce its intervals)
B = 10000
SMOKE = "--smoke" in sys.argv

# label, a43 score file, a43 key, eval score file (for R1 = E7), eval key, role
DETS = [
    ("MADation ViT-B/16 release", "madation_vitb16/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz", "score_noTTA", "primary"),
    ("MADation ViT-L/14 release", "madation_vitl14/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz", "score_noTTA", "primary"),
    ("SelfMAD release, own preprocessing", "selfmad_hrnet_w18/own", "score", "experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", "score", "primary"),
    ("SelfMAD release, our pipeline", "selfmad_hrnet_w18/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/selfmad_hrnet_w18/scores_eval.npz", "score_noTTA", "descriptive"),
    ("MADation FE ViT-B/16 release", "madation_fe_vitb16/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_fe_vitb16/scores_eval.npz", "score_noTTA", "descriptive"),
    ("MADation FE ViT-L/14 release", "madation_fe_vitl14/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_fe_vitl14/scores_eval.npz", "score_noTTA", "descriptive"),
    ("MADation FS ViT-B/16 release", "madation_fs_vitb16/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_fs_vitb16/scores_eval.npz", "score_noTTA", "descriptive"),
    ("MADation FS ViT-L/14 release", "madation_fs_vitl14/rel", "score_noTTA", "smadcvpr_runs/A12_scored/A12REL/madation_fs_vitl14/scores_eval.npz", "score_noTTA", "descriptive"),
]
# published MorDIFF EER (%) as recorded in the programme (CONCLUSIONS.md l.23, l.128); None = not in the record
PUBLISHED = {"MADation ViT-B/16 release": 1.10, "MADation ViT-L/14 release": 19.3}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def dprime(auc):
    return float(np.sqrt(2) * norm.ppf(np.clip(auc, 0.005, 0.995)))


def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    return (wp * (below + 0.5 * tie)).sum(1) / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


class Draw:
    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, pp):
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[-1]] for p in pp])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        w[:, same] = self.C[:, a[same]]
        return w


def eer_thr(b, m):
    """EER (%) and threshold (flag = score >= t), unit weights, t over all scores."""
    t = np.unique(np.r_[b, m])
    fpr = np.array([(b >= x).mean() for x in t])
    fnr = np.array([(m < x).mean() for x in t])
    i = int(np.argmin(np.abs(fpr - fnr)))
    return 100 * (fpr[i] + fnr[i]) / 2, float(t[i])


def cp(k, n):
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return [float(lo), float(hi)]


RXB = re.compile(r"^(\d{3})_(\d{2})_")
RXM = re.compile(r"^morph_(\d{3})_\d{2}_and_(\d{3})_\d{2}")


def pers_eval(r):
    n = pathlib.PurePath(r["path"]).name
    if r["label"] == "0":
        return (RXB.match(n).group(1),)
    m = RXM.match(n)
    return (m.group(1), m.group(2))


def pers_a43(r):
    if r["source"] == "eval":
        return pers_eval(r)
    if r["src_b"]:
        return (r["src_a"][:3], r["src_b"][:3])
    return (r["src_a"][:3],)


def main():
    assert sha(MAN) == MAN_SHA and sha(EVAL) == EVAL_SHA
    rows = list(csv.DictReader(open(MAN)))
    ev = [r for r in csv.DictReader(open(EVAL)) if r["set"] == "mordiff"]
    groups = {}
    for i, r in enumerate(rows):
        k = r["arm"] if r["source"] == "a43" else {"mordiff_bona": "R0", "mordiff": "A_reg"}.get(r["family"], "frll_bona")
        groups.setdefault(k, []).append(i)
    e7 = [r for r in ev if r["family"] == "mordiff" and r["variant"] == "resmatch"]
    # ---------------- G-b (before any score): glint cosines of the A43 manifest
    thr = json.load(open(A43 / "data/a43_stats.json"))["g2_identity"]["thr_fmr_1e-3"]
    f = lambda x: float(x) if x != "" else np.nan  # noqa: E731
    mn = lambda ii: np.array([min(f(rows[i]["cos_stored_raw_a"]), f(rows[i]["cos_stored_raw_b"])) for i in ii])  # noqa: E731
    mB, mC = mn(groups["B20"]), mn(groups["C20"])
    gb = {"thr_fmr_1e-3": thr,
          "oracle_auc_morph_vs_twin (lower min-cosine = morph)": float(((mC[:, None] > mB[None, :]).mean() + 0.5 * (mC[:, None] == mB[None, :]).mean())),
          "B20_verifies_both": float(np.mean(mB >= thr)), "C20_verifies_A": float(np.mean([f(rows[i]["cos_stored_raw_a"]) >= thr for i in groups["C20"]])),
          "negative_control_twin(A,A')_vs_twin(A',A)": "not available (one twin per person)"}
    gb["pass"] = gb["oracle_auc_morph_vs_twin (lower min-cosine = morph)"] >= 0.90 and gb["B20_verifies_both"] >= 0.70 and gb["C20_verifies_A"] >= 0.9
    print("G-b", gb, flush=True)
    # ---------------- persons and draw (the A43 reader's: every person of the manifest, sorted)
    allp = sorted({p for r in rows for p in pers_a43(r)})
    D = Draw(allp, 200 if SMOKE else B, SEED)
    P = {k: [pers_a43(rows[i]) for i in v] for k, v in groups.items()}
    P["R1"] = [pers_eval(r) for r in e7]
    W = {k: D.w(v) for k, v in P.items()}
    res = {"G-b": gb, "persons": len(allp), "B": D.C.shape[0], "seed": SEED, "detectors": {}}
    csv_rows = []
    for lab, a43f, k43, evf, kev, role in DETS:
        z = np.load(A43 / "a43_out/a43" / a43f / "scores_a43.npz", allow_pickle=False)
        assert str(z["manifest_sha256"]) == MAN_SHA and list(z["id"]) == [r["id"] for r in rows]
        s = z[k43].astype(np.float64)
        ze = np.load(MC / evf, allow_pickle=False)
        assert str(ze["manifest_sha256"]) == EVAL_SHA
        em = dict(zip(ze["id"].tolist(), ze[kev].astype(np.float64)))
        S = {k: s[np.array(v)] for k, v in groups.items()}
        S["R1"] = np.array([em[r["id"]] for r in e7])
        # consistency: a43 re-score of the registered MorDIFF bona fide frames vs the eval file
        cons = float(np.max(np.abs(S["R0"] - np.array([em[rows[i]["id"]] for i in groups["R0"]]))))
        if SMOKE:
            S = {k: v[:8] for k, v in S.items()}
            Wk = {k: v[:, :8] for k, v in W.items()}
        else:
            Wk = W

        def C(pa, pb):
            pt = float(wauc(S[pa], S[pb], np.ones((1, len(S[pa]))), np.ones((1, len(S[pb]))))[0])
            rep = wauc(S[pa], S[pb], Wk[pa], Wk[pb])
            return pt, rep
        con = {"bench R4pub vs R0": ("A_reg", "R0"), "bridge A vs B20": ("A", "B20"),
               "R0->R1 (R1 vs R0)": ("R1", "R0"), "R1->R2 (D20 vs R1)": ("D20", "R1"), "R0->R2 (D20 vs R0)": ("D20", "R0"),
               "R2->R3 (C20 vs D20)": ("C20", "D20"), "R3->R4 (B20 vs C20)": ("B20", "C20"),
               "main R2 vs R4 (B20 vs D20)": ("B20", "D20"), "R2 vs R4pub (A vs D20)": ("A", "D20"),
               "bench ours R4 vs R0 (B20 vs R0)": ("B20", "R0"),
               "desc E vs R0": ("E", "R0"), "desc D100 vs R0": ("D", "R0"), "desc C20 vs R0": ("C20", "R0")}
        out = {}
        for nm, (pa, pb) in con.items():
            pt, rep = C(pa, pb)
            fold = 0.5 + np.abs(rep - 0.5)
            out[nm] = {"auc": pt, "ci95": [float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))],
                       "fold": 0.5 + abs(pt - 0.5), "fold_ub95": float(np.percentile(fold, 97.5)), "dprime": dprime(pt), "_rep": rep}
        bpt, brep = out["bench R4pub vs R0"]["auc"], out["bench R4pub vs R0"]["_rep"]
        dbr = np.sqrt(2) * norm.ppf(np.clip(brep, 0.005, 0.995))
        shares = {}
        for nm in ("R0->R1 (R1 vs R0)", "R1->R2 (D20 vs R1)", "R0->R2 (D20 vs R0)", "R2->R3 (C20 vs D20)", "R3->R4 (B20 vs C20)", "main R2 vs R4 (B20 vs D20)"):
            dr = np.sqrt(2) * norm.ppf(np.clip(out[nm]["_rep"], 0.005, 0.995))
            ok = dbr > 0
            sh = dr[ok] / dbr[ok]
            shares[nm] = {"point": dprime(out[nm]["auc"]) / dprime(bpt) if dprime(bpt) > 0 else None,
                          "ci95": [float(np.percentile(sh, 2.5)), float(np.percentile(sh, 97.5))] if ok.any() else None}
        # verdicts (11_AUDIT_PLAN.md, fixed rules)
        m_ = out["main R2 vs R4 (B20 vs D20)"]
        s02 = shares["R0->R2 (D20 vs R0)"]
        if m_["auc"] >= 0.75 and m_["ci95"][0] > 0.65 and s02["point"] is not None and s02["point"] <= 0.2:
            main_v = "reads morphing"
        elif (s02["ci95"] is not None and s02["ci95"][0] >= 0.5) or (m_["fold"] < 0.60 and m_["fold_ub95"] < 0.65):
            main_v = "reads the benchmark"
        else:
            main_v = "mixed"

        def side(o):
            if o["auc"] < 0.40 and o["ci95"][1] < 0.5:
                return "twin artefact, cell invalid"
            if o["fold"] < 0.60 and o["fold_ub95"] < 0.65:
                return "no identity reading"
            if o["auc"] >= 0.75 and o["ci95"][0] > 0.65:
                return "identity reading"
            return "mixed"
        eer, t = eer_thr(S["R0"], S["A_reg"])
        k = int((S["C20"] >= t).sum())
        gfl = {"eer_ours_pct": eer, "published_pct": PUBLISHED.get(lab)}
        gfl["G-a"] = ("not in record" if gfl["published_pct"] is None else
                      ("pass" if abs(eer - gfl["published_pct"]) <= 3 else "fail: not reproduced, descriptive"))
        R = {"role": role, "consistency_R0_a43_vs_eval_maxabs": cons, "G-a": gfl,
             "contrasts": {k_: {kk: vv for kk, vv in v.items() if kk != "_rep"} for k_, v in out.items()},
             "shares": shares, "verdict_main": main_v,
             "verdict_side_R3_vs_R4": side(out["R3->R4 (B20 vs C20)"]), "verdict_side_R2_vs_R3": side(out["R2->R3 (C20 vs D20)"]),
             "twin_flag_rate_at_bench_eer_thr": {"k": k, "n": len(S["C20"]), "rate": k / len(S["C20"]), "cp95": cp(k, len(S["C20"]))},
             "recon_flag_rate_at_bench_eer_thr": float((S["D20"] >= t).mean()),
             "R1_flag_rate_at_bench_eer_thr": float((S["R1"] >= t).mean())}
        res["detectors"][lab] = R
        for k_, v in out.items():
            csv_rows.append([lab, k_, f"{v['auc']:.3f}", f"{v['ci95'][0]:.3f}", f"{v['ci95'][1]:.3f}", f"{v['dprime']:.2f}",
                             "" if k_ not in shares or shares[k_]["point"] is None else f"{shares[k_]['point']:.2f}",
                             "" if k_ not in shares or shares[k_]["ci95"] is None else f"{shares[k_]['ci95'][0]:.2f}",
                             "" if k_ not in shares or shares[k_]["ci95"] is None else f"{shares[k_]['ci95'][1]:.2f}"])
        print(lab, main_v, R["verdict_side_R3_vs_R4"], R["verdict_side_R2_vs_R3"], {k_: round(v["auc"], 3) for k_, v in out.items()}, flush=True)
    if SMOKE:
        print("smoke ok")
        return
    json.dump(res, open(OUT / "ad1_ladder.json", "w"), indent=1)
    with open(OUT / "ad1_ladder.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "contrast", "auc", "lo95", "hi95", "dprime", "share_of_bench", "share_lo95", "share_hi95"])
        w.writerows(csv_rows)


if __name__ == "__main__":
    main()

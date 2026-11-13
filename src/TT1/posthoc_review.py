"""Threshold transfer on unseen genuine sources (TT1): POST HOC, descriptive recomputations requested by the review
REVIEW_TT1_20261113.md (F1-F8). No registered verdict is computed here except the re-check of the verdicts under the
reader correction (lower bounds clipped at 0; Clopper-Pearson printed beside zero-event families), which must leave every
verdict unchanged. Scores: the tt1c result (gate passed). Output: experiments/TT1_.../posthoc_review.json
  python -I posthoc_review.py"""
import csv
import json
import pathlib
import sys

import numpy as np
from scipy.stats import beta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

S = pathlib.Path("/mnt/t7/smad_next/TT1/results/unpacked_tt1c/TT1_A100_tt1c_full/scores")
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb", "C", "Bv") for s in (401, 402)] + ["PN1_Bn_s402"]
INFL = {"lfw_calfw": 1.18, "cfp_ff": 1.78, "agedb_30": 2.03}


def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def main():
    lst = list(csv.DictReader(open(T.OUT / "tt1_score.csv")))
    tt = {r["id"]: r for r in T.tt1_rows()}
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    U = {f: [r["id"] for r in lst if r["rung"] in fam_src[f] and tt[r["id"]]["primary"]] for f in T.FAMILIES}
    cam = {r["id"]: r for r in lst if r["rung"] == "R_cam"}
    ffq = [r["id"] for r in lst if r["rung"] == "R_ffhq"]
    geo = {g: {r["strength"]: r["id"] for r in lst if r["rung"] == f"R_cam_geo{g[1:]}"} for g in ("g224", "g112")}
    bcam = {}
    for r in lst:
        if r["rung"] == "R_cam_border":
            bcam.setdefault(r["cell"], {})[r["id"].split("__")[0][len("bref_"):]] = r["id"]
    bff = {r["id"][len("bref_"):]: r["id"] for r in lst if r["rung"] == "R_ffhq_border"}
    read = json.load(open(T.RES / "tt1_read.json"))
    out = dict(label="POST HOC, descriptive (review REVIEW_TT1_20261113.md); not registered reads", nets={})
    for n in NETS:
        L = {}
        for fam in ("gate", "tt1"):
            z = np.load(S / f"{n}__{fam}.npz")
            L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        g = lambda ids: np.array([L[i] for i in ids])
        camv = g(list(cam))
        cm = float(np.median(camv))
        allU = np.concatenate([g(U[f]) for f in T.FAMILIES])
        o = dict(
            R_cam_p05_p95=[float(np.percentile(camv, 5)), float(np.percentile(camv, 95))], R_cam_median=cm,
            unseen_family_median_minus_cam={f: float(np.median(g(U[f])) - cm) for f in T.FAMILIES},
            unseen_p95=float(np.percentile(allU, 95)), unseen_median=float(np.median(allU)),
            u=read["nets"][n]["u"],
            Fbar_at={str(t): float(np.mean([np.mean(g(U[f]) > t) for f in T.FAMILIES])) for t in (0, -0.5, -1, -2)})
        o["unseen_family_median_minus_cam_in_u"] = {f: v / o["u"] for f, v in o["unseen_family_median_minus_cam"].items()}
        for gg in ("g224", "g112"):
            ids = list(cam)
            d = np.array([L[geo[gg][i]] - L[i] for i in ids])
            o[f"geo_{gg}"] = dict(flag=float(np.mean(g([geo[gg][i] for i in ids]) > 0)), paired_median_shift=float(np.median(d)))
        o["border_cam_paired_median_shift"] = {f: float(np.median([L[bcam[f][i]] - L[i] for i in cam])) for f in T.FAMILIES}
        o["border_cam_flag"] = {f: float(np.mean([L[bcam[f][i]] > 0 for i in cam])) for f in T.FAMILIES}
        o["border_share_of_unseen_excess"] = {f: o["border_cam_paired_median_shift"][f] / o["unseen_family_median_minus_cam"][f]
                                              for f in T.FAMILIES}
        o["border_ffhq_paired_median_shift"] = float(np.median([L[bff[i]] - L[i] for i in ffq]))
        o["ffhq_flag"] = float(np.mean(g(ffq) > 0))
        o["ffhq_border_flag"] = float(np.mean(g([bff[i] for i in ffq]) > 0))
        # reader correction: clip lower bounds at 0; Clopper-Pearson beside zero-event families
        fam = {}
        for f in T.FAMILIES:
            x = g(U[f]) > 0
            ci = read["nets"][n]["fam_flag_ci"][f]
            fam[f] = dict(flag=float(x.mean()), k=int(x.sum()), n=len(x), boot_ci_clipped=[max(0.0, ci[0]), ci[1]],
                          cp=cp(int(x.sum()), len(x)), zero_event=bool(x.sum() == 0))
        o["family_flag_corrected"] = fam
        out["nets"][n] = o
    # Sb - B and Bv - B at cut-offs, per seed
    out["arm_cutoffs"] = {}
    for s in ("401", "402"):
        for t in ("0", "-0.5", "-1", "-2"):
            fb = {a: out["nets"][f"PN1_{a}_s{s}"]["Fbar_at"][t] for a in ("A", "B", "Sb", "Bv")}
            out["arm_cutoffs"][f"s{s}_t{t}"] = dict(Sb_minus_B=fb["Sb"] - fb["B"], Bv_minus_B=fb["Bv"] - fb["B"],
                                                     B_minus_A=fb["B"] - fb["A"])
    # verdict re-check under the reader correction (TT-H1 is the only rule using lower bounds)
    chk = {}
    for a in ("A", "B", "Sb", "C", "Bv"):
        per = {}
        for s in ("401", "402"):
            fam = out["nets"][f"PN1_{a}_s{s}"]["family_flag_corrected"]
            per[s] = dict(fails=[f for f in T.FAMILIES if fam[f]["boot_ci_clipped"][0] > 0.05],
                          all_upper_le_10=all(fam[f]["boot_ci_clipped"][1] <= 0.10 for f in T.FAMILIES),
                          all_cp_upper_le_10=all(fam[f]["cp"][1] <= 0.10 for f in T.FAMILIES),
                          max_cp_upper=max(fam[f]["cp"][1] for f in T.FAMILIES))
        reg = read["verdicts"]["TT-H1"][a]
        same = all(sorted(per[s]["fails"]) == sorted(reg["seeds"][s]["fails"]) and
                   per[s]["all_upper_le_10"] == reg["seeds"][s]["all_upper_le_10"] for s in ("401", "402"))
        chk[a] = dict(corrected=per, registered_verdict=reg["verdict"], unchanged=bool(same))
    out["TT-H1_recheck_after_clip"] = chk
    # Sb margins (F5)
    out["Sb_margins"] = {f"s{s}": {f: out["nets"][f"PN1_Sb_s{s}"]["family_flag_corrected"][f]["boot_ci_clipped"][0]
                                   for f in ("agedb_30", "cfp_ff", "oulu_npu")} for s in ("401", "402")}
    (T.RES / "posthoc_review.json").write_text(json.dumps(out, indent=1))
    for n, o in out["nets"].items():
        print(n, "geo112 %.3f shift %+.2f | geo224 %.3f shift %+.2f | Rcam p5-95 %.2f..%.2f | p95 %.2f | border shift %s | ffhq %.3f->%.3f (%+.2f)" % (
            o["geo_g112"]["flag"], o["geo_g112"]["paired_median_shift"], o["geo_g224"]["flag"], o["geo_g224"]["paired_median_shift"],
            o["R_cam_p05_p95"][0], o["R_cam_p05_p95"][1], o["unseen_p95"],
            {f[:4]: round(v, 2) for f, v in o["border_cam_paired_median_shift"].items()}, o["ffhq_flag"], o["ffhq_border_flag"],
            o["border_ffhq_paired_median_shift"]))
    print(json.dumps(out["arm_cutoffs"], indent=0))
    print(json.dumps({a: (v["unchanged"], v["registered_verdict"], {s: v["corrected"][s]["max_cp_upper"] for s in v["corrected"]}) for a, v in chk.items()}, indent=0))
    print(out["Sb_margins"])


if __name__ == "__main__":
    main()

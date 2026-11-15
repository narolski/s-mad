"""Amendment 9 reader: (a) released-detector S0 vs S4 (OpenCV-style only) as excess over the PN1 3-statistic floor
(fitted on PN1 development hosts; scores from posthoc2.floor3 saved in OUT/floor3_pn1.json), on non-development,
non-validation hosts; S0 vs S4 within tone-matched fifths. (b) S4 vs swap-splice SW. -> experiments/AR1/sp_floor.json"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import analyse as A  # noqa: E402
import stats  # noqa: E402

PN1 = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests")


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    sp = [r for r in csv.DictReader(open(K.OUT / "manifest_splice2.csv")) if r["variant"] == "native" and r["tool"] == "opencv"]
    sw = list(csv.DictReader(open(K.OUT / "manifest_swap.csv")))
    role = {r["pid"]: r["role"] for r in csv.DictReader(open(PN1 / "split/ladder_split.csv"))}
    fl = json.load(open(K.OUT / "floor3_pn1.json"))
    F = fl["scores"]
    zt = np.load("/mnt/t7/smad_next/PN1/cues/tone_splice.npz")
    tone = {str(i): float(v[0]) for i, v in zip(zt["ids"], zt["tone"])}
    ev = lambda r: role.get(r["p1"]) not in ("dev", "val") and r["p1"] in role  # noqa
    P = A.Pool(man, "frgcferet")
    D = P.D
    s4 = [r for r in sp if r["rung"] == "S4" and ev(r)]
    s0 = [r for r in sp if r["rung"] == "S0" and ev(r)]
    out = {"floor_info": fl["info"], "n_eval_hosts": len({r["p1"] for r in s4}), "detectors": {}}
    fa, frep, _, _ = A.contrast(D, F, s4, s0)
    out["floor_auc_eval"] = dict(auc=fa, ci95=stats.ci(frep))
    # tone quintiles over S0 and S4 pooled
    tv = np.array([tone[r["id"]] for r in s4 + s0])
    edges = np.quantile(tv, [0.2, 0.4, 0.6, 0.8])
    q = {r["id"]: int(np.digitize(tone[r["id"]], edges)) for r in s4 + s0}
    for name, tag in A.REL:
        S = A.load(f"{tag}__splice2")
        Sw = A.load(f"{tag}__swap") or {}
        da, drep, _, _ = A.contrast(D, S, s4, s0)
        o = dict(S0_vs_S4=dict(auc=da, ci95=stats.ci(drep)),
                 excess_over_floor=dict(excess=da - fa, ci95=stats.ci(drep - frep)))
        num = den = 0.0
        cells = []
        for k in range(5):
            p_ = [S[r["id"]] for r in s4 if q[r["id"]] == k and r["id"] in S]
            n_ = [S[r["id"]] for r in s0 if q[r["id"]] == k and r["id"] in S]
            if len(p_) >= 10 and len(n_) >= 10:
                a_ = stats.auc(p_, n_)
                w = min(len(p_), len(n_))
                num += w * a_
                den += w
                cells.append(dict(fifth=k, auc=a_, n_s4=len(p_), n_s0=len(n_)))
        o["tone_matched_auc"] = num / den if den else None
        o["tone_matched_drop"] = da - o["tone_matched_auc"] if den else None
        o["tone_cells"] = cells
        if Sw:
            all4 = [r for r in sp if r["rung"] == "S4"]
            a_, rep, n1, n0 = A.contrast(D, {**S, **Sw}, all4, sw)
            o["S4_vs_SW"] = dict(auc=a_, ci95=stats.ci(rep), n_pos=n1, n_neg=n0)
        out["detectors"][name] = o
    # seam statistics summary
    rows = list(csv.DictReader(open(K.RES / "swap_seam.csv")))
    summ = {}
    for arm in ("S4", "S0", "SW"):
        v = np.array([[abs(float(x["tone_luma"])), abs(float(x["tone_rg"])), float(x["abs_step"])] for x in rows if x["arm"] == arm])
        summ[arm] = dict(median_abs_tone_luma=float(np.median(v[:, 0])), median_abs_tone_rg=float(np.median(v[:, 1])),
                         median_abs_step=float(np.median(v[:, 2])))
    out["seam"] = summ
    json.dump(out, open(K.RES / "sp_floor.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "detectors"}, indent=1))
    for n, o in out["detectors"].items():
        print(n, {k: (round(v["auc"], 3), [round(x, 3) for x in v["ci95"]]) for k, v in o.items() if isinstance(v, dict) and "auc" in v},
              "excess", round(o["excess_over_floor"]["excess"], 3), [round(x, 3) for x in o["excess_over_floor"]["ci95"]],
              "tone-matched", round(o["tone_matched_auc"], 3), "drop", round(o["tone_matched_drop"], 3))


if __name__ == "__main__":
    main()

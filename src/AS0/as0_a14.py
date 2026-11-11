"""Mirror-asymmetry test (AS0), amendment A14: the geometry-matched warp-only reference R2w4 (review H-new-1, H-new-2).
  python3 -I as0_a14.py -> experiments/AS0_mirror-asymmetry/a14.json, a14.csv
Y, F0, both engines pooled (and per engine); AUC = P(L(X) < L(Y)); pigeonhole person bootstrap B = 2000, seed
[20261111, 61]. Typicality on detected landmarks with the ID0 statistic imported unchanged (as as0_typ.py).
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_analyse as A  # noqa: E402
import as0_common as K  # noqa: E402
import as0_measure as M  # noqa: E402

BANDS = ["B1", "B2", "B3", "B4", "B5", "BB"]


def main():
    D = A.Data()
    rows, res = [], {}
    tools = {"pooled": ["opencv", "facemorpher"], "opencv": ["opencv"], "facemorpher": ["facemorpher"]}
    pool = [r["pid"] for r in K.read_csv(K.AR1 / "pool.csv")]
    for sub, tl in tools.items():
        for drop in (False, True):
            g = {}
            for rung in ("R2w", "R2w4", "R3", "R4"):
                g[rung] = [f"L|{p}|{t}|{rung}" for t in tl for p in pool
                           if D.ok(f"L|{p}|{t}|{rung}") and not (drop and D.isval(f"L|{p}|{t}|{rung}"))]
            Dr = A.draw_for(D, g["R2w"] + g["R2w4"] + g["R3"] + g["R4"], 2000)
            for name, X, Y in (("R2w4 vs R2w", g["R2w4"], g["R2w"]), ("R4 vs R2w4", g["R4"], g["R2w4"]),
                               ("R3 vs R2w", g["R3"], g["R2w"]), ("R4 vs R3", g["R4"], g["R3"]),
                               ("R2w4 vs R3", g["R2w4"], g["R3"])):
                for b in BANDS:
                    rows.append(dict(contrast=name, engine=sub, is_val_dropped=int(drop), band=b,
                                     **A.auc_ci(Dr, D, X, Y, band=b)))
            # paired per host and engine
            hosts = [(p, t) for t in tl for p in pool if all(D.ok(f"L|{p}|{t}|{r}") for r in ("R2w", "R2w4", "R3", "R4"))
                     and not (drop and any(D.isval(f"L|{p}|{t}|{r}") for r in ("R4", "R3")))]
            W = A.ST.weights(Dr, [(p,) for p, _ in hosts])
            for b in BANDS:
                v = {r: np.array([D.val([f"L|{p}|{t}|{r}"], band=b)[0] for p, t in hosts]) for r in ("R2w", "R2w4", "R3", "R4")}
                geo = v["R2w4"] - v["R2w"]
                gap = v["R4"] - v["R3"]
                Dd = (v["R4"] - v["R2w4"]) - (v["R3"] - v["R2w"])
                ratio = np.exp(geo)
                share = float(geo.mean() / gap.mean())
                reps_s, reps_m = [], []
                for w in W[:2000]:
                    s = w.sum()
                    if s <= 0:
                        continue
                    reps_s.append(float((w * geo).sum() / (w * gap).sum()))
                    reps_m.append(A.wmedian(ratio, w))
                res[f"{sub}|drop{int(drop)}|{b}"] = dict(
                    n=len(hosts), median_ratio_R2w4_over_R2w=round(float(np.median(ratio)), 4),
                    ci_median_ratio=[round(float(x), 4) for x in np.percentile(reps_m, [2.5, 97.5])],
                    geometry_share=round(share, 4), ci_geometry_share=[round(float(x), 4) for x in np.percentile(reps_s, [2.5, 97.5])],
                    mean_geo=round(float(geo.mean()), 4), mean_gap_R4_minus_R3=round(float(gap.mean()), 4),
                    mean_DiD=round(float(Dd.mean()), 4), share_DiD_negative=round(float((Dd < 0).mean()), 4))
    K.write_csv(K.RES / "a14.csv", rows)
    cell = {(r["contrast"], r["engine"], r["is_val_dropped"], r["band"]): r for r in rows}
    # registered readings (B3, pooled, all persons; with the reserved persons dropped beside)
    rd = {}
    for drop in (0, 1):
        p = res[f"pooled|drop{drop}|B3"]
        a_r4 = cell[("R4 vs R2w4", "pooled", drop, "B3")]["auc"]
        a_r3 = cell[("R3 vs R2w", "pooled", drop, "B3")]["auc"]
        fals = p["median_ratio_R2w4_over_R2w"] >= 0.95 or a_r4 >= 0.65
        rd[f"drop{drop}"] = dict(
            AUC_R2w4_vs_R2w=cell[("R2w4 vs R2w", "pooled", drop, "B3")]["auc"],
            median_ratio=p["median_ratio_R2w4_over_R2w"], AUC_R4_vs_R2w4=a_r4, AUC_R3_vs_R2w=a_r3,
            texture_excess=round(a_r4 - a_r3, 4), geometry_share=p["geometry_share"], ci_geometry_share=p["ci_geometry_share"],
            H_new_1="falsified" if fals else "not falsified",
            in_predicted_ranges=dict(AUC_R2w4_vs_R2w=0.55 <= cell[("R2w4 vs R2w", "pooled", drop, "B3")]["auc"] <= 0.60,
                                     median_ratio=0.82 <= p["median_ratio_R2w4_over_R2w"] <= 0.90,
                                     AUC_R4_vs_R2w4=0.58 <= a_r4 <= 0.64, geometry_share=0.40 <= p["geometry_share"] <= 0.70),
            revisit_learned_version_rule=bool(a_r4 - a_r3 >= 0.03))
    res["H_new_1_reading_B3"] = rd

    # H-new-2: detected typicality
    sys.path.insert(0, str(K.REPO / "src/ID0"))
    import analyse as IA  # noqa: E402
    import id0_common as IC  # noqa: E402
    from iss import ISS  # noqa: E402
    fit = IA.fit_rows()
    T = [IC.read_tem(r["tem"]) for r in fit]
    ref = IA.gpa(T)
    model = ISS(np.array([IA.procrustes_to(t, ref).ravel() for t in T]), [r["pid"] for r in fit], kmax=64)
    items = D.items
    L = M.LM(items)
    sc = {}
    for i, it in items.items():
        if it["set"] in ("LD1", "LD4") and it["role"] in ("R3", "R4", "R2w4"):
            lm = L.of(it)
            if lm is None:
                continue
            s = model.scores(IA.procrustes_to(lm, ref).ravel()[None])
            sc[i] = (it["role"], it["tool"], tuple(it["persons"].split("|")), s["iss"][0], s["typ"][0], -M.shape_asym(lm, 512))
    typ = {}
    for drop in (0, 1):
        for stat, j in (("iss", 3), ("typ", 4), ("shape_L", 5)):
            for name, xr, yr in (("R4 vs R2w4", "R4", "R2w4"), ("R2w4 vs R3", "R2w4", "R3"), ("R4 vs R3", "R4", "R3")):
                X = [v for v in sc.values() if v[0] == xr and not (drop and any(A.is_val_person(p) for p in v[2]))]
                Y = [v for v in sc.values() if v[0] == yr and not (drop and any(A.is_val_person(p) for p in v[2]))]
                ps = sorted({p for v in X + Y for p in v[2]})
                Dr = A.ST.Draw(ps, 2000, A.SEED)
                a, (lo, hi) = A.ST.wauc_ci(Dr, np.array([v[j] for v in X]), [v[2] for v in X],
                                           np.array([v[j] for v in Y]), [v[2] for v in Y])
                typ[f"{stat}|{name}|drop{drop}"] = dict(auc=round(a, 4), lo=round(float(lo), 4), hi=round(float(hi), 4),
                                                       nX=len(X), nY=len(Y))
    res["detected_shape_stats"] = typ
    a = typ["iss|R4 vs R2w4|drop1"]["auc"]
    b = typ["iss|R2w4 vs R3|drop1"]["auc"]
    res["H_new_2_reading"] = dict(AUC_R4_vs_R2w4=a, AUC_R2w4_vs_R3=b,
                                  prediction_met=bool(0.44 <= a <= 0.56 and b >= 0.62),
                                  reading="falsified: conclusion about detected typicality withdrawn" if a >= 0.60
                                  else "not falsified")
    json.dump(res, open(K.RES / "a14.json", "w"), indent=1)
    print(json.dumps(dict(H_new_1=rd, H_new_2=res["H_new_2_reading"]), indent=1))


if __name__ == "__main__":
    main()

"""ID0: apply the pre-registered falsifiers to the arm JSON files; print the summary table and write verdicts.json.
  python3 -I verdicts.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402

ARMS = ("landmark", "glint", "clip", "dino", "diffae")


def get(res, label, score="iss"):
    for r in res["contrasts"]:
        if r["label"] == label and r["score"] == score:
            return r
    return None


def main():
    A = {a: json.load(open(C.RES / f"arm_{a}.json")) for a in ARMS if (C.RES / f"arm_{a}.json").exists()}
    out = {"arms": {}}
    for a, r in A.items():
        if a == "landmark":
            main_lm = get(r, "frgcferet exact R3 vs R4 (R2w vs R4 shape)")
            d = dict(R0_vs_R4=get(r, "frgcferet exact R0 vs R4"), R2w_vs_R4_opencv=main_lm, D20_vs_B20=None,
                     control="not applicable (landmark files, not images)")
        else:
            d20 = get(r, "MorDIFF DiffAE-native D20 vs B20") if a == "diffae" else get(r, "MorDIFF stored D20 vs B20")
            d = dict(R0_vs_R4=get(r, "frgcferet opencv R0 vs R4"), R2w_vs_R4_opencv=get(r, "frgcferet opencv R2w vs R4"),
                     D20_vs_B20=d20, D20_vs_B20_stored=get(r, "MorDIFF stored D20 vs B20"),
                     SG3_bona_vs_morph=get(r, "StyleGAN3 h3_bona vs h3_sg3"),
                     SG3_spread_vs_morph=get(r, "StyleGAN3 a37spread vs h3_sg3"),
                     R3_vs_R4_opencv=get(r, "frgcferet opencv R3 vs R4"),
                     C20_vs_B20=get(r, "MorDIFF stored C20 vs B20"),
                     control=r.get("control_primary_iss"), control_clean=r.get("control_clean_045_055"))
        dose = list(r.get("dose", {}).values())
        d["dose_page_p"] = dose[0]["p"] if dose else None
        d["dose_monotone_means"] = dose[0]["monotone_means"] if dose else None
        out["arms"][a] = d
    # physics falsifier: best arm R2-vs-R4 below 0.65 on both a43 (D20 vs B20) and AR1 (R2w vs R4, OpenCV)
    def best(key):
        v = [(d[key]["auc"], a) for a, d in out["arms"].items() if d.get(key)]
        return max(v) if v else None
    b1, b2 = best("D20_vs_B20"), best("R2w_vs_R4_opencv")
    one_arm_both = [a for a, d in out["arms"].items() if d.get("D20_vs_B20") and d.get("R2w_vs_R4_opencv")
                    and d["D20_vs_B20"]["auc"] >= 0.65 and d["R2w_vs_R4_opencv"]["auc"] >= 0.65]
    out["physics_falsifier"] = dict(
        best_D20_vs_B20=b1, best_R2w_vs_R4_opencv=b2,
        part1_fires=bool(b1 and b2 and b1[0] < 0.65 and b2[0] < 0.65),
        arms_at_or_above_065_on_both=one_arm_both,
        part2_controls={a: d.get("control_clean") for a, d in out["arms"].items() if a != "landmark"},
        part3_dose_page_p={a: d.get("dose_page_p") for a, d in out["arms"].items()},
        landmark_R0_vs_R4=out["arms"].get("landmark", {}).get("R0_vs_R4"))
    # decision of the tonight text: any arm >= 0.75 on R2 vs R4 with a clean control; all arms < 0.65
    r2r4 = {}
    for a, d in out["arms"].items():
        vals = [d[k]["auc"] for k in ("R2w_vs_R4_opencv", "D20_vs_B20", "SG3_bona_vs_morph") if d.get(k)]
        r2r4[a] = vals
    out["decision"] = dict(
        arms_ge_075_with_clean_control=[a for a, v in r2r4.items() if any(x >= 0.75 for x in v)
                                        and out["arms"][a].get("control_clean") is True],
        all_arms_all_R2vsR4_below_065=all(all(x < 0.65 for x in v) for v in r2r4.values()),
        r2_vs_r4_values=r2r4)
    if "glint" in A:
        g = A["glint"]["geo0"]
        h = {x["label"]: x for x in g["virtual_head_applied"]}
        lm, dae = h.get("AR1 frgcferet opencv R3 vs R4"), h.get("a43_B vs a43_D (a46, 100 steps): D neg")
        ctl = [x for k, x in h.items() if k.startswith("control")]
        out["geo0"] = dict(
            head_landmark=lm, head_diffae=dae,
            go=bool(lm and dae and lm["auc"] >= 0.65 and lm["ci95"][0] > 0.60 and dae["auc"] >= 0.65 and dae["ci95"][0] > 0.60
                    and all(0.45 <= x["auc"] <= 0.55 for x in ctl)),
            kill=bool(lm and dae and lm["auc"] <= 0.55 and dae["auc"] <= 0.55),
            controls={k: x["auc"] for k, x in h.items() if k.startswith("control")},
            in_domain=g["virtual_head_in_domain"]["auc_morph_vs_single_and_twin"],
            idea0_falsifier_fires=bool(lm and dae and lm["auc"] <= 0.55 and lm["ci95"][1] < 0.60 and dae["auc"] <= 0.55
                                       and dae["ci95"][1] < 0.60 and g["virtual_head_in_domain"]["auc_morph_vs_single_and_twin"] >= 0.70),
            idea0_control_outside=[k for k, x in h.items() if k.startswith("control") and not 0.45 <= x["auc"] <= 0.55])
    # idea 1 shrink law
    sl = {}
    for a, r in A.items():
        for k, v in r.get("shrink_law", {}).items():
            sl[f"{a} | {k}"] = v
        for k, v in r.get("shrink_law_power", {}).items():
            sl[f"{a} | {k} [oracle power check]"] = v
    out["shrink_law"] = sl
    json.dump(out, open(C.RES / "verdicts.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:12000])


if __name__ == "__main__":
    main()

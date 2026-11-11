"""PD1 DiffAE family: tables (markdown to stdout, CSV files) from results_<feat>.json; applies the fixed readings.

Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_report.py > /tmp/report.md
Writes experiments/PD1_signal-isolation-paired-differences/diffae/{q1,q2_cos,q3q4,flags,external,bench,q5,readings}.csv
"""
import csv, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K

FEATS = ("clip_pool", "clip_patch", "dino_pool", "dino_patch")
FN = {"clip_pool": "CLIP pooled", "clip_patch": "CLIP mean patch", "dino_pool": "DINOv3 pooled", "dino_patch": "DINOv3 mean patch"}
VN = {"none": "no projection", "soft1": "softening removed (k=1)", "soft5": "softening removed (k=5)", "pipe": "pipeline removed",
      "soft1+pipe": "softening and pipeline removed"}
PRIMARY_FLAG = "FRLL_E7_vs_native (primary)"


def f3(x):
    return "n/a" if x is None else f"{x:.3f}"


def ci(c):
    return f"[{c[0]:.3f}, {c[1]:.3f}]"


def wcsv(name, rows):
    if not rows:
        return
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(K.OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, keys, restval="")
        w.writeheader()
        w.writerows(rows)


def reading(auc, excess, flag):
    if auc < 0.60 or excess <= 0:
        return "fails"
    if auc >= 0.75 and excess >= 0.05 and flag is not None and flag <= 0.15:
        return "works"
    return "mixed"


def main():
    R = {f: json.load(open(K.OUT / f"results_{f}.json")) for f in FEATS if (K.OUT / f"results_{f}.json").exists()}
    q1r, q2r, q34r, flr, exr, bnr, q5r, rdr = [], [], [], [], [], [], [], []
    for f, d in R.items():
        for s, v in d["Q1"].items():
            q1r.append(dict(feature=f, step=v["step"], hosts=v["hosts"], share=v["share"], share_lo=v["share_ci"][0], share_hi=v["share_ci"][1],
                            proj_auc=v["proj_auc"], proj_lo=v["proj_auc_ci"][0], proj_hi=v["proj_auc_ci"][1], reading=v["reading"]))
        for k, v in d.get("Q1_frll", {}).items():
            q1r.append(dict(feature=f, step=k + f" (training step {v['training_step']}; {v['note']})", hosts=v["n"], share=v["share"], share_lo="", share_hi="",
                            proj_auc="", proj_lo="", proj_hi="", reading="diagnostic (FRLL), no reading"))
        q2 = d["Q2"]
        for i, a in enumerate(q2["names"]):
            for j, b in enumerate(q2["names"]):
                if j >= i:
                    q2r.append(dict(feature=f, a=q2["labels"][i], b=q2["labels"][j], cos=q2["cos"][i][j], lo=q2["lo"][i][j], hi=q2["hi"][i][j],
                                    disattenuated=q2["disattenuated"][i][j]))
        for k, v in q2["frll_diagnostic"].items():
            for b, c in v["cos_with"].items():
                q2r.append(dict(feature=f, a=k + f" ({v['note']}; split-half reliability {v['split_half_reliability']:.3f}; n={v['n']})",
                                b=K.STEP_NAMES[b], cos=c, lo="", hi="", disattenuated=""))
        base = d["Q3Q4"].get("none")
        for var, vv in d["Q3Q4"].items():
            for h in ("H1", "H2"):
                r = vv[h]
                for c, x in r["contrasts"].items():
                    q34r.append(dict(feature=f, variant=var, head=h, contrast=c, auc=x["auc"], lo=x["ci"][0], hi=x["ci"][1],
                                     floor_stat=x.get("floor_stat", ""), floor_auc=x.get("floor_auc", ""), excess=x.get("excess", ""),
                                     excess_lo=x.get("excess_ci", ["", ""])[0], excess_hi=x.get("excess_ci", ["", ""])[1],
                                     final_C=r.get("final_C", "")))
                ext = vv.get("external", {}).get(h, {})
                for k, x in ext.get("flag", {}).items():
                    flr.append(dict(feature=f, variant=var, head=h, pool=k, threshold=x["threshold"], flag_native=x["flag_native"], flag_soft=x["flag_soft"],
                                    lo=x["flag_soft_ci"][0], hi=x["flag_soft_ci"][1], shift_sd=x["shift_sd"], n_soft=x["n_soft"]))
                for grp in ("frll256", "frll_stored", "mirror"):
                    for k, x in ext.get(grp, {}).items():
                        exr.append(dict(feature=f, variant=var, head=h, group=grp, contrast=k, auc=x.get("auc", x.get("share", "")),
                                        lo=x.get("ci", ["", ""])[0], hi=x.get("ci", ["", ""])[1], n=x.get("n", ""), note=x.get("note", x.get("source", ""))))
                for fam, x in ext.get("bench", {}).items():
                    bnr.append(dict(feature=f, variant=var, head=h, cell=fam, n_morphs=x["n_morphs"],
                                    auc_native=x["native"]["auc"], auc_native_lo=x["native"]["auc_ci"][0], auc_native_hi=x["native"]["auc_ci"][1],
                                    eer_native=x["native"]["eer"], auc_E7=x["E7"]["auc"], auc_E7_lo=x["E7"]["auc_ci"][0], auc_E7_hi=x["E7"]["auc_ci"][1],
                                    eer_E7=x["E7"]["eer"], auc_neutral_only=x["native_neutral_only"]["auc"], eer_neutral_only=x["native_neutral_only"]["eer"],
                                    E7_flag_at_native5=x["E7_flag_at_native5pct"]["rate"], morphs_flag_at_native5=x["E7_flag_at_native5pct"]["morphs_flagged"]))
            r1 = vv["H1"]["contrasts"]["x3_vs_x1"]
            fl = vv.get("external", {}).get("H1", {}).get("flag", {}).get(PRIMARY_FLAG, {}).get("flag_soft")
            row = dict(feature=f, variant=var, H1_x3_vs_x1=r1["auc"], lo=r1["ci"][0], hi=r1["ci"][1], floor=r1["floor_auc"], floor_stat=r1["floor_stat"],
                       excess=r1["excess"], excess_lo=r1["excess_ci"][0], flag_E7=fl, reading=reading(r1["auc"], r1["excess"], fl))
            if var != "none" and base is not None:
                b1 = base["H1"]["contrasts"]["x3_vs_x1"]["auc"]
                bfl = base.get("external", {}).get("H1", {}).get("flag", {}).get(PRIMARY_FLAG, {}).get("flag_soft")
                row["Q4_keeps_separation"] = "keeps its separation" if (b1 - r1["auc"]) < 0.05 else "loses separation"
                row["Q4_loses_soft_reaction"] = ("loses its reaction to softened genuine photos" if (fl is not None and bfl is not None and fl <= 0.15 and fl < bfl)
                                                 else "does not lose it")
            rdr.append(row)
        for key, v in d.get("Q5", {}).items():
            for nm in ("score", "paired_step"):
                q5r.append(dict(feature=f, measure=key, target=nm, n=v["n"], rho=v[nm]["rho"], lo=v[nm]["ci"][0], hi=v[nm]["ci"][1], reading=v[nm]["reading"]))
    for name, rows in (("q1.csv", q1r), ("q2_cos.csv", q2r), ("q3q4.csv", q34r), ("flags.csv", flr), ("external.csv", exr), ("bench.csv", bnr),
                       ("q5.csv", q5r), ("readings.csv", rdr)):
        wcsv(name, rows)
    # markdown digest
    print("## Readings\n")
    print("| Feature set | Variant | H1 x3 vs x1 [95%] | Floor (statistic) | Excess [lower] | FRLL E7 flag | Reading | Q4 separation | Q4 softening |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rdr:
        print(f"| {FN[r['feature']]} | {VN[r['variant']]} | {f3(r['H1_x3_vs_x1'])} [{f3(r['lo'])}, {f3(r['hi'])}] | {f3(r['floor'])} ({r['floor_stat']}) | "
              f"{r['excess']:+.3f} [{r['excess_lo']:+.3f}] | {f3(r['flag_E7'])} | {r['reading']} | {r.get('Q4_keeps_separation', '')} | {r.get('Q4_loses_soft_reaction', '')} |")
    print()
    for f, d in R.items():
        print(f"### {FN[f]}: Q1\n")
        for s, v in d["Q1"].items():
            print(f"- {v['step']}: share {f3(v['share'])} {ci(v['share_ci'])}, projection AUC {f3(v['proj_auc'])} {ci(v['proj_auc_ci'])}: {v['reading']}")
        for k, v in d.get("Q1_frll", {}).items():
            print(f"- {k}: share {f3(v['share'])} (n={v['n']}, {v['note']})")
        q2 = d["Q2"]
        print(f"\n### {FN[f]}: Q2 cross-validated cosines (diagonal = split-half reliability)\n")
        print("| | " + " | ".join(q2["names"]) + " |")
        print("|---" * (len(q2["names"]) + 1) + "|")
        for i, a in enumerate(q2["names"]):
            print(f"| {a} | " + " | ".join(f"{q2['cos'][i][j]:.2f} [{q2['lo'][i][j]:.2f}, {q2['hi'][i][j]:.2f}]" for j in range(len(q2["names"]))) + " |")
        for k, v in q2["readings"].items():
            print(f"- {k}: cos {v['cos']:.3f}: {v['reading']}")
        for k, v in q2["frll_diagnostic"].items():
            print(f"- {k} (rel {v['split_half_reliability']:.2f}, n {v['n']}, {v['note']}): " + ", ".join(f"{b} {c:+.2f}" for b, c in v["cos_with"].items()))
        print()
        for var, vv in d["Q3Q4"].items():
            print(f"### {FN[f]}, {VN[var]}: Q3\n")
            for h in ("H1", "H2"):
                r = vv[h]
                print(f"- {h} (final C {r.get('final_C')}): " + "; ".join(
                    f"{c} {f3(x['auc'])} {ci(x['ci'])} (floor {x.get('floor_stat')} {f3(x.get('floor_auc'))}, excess {x.get('excess', 0):+.3f} {ci(x.get('excess_ci', [0, 0]))})"
                    for c, x in r["contrasts"].items()))
                print(f"  paired: " + "; ".join(f"{k} {f3(x['share'])} {ci(x['ci'])}" for k, x in r["paired"].items()))
                ext = vv.get("external", {}).get(h, {})
                print("  flags: " + "; ".join(f"{k}: {f3(x['flag_soft'])} {ci(x['flag_soft_ci'])} (shift {x['shift_sd']:+.2f} sd)" for k, x in ext.get("flag", {}).items()))
            if "stat_head_H1recipe" in vv:
                print("- statistics head (H1 recipe): " + "; ".join(f"{c} {f3(x['auc'])}" for c, x in vv["stat_head_H1recipe"].items()))
            print()
        if "Q5" in d:
            print(f"### {FN[f]}: Q5\n")
            for key, v in d["Q5"].items():
                for nm in ("score", "paired_step"):
                    print(f"- {key} vs {nm}: rho {v[nm]['rho']:+.3f} {ci(v[nm]['ci'])} (n {v['n']}): {v[nm]['reading']}")
        if d.get("cohort_transfer"):
            print(f"\n### {FN[f]}: cohort transfer (expanded123 -> confirmation blocks)\n")
            for h, v in d["cohort_transfer"].items():
                print(f"- {h}: " + "; ".join(f"{c} {f3(x['auc'])} {ci(x['ci'])} (n {x['na']}/{x['nb']})" for c, x in v.items()))
        print()


if __name__ == "__main__":
    main()

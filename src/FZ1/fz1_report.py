"""FZ1: markdown tables for result.md from the P1-P4 json files (prints to stdout)."""
import json, pathlib, sys
O = pathlib.Path("/home/narolski/smad-next/experiments/FZ1")


def f(x):
    return f"{x['auc']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}]"


def ladder_table(res, labels, keys_a43, keys_sg3):
    print("| Contrast | " + " | ".join(labels) + " |")
    print("|---|" + "---|" * len(labels))
    for k in keys_a43:
        print(f"| {k} | " + " | ".join(f(res[l]["a43"][k]) for l in labels) + " |")
    for k in keys_sg3:
        print(f"| SG3 {k} | " + " | ".join(f(res[l]["sg3"][k]) for l in labels) + " |")
    print("| flag rate R0 → R1 at own MorDIFF EER thr (pts) | " + " | ".join(
        "{:.1f}% → {:.1f}% ({:+.1f} [{:+.1f}, {:+.1f}])".format(100 * r["flag_R0"], 100 * r["flag_R1"], r["change_pts"], *r["change_ci_pts"])
        for r in (res[l]["flag_R0_R1"]["thr_full_mordiff"] for l in labels)) + " |")
    print("| same, threshold from the 200 sampled morphs | " + " | ".join(
        "{:.1f}% → {:.1f}% ({:+.1f} [{:+.1f}, {:+.1f}])".format(100 * r["flag_R0"], 100 * r["flag_R1"], r["change_pts"], *r["change_ci_pts"])
        for r in (res[l]["flag_R0_R1"]["thr_200_sampled"] for l in labels)) + " |")
    for k in ("frll_bona", "mordiff_bona_R0"):
        print(f"| neutral above smiling, {k} | " + " | ".join(
            "{:.3f} [{:.3f}, {:.3f}]".format(r["value"], *r["ci"]) for r in (res[l]["neutral_above_smiling"][k] for l in labels)) + " |")
    print()
    print("| Benchmark EER % (native / E7) | " + " | ".join(labels) + " |")
    print("|---|" + "---|" * len(labels))
    for c in res[labels[0]]["bench"]:
        print(f"| {c} | " + " | ".join("{:.1f} [{:.1f}, {:.1f}] / {:.1f} [{:.1f}, {:.1f}]".format(
            b["native"]["eer"], *b["native"]["ci"], b["E7"]["eer"], *b["E7"]["ci"]) for b in (res[l]["bench"][c] for l in labels)) + " |")
    print()


KA = ["B20 vs D20", "B vs D", "C20 vs D20", "C vs D", "B20 vs C20", "B vs C", "D vs R0", "D20 vs R0", "E vs R0", "R1 vs R0", "A vs R0", "B20 vs R0", "B vs R0"]
KS = ["morph vs render", "morph vs spread"]
part = sys.argv[1] if len(sys.argv) > 1 else "all"
if part in ("p1", "all"):
    p1 = json.load(open(O / "p1_release_reread.json"))
    labs = [k for k in p1 if not k.startswith("_")]
    ladder_table(p1, labs, KA, KS)
if part in ("p2", "all") and (O / "p2_probe.json").exists():
    p2 = json.load(open(O / "p2_probe.json"))
    bbs = sorted({d["backbone"] for d in p2.values()}, key=["clip_mad", "clip_native", "dinov3", "dinov2"].index)
    cons = list(dict.fromkeys(d["contrast"] for d in p2.values()))
    print("| Contrast | " + " | ".join(bbs) + " |")
    print("|---|" + "---|" * len(bbs))
    for c in cons:
        cells = []
        for b in bbs:
            d = p2[f"{b}|{c}"]
            cells.append(f"{d['auc']:.3f} [{d['ci'][0]:.3f}, {d['ci'][1]:.3f}] (seeds {d['fold_seed_range'][0]:.2f}–{d['fold_seed_range'][1]:.2f}); {d['reading']}")
        print(f"| {c} | " + " | ".join(cells) + " |")
    print()
if part in ("p3", "all") and (O / "p3_heads.json").exists():
    p3 = json.load(open(O / "p3_heads.json"))
    seeds = [k for k in p3 if not k.startswith("_")]
    ladder_table(p3, seeds, KA, KS)
    print("| | " + " | ".join(seeds) + " |")
    print("|---|" + "---|" * len(seeds))
    print("| train AUC (SMDD) | " + " | ".join(f"{p3[s]['train']['train_auc_morph_vs_bona']:.3f}" for s in seeds) + " |")
    print("| Spearman vs released FE ViT-L/14 (A43 rows) | " + " | ".join(f"{p3[s]['spearman_vs_release_FE_L14_a43']:.3f}" for s in seeds) + " |")
    print()
    print(p3["_prediction"])
if part in ("p4", "all") and (O / "p4_stats.json").exists():
    p4 = json.load(open(O / "p4_stats.json"))
    for key, res in p4.items():
        print(f"**{key}**")
        print()
        print("| Statistic | folded AUC [95%] | direction | probe − stat [95%] | matches probe |")
        print("|---|---|---|---|---|")
        for nm, d in res.items():
            if nm == "logistic_all7":
                pm = d.get("probe_minus_logistic")
                print(f"| logistic on all 7 (5-fold by person) | {d['auc']:.3f} [{d['ci'][0]:.3f}, {d['ci'][1]:.3f}] | — | "
                      + (f"{pm['point']:+.3f} [{pm['ci'][0]:+.3f}, {pm['ci'][1]:+.3f}] | {d['matches_probe']} |" if pm else "| |"))
            else:
                pm = d.get("probe_minus_stat")
                print(f"| {nm} | {d['auc_folded']:.3f} [{d['ci_folded'][0]:.3f}, {d['ci_folded'][1]:.3f}] | {d['direction']} | "
                      + (f"{pm['point']:+.3f} [{pm['ci'][0]:+.3f}, {pm['ci'][1]:+.3f}] | {d['matches_probe']} |" if pm else "| |"))
        print()

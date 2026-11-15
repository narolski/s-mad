"""AB1: print the result tables from ab1_read.json (no new statistic; formatting only).
  python3 ab1_tables.py ab1_read.json > tables.md"""
import json
import sys

R = json.load(open(sys.argv[1]))
N, V = R["networks"], R["verdicts"]
S = (408, 409, 410, 411, 412)
ARMS = ("A", "B", "Sb", "Sp", "SbZ", "SbH", "SbS", "AS")


def g(arm, s, f):
    n = N.get(f"{arm}_s{s}")
    return None if n is None else f(n)


def row(label, f, fmt="{:.3f}"):
    out = [label]
    for a in ARMS:
        v = [g(a, s, f) for s in S]
        out.append(" / ".join("–" if x is None else fmt.format(x) for x in v))
    return "| " + " | ".join(out) + " |"


print("Per network, seeds 408 / 409 / 410 / 411 / 412 (WCSS H100; own rule logit > 0; development data only)\n")
print("| Read | " + " | ".join(ARMS) + " |")
print("|---" * (len(ARMS) + 1) + "|")
print(row("landmark_combined AUC", lambda n: n["lcomb_auc"]))
for z in ("fm61", "amsl112"):
    print(row(f"C2P Δf {z}", lambda n, z=z: n["c2p"][z]["d_flag"], "{:+.3f}"))
    print(row(f"C2P Δf {z} upper 95%", lambda n, z=z: n["c2p"][z]["d_flag_upper95"], "{:+.3f}"))
    print(row(f"C2P Δm {z} (genuine SD)", lambda n, z=z: n["c2p"][z]["d_mean_sd"], "{:+.2f}"))
    print(row(f"C2P Δm_att {z}", lambda n, z=z: n["c2p"][z]["d_mean_att_sd"], "{:+.2f}"))
print(row("FFHQ hold-out native photos flagged", lambda n: n["ffhq_native_photo_flag"]))
print(row("dev camera photos flagged (226)", lambda n: n["camera"]))
print(row("dev storage rise Δsoft (452 vs 226)", lambda n: n["dsoft"], "{:+.3f}"))
print(row("dev warp-only placed (371)", lambda n: n["warp"]))
print(row("dev halves placed (610)", lambda n: n["halves"]))
print(row("dev S3 placed (100)", lambda n: n["S3"], "{:.2f}"))
print(row("dev S0 placed (100)", lambda n: n["S0"], "{:.2f}"))
print(row("dev S0-vs-S4 AUC", lambda n: n["S0_vs_S4_auc"]))
print(row("dev S3-vs-S4 AUC", lambda n: n["S3_vs_S4_auc"]))
print(f"\nFloor (best single statistic, landmark_combined): {R['floor_best_auc']:.3f}; 27-statistic baseline 0.814.\n")
print("Verdicts:\n")
for k, v in V.items():
    if isinstance(v, dict) and "verdict" in v:
        extra = ""
        if "mean" in v:
            extra = f" (seed mean {v['mean']:+.3f}, 95% t-interval [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]; per-seed rule: {v['per_seed_verdict']})"
        if "k" in v and "n" in v:
            extra += f" ({v['k']} of {v['n']} seeds)"
        print(f"- {k}: {v['verdict']}{extra}")
    elif isinstance(v, str):
        print(f"- {k}: {v}")
print("\nAttribution table (secondary; seed-mean rule):\n")
for k, v in V["attribution_table_secondary"].items():
    m = v.get("mean")
    print(f"- {k}: {v['label']}" + (f" (mean {m:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}])" if m is not None else ""))

"""C1c step 4: benchmark tables with neutral-only genuine photos as the headline, from the C1b outputs (no new scores).
Mean over the 11 scored imbalanced cells with an interval from the stored two-way person-bootstrap replicates.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1c/c1c_bench.py
"""
import json, pathlib
import numpy as np

C1B = pathlib.Path("/home/narolski/smad-next/experiments/C1b/c1b_read.json")
REPS = pathlib.Path("/mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1c_smiling-half-expression-or-detail")
R = json.load(open(C1B))
Z = np.load(REPS)
IMB = [c for c in R["cells"] if not c.startswith("mordiff")]
SHORT = {c: c.split("/")[1] for c in R["cells"]}
rel = [d for d in R["detectors"] if d["ckpt"] == "release"]
out = {"cells": IMB, "releases": {}, "recipes": {}}
lines = []
p = lines.append
p("## EER (%) per cell: neutral-only genuine (headline) | all genuine | smiling-only; releases\n")
p("| Release | " + " | ".join(SHORT[c] for c in IMB) + " | mean neutral-only [95%] | mean all [95%] | mean change [95%] |")
p("|---|" + "---|" * (len(IMB) + 3))
means = {}
for d in rel:
    lab = d["label"]
    rn = np.mean([Z[f"{lab}||{c}|neu"] for c in IMB], 0); ra = np.mean([Z[f"{lab}||{c}|all"] for c in IMB], 0)
    mn = np.mean([d["b"][c]["neu"]["eer"] for c in IMB]); ma = np.mean([d["b"][c]["all"]["eer"] for c in IMB]); ms = np.mean([d["b"][c]["smi"]["eer"] for c in IMB])
    q = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]  # noqa: E731
    means[lab] = {"neu": mn, "all": ma, "smi": ms, "ci_neu": q(rn), "ci_all": q(ra), "change": mn - ma, "ci_change": q(rn - ra)}
    p(f"| {lab} | " + " | ".join(f"**{d['b'][c]['neu']['eer']:.1f}** / {d['b'][c]['all']['eer']:.1f} / {d['b'][c]['smi']['eer']:.1f}" for c in IMB)
      + f" | **{mn:.1f}** [{means[lab]['ci_neu'][0]:.1f}, {means[lab]['ci_neu'][1]:.1f}] | {ma:.1f} [{means[lab]['ci_all'][0]:.1f}, {means[lab]['ci_all'][1]:.1f}]"
      + f" | {mn - ma:+.2f} [{means[lab]['ci_change'][0]:+.2f}, {means[lab]['ci_change'][1]:+.2f}] |")
rk_n = {l: i + 1 for i, l in enumerate(sorted(means, key=lambda l: means[l]["neu"]))}
rk_a = {l: i + 1 for i, l in enumerate(sorted(means, key=lambda l: means[l]["all"]))}
p("\n## Mean EER over the 11 cells and rank among the 9 release score sets\n")
p("| Release | mean EER neutral-only | rank | mean EER all | rank | mean EER smiling-only |")
p("|---|---|---|---|---|---|")
for l in sorted(means, key=lambda l: means[l]["neu"]):
    p(f"| {l} | {means[l]['neu']:.1f} | {rk_n[l]} | {means[l]['all']:.1f} | {rk_a[l]} | {means[l]['smi']:.1f} |")
p("\n## Per-cell rank among the 9 releases, neutral-only (all)\n")
p("| Release | " + " | ".join(SHORT[c] for c in IMB) + " |")
p("|---|" + "---|" * len(IMB))
for d in rel:
    cells = []
    for c in IMB:
        rn = 1 + sum(e["b"][c]["neu"]["eer"] < d["b"][c]["neu"]["eer"] for e in rel)
        ra = 1 + sum(e["b"][c]["all"]["eer"] < d["b"][c]["all"]["eer"] for e in rel)
        cells.append(f"{rn} ({ra})")
    p(f"| {d['label']} | " + " | ".join(cells) + " |")
p("\n## BPCER at APCER 5% (%): neutral-only (headline) | all | smiling-only; releases\n")
p("| Release | " + " | ".join(SHORT[c] for c in IMB) + " | mean neutral-only | mean all |")
p("|---|" + "---|" * (len(IMB) + 2))
for d in rel:
    p(f"| {d['label']} | " + " | ".join(f"**{d['b'][c]['neu']['bpcer5']:.0f}** / {d['b'][c]['all']['bpcer5']:.0f} / {d['b'][c]['smi']['bpcer5']:.0f}" for c in IMB)
      + f" | {np.mean([d['b'][c]['neu']['bpcer5'] for c in IMB]):.1f} | {np.mean([d['b'][c]['all']['bpcer5'] for c in IMB]):.1f} |")
p("\n## Recipes (seed means): mean EER over the 11 cells, neutral-only | all | smiling-only\n")
p("| Recipe, checkpoint | seeds | mean EER neutral-only | all | smiling-only | change (range over seeds) |")
p("|---|---|---|---|---|---|")
G = {}
for d in R["detectors"]:
    if d["ckpt"] != "release":
        G.setdefault(f"{d['label'].split()[0]} {d['ckpt']}", []).append(d)
for k, L in G.items():
    ch = [np.mean([d["b"][c]["neu"]["eer"] - d["b"][c]["all"]["eer"] for c in IMB]) for d in L]
    vals = [np.mean([np.mean([d["b"][c][g]["eer"] for c in IMB]) for d in L]) for g in ("neu", "all", "smi")]
    out["recipes"][k] = {"neu": vals[0], "all": vals[1], "smi": vals[2], "change_range": [min(ch), max(ch)]}
    p(f"| {k} | {len(L)} | {vals[0]:.1f} | {vals[1]:.1f} | {vals[2]:.1f} | {vals[0] - vals[1]:+.2f} ({min(ch):+.1f} to {max(ch):+.1f}) |")
out["releases"] = {l: {**means[l], "rank_neu": rk_n[l], "rank_all": rk_a[l]} for l in means}
json.dump(out, open(OUT / "c1c_bench.json", "w"), indent=1)
open(OUT / "c1c_bench.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

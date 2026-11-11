"""C1b: summary tables from c1b_read.json and c1b_probe.json (no new statistics; applies the fixed falsifiers).
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1b/c1b_summarize.py > experiments/C1b/c1b_summary.txt
"""
import json, pathlib, collections
import numpy as np

OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1b")
R = json.load(open(OUT / "c1b_read.json"))
D = R["detectors"]
IMB = [c for c in R["cells"] if not c.startswith("mordiff")]
f3 = lambda x: f"{x:.3f}"  # noqa: E731
f1 = lambda x: f"{x:.1f}"  # noqa: E731


def ci(v, f=f3):
    return f"{f(v[0])} [{f(v[1])}, {f(v[2])}]"


def wp(d, fr="frll_bona"):
    return d["a"][fr]


def recipe(d):
    return d["label"].split()[0]


print("## (a) within-person neutral-above-smiling AUC (frll_bona = dim_bona frames; mordiff_bona secondary)\n")
print("| Detector | AUC_wp [95%] | persons neutral > smiling | pooled AUC [95%] | MorDIFF frames AUC_wp [95%] |")
print("|---|---|---|---|---|")
for d in D:
    if d["ckpt"] == "release":
        a, m = wp(d), wp(d, "mordiff_bona")
        print(f"| {d['label']} | {ci([a['auc_wp']] + a['ci'])} | {a['n_neutral_above']}/102 (ties {a['n_ties']}) | {ci([a['auc_pooled']] + a['ci_pooled'])} | {ci([m['auc_wp']] + m['ci'])} |")
print()
print("| Recipe, checkpoint | n | AUC_wp per seed | mean | n ≥ 0.65 | n with LB > 0.5 | MorDIFF frames per seed |")
print("|---|---|---|---|---|---|---|")
G = collections.OrderedDict()
for d in D:
    if d["ckpt"] != "release":
        G.setdefault((recipe(d), d["ckpt"]), []).append(d)
for (rc, ck), L in G.items():
    v = [wp(d)["auc_wp"] for d in L]
    lb = [wp(d)["ci"][0] for d in L]
    vm = [wp(d, "mordiff_bona")["auc_wp"] for d in L]
    print(f"| {rc} {ck} | {len(L)} | {' '.join(f'{x:.2f}' for x in v)} | {np.mean(v):.3f} | {sum(x >= 0.65 for x in v)} | {sum(x > 0.5 for x in lb)} | {' '.join(f'{x:.2f}' for x in vm)} |")

print("\n## Fixed falsifiers\n")
mad = [d for d in D if d["ckpt"] == "last" and recipe(d) in ("M3", "M3L")]
assert len(mad) == 13
n65 = sum(wp(d)["auc_wp"] >= 0.65 for d in mad)
print(f"H1: {n65} of 13 last-checkpoint MADation-recipe networks have AUC_wp >= 0.65 (falsified if < 10) -> {'FALSIFIED' if n65 < 10 else 'not falsified'}")
for d in mad:
    a = wp(d)
    print(f"   {d['label']}: {ci([a['auc_wp']] + a['ci'])}, {a['n_neutral_above']}/102")
m3 = [wp(d)["auc_wp"] for d in mad if recipe(d) == "M3"]
mm = float(np.mean(m3))
lab = "FALSIFIED" if mm >= 0.70 else "prediction met" if mm <= 0.60 else "not falsified, prediction not met"
print(f"H2: mean AUC_wp of the 8 last M3 = {mm:.3f} (min {min(m3):.3f}, max {max(m3):.3f}); {sum(x <= 0.60 for x in m3)} of 8 <= 0.60 -> {lab}")

print("\n## (b) EER change neutral-only minus all, imbalanced cells, releases (points; [95% two-way person bootstrap])\n")
print("| Detector | " + " | ".join(c.split('/')[1] for c in IMB) + " | mean | cells with LB > 0 |")
print("|---|" + "---|" * (len(IMB) + 2))
for d in D:
    if d["ckpt"] == "release":
        v = [d["b"][c]["neu-all_eer"] for c in IMB]
        print(f"| {d['label']} | " + " | ".join(f"{x[0]:+.1f} [{x[1]:+.1f}, {x[2]:+.1f}]" for x in v) + f" | {np.mean([x[0] for x in v]):+.2f} | {sum(x[1] > 0 for x in v)}/11 |")

print("\n## (b) EER all -> neutral-only, releases, every cell (EER all / neu / smi)\n")
print("| Detector | " + " | ".join(c.split('/')[1] for c in R["cells"]) + " |")
print("|---|" + "---|" * len(R["cells"]))
for d in D:
    if d["ckpt"] == "release":
        print(f"| {d['label']} | " + " | ".join(f"{d['b'][c]['all']['eer']:.1f} / {d['b'][c]['neu']['eer']:.1f} / {d['b'][c]['smi']['eer']:.1f}" for c in R["cells"]) + " |")

print("\n## (b) BPCER@APCER 5% and 10%, all -> neutral-only (releases, imbalanced cells; difference [95%])\n")
for key in ("bpcer5", "bpcer10"):
    print(f"\n{key}:\n")
    print("| Detector | " + " | ".join(c.split('/')[1] for c in IMB) + " |")
    print("|---|" + "---|" * len(IMB))
    for d in D:
        if d["ckpt"] == "release":
            print(f"| {d['label']} | " + " | ".join(f"{d['b'][c]['all'][key]:.0f}→{d['b'][c]['neu'][key]:.0f} ({d['b'][c]['neu-all_' + key][0]:+.0f} [{d['b'][c]['neu-all_' + key][1]:+.0f}, {d['b'][c]['neu-all_' + key][2]:+.0f}])" for c in IMB) + " |")

print("\n## (b) recipes: mean over seeds of the EER change neutral-only minus all (imbalanced cells)\n")
print("| Recipe, ckpt | " + " | ".join(c.split('/')[1] for c in IMB) + " | mean | networks×cells with LB > 0 | EER all, mean over cells |")
print("|---|" + "---|" * (len(IMB) + 3))
for (rc, ck), L in G.items():
    v = [np.mean([d["b"][c]["neu-all_eer"][0] for d in L]) for c in IMB]
    nlb = sum(d["b"][c]["neu-all_eer"][1] > 0 for d in L for c in IMB)
    ea = np.mean([d["b"][c]["all"]["eer"] for d in L for c in IMB])
    print(f"| {rc} {ck} | " + " | ".join(f"{x:+.1f}" for x in v) + f" | {np.mean(v):+.2f} | {nlb}/{len(L) * 11} | {ea:.1f} |")

print("\n## Family summary of the EER change (neutral-only minus all, mean over the 11 imbalanced cells)\n")
fam = collections.OrderedDict([
    ("MADation releases ViT-B/16, ViT-L/14", lambda d: d["ckpt"] == "release" and d["label"] in ("MADation ViT-B/16 release", "MADation ViT-L/14 release")),
    ("MADation FE/FS releases", lambda d: d["ckpt"] == "release" and (" FE " in d["label"] or " FS " in d["label"])),
    ("SelfMAD release (both pipelines)", lambda d: d["ckpt"] == "release" and "SelfMAD" in d["label"]),
    ("MixFaceNet-MAD release", lambda d: d["ckpt"] == "release" and "MixFaceNet" in d["label"]),
    ("M3 last", lambda d: d["ckpt"] == "last" and recipe(d) == "M3"), ("M3L last", lambda d: d["ckpt"] == "last" and recipe(d) == "M3L"),
    ("M3 es", lambda d: d["ckpt"] == "es" and recipe(d) == "M3"), ("M3L es", lambda d: d["ckpt"] == "es" and recipe(d) == "M3L"),
    ("CNN recipes last (M1 M2 M4 M5 M6 M8 M8O)", lambda d: d["ckpt"] == "last" and recipe(d) not in ("M3", "M3L")),
    ("CNN recipes es", lambda d: d["ckpt"] == "es" and recipe(d) not in ("M3", "M3L"))])
print("| Family | networks | mean EER change (range over networks) | mean BPCER@5 change | AUC_wp mean (range) |")
print("|---|---|---|---|---|")
for fn, fl in fam.items():
    L = [d for d in D if fl(d)]
    ch = [np.mean([d["b"][c]["neu-all_eer"][0] for c in IMB]) for d in L]
    b5 = [np.mean([d["b"][c]["neu-all_bpcer5"][0] for c in IMB]) for d in L]
    a = [wp(d)["auc_wp"] for d in L]
    print(f"| {fn} | {len(L)} | {np.mean(ch):+.2f} ({min(ch):+.1f} to {max(ch):+.1f}) | {np.mean(b5):+.1f} | {np.mean(a):.3f} ({min(a):.2f}–{max(a):.2f}) |")
# association between AUC_wp and EER change over all networks
a = np.array([wp(d)["auc_wp"] for d in D]); ch = np.array([np.mean([d["b"][c]["neu-all_eer"][0] for c in IMB]) for d in D])
from scipy.stats import spearmanr  # noqa: E402
print(f"\nSpearman(AUC_wp, mean EER change) over all {len(D)} score sets: {spearmanr(a, ch).statistic:.3f}")

print("\n## Cue-matrix reading rule per detector (pre-registered)\n")
rule = collections.OrderedDict()
for d in D:
    A = wp(d)
    n6 = sum(d["b"][c]["neu-all_eer"][1] > 0 for c in IMB)
    fold = 0.5 + abs(A["auc_wp"] - 0.5)
    lo, hi = A["ci"]
    fhi = 0.5 + max(abs(lo - 0.5), abs(hi - 0.5))
    if A["auc_wp"] >= 0.65 and lo > 0.5 and n6 >= 6:
        v = "USED"
    elif fold < 0.60 and fhi < 0.65:
        v = "NOT USED"
    else:
        v = "undetermined"
    rule[d["label"]] = (v, A["auc_wp"], n6, d)
print("| Detector / recipe | verdict |")
print("|---|---|")
for k, (v, a_, n6, d) in rule.items():
    if d["ckpt"] == "release":
        print(f"| {k} | {v} (AUC_wp {a_:.3f}, EER-change LB > 0 in {n6}/11 cells) |")
for (rc, ck), L in G.items():
    c = collections.Counter(rule[d["label"]][0] for d in L)
    print(f"| {rc} {ck} | " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + " |")

print("\n## MorDIFF (balanced cell): EER all / neu / smi and 2x2 AUC (morph expression x genuine expression), releases\n")
for d in D:
    if d["ckpt"] == "release":
        o = d["b"]["mordiff/mordiff"]
        print(f"- {d['label']}: EER {o['all']['eer']:.1f} / {o['neu']['eer']:.1f} / {o['smi']['eer']:.1f}; neu-all {ci(o['neu-all_eer'], f1)}; "
              + ", ".join(f"{k} {v:.3f}" for k, v in o["2x2_auc"].items()))

print("\n## (c) Rank changes, 27 rows (9 releases + 18 recipe-checkpoint seed means), imbalanced cells\n")
print("| Cell | Kendall τ | rows that move | pairs flipped | release pairs flipped beyond noise |")
print("|---|---|---|---|---|")
for c in IMB:
    rk = R["ranks"][c]
    bn = [f"{f['pair'][0]} vs {f['pair'][1]}" for f in rk["flips"] if f.get("beyond_noise")]
    print(f"| {c} | {rk['kendall_tau']:.3f} | {len(rk['moved'])} | {len(rk['flips'])} | {'; '.join(bn) if bn else 'none'} |")
print("\nRank of selected rows (all -> neutral-only):\n")
sel = ["MADation ViT-B/16 release", "MADation ViT-L/14 release", "SelfMAD release, own preprocessing", "MixFaceNet-MAD release, our frames (desc.)",
       "M3 last (seed mean)", "M3L last (seed mean)", "M4 last (seed mean)", "M8O last (seed mean)"]
print("| Row | " + " | ".join(c.split('/')[1] for c in IMB) + " |")
print("|---|" + "---|" * len(IMB))
for s in sel:
    print(f"| {s} | " + " | ".join(f"{R['ranks'][c]['table'][s]['rank_all']}→{R['ranks'][c]['table'][s]['rank_neu']}" for c in IMB) + " |")
print("\nRelease-pair flips (point estimates), per cell:\n")
for c in IMB:
    rel = [f for f in R["ranks"][c]["flips"] if "ci_gap_all" in f]
    if rel:
        print(f"- {c}: " + "; ".join(f"{f['pair'][0]} vs {f['pair'][1]} gap {f['gap_all']:+.1f} → {f['gap_neu']:+.1f} (change CI [{f['ci_change'][0]:+.1f}, {f['ci_change'][1]:+.1f}])" for f in rel))

pj = OUT / "c1b_probe.json"
if pj.exists():
    P = json.load(open(pj))
    print("\n## Probe validation on morphs with known expression\n")
    print("| Family | n (smiling) | accuracy [95%] | sensitivity [95%] | specificity [95%] | AUC [95%] |")
    print("|---|---|---|---|---|---|")
    for cn, o in P["validation"].items():
        s = f"{o['sensitivity']:.3f} [{o['sensitivity_ci'][0]:.3f}, {o['sensitivity_ci'][1]:.3f}]" if "sensitivity" in o else "–"
        sp = f"{o['specificity']:.3f} [{o['specificity_ci'][0]:.3f}, {o['specificity_ci'][1]:.3f}]" if "specificity" in o else "–"
        au = f"{o['auc']:.3f} [{o['auc_ci'][0]:.3f}, {o['auc_ci'][1]:.3f}]" if "auc" in o else "–"
        print(f"| {cn} | {o['n']} ({o['n_smiling_true']}) | {o['accuracy']:.3f} [{o['accuracy_ci'][0]:.3f}, {o['accuracy_ci'][1]:.3f}] | {s} | {sp} | {au} |")
    print("\nPooled references:", json.dumps(P["pooled_refs"]))
    print("\n| Target family | n | flagged smile-like [95%] | reference | corrected smiling share [95%] | neutral-only status |")
    print("|---|---|---|---|---|---|")
    for cn, o in P["targets"].items():
        print(f"| {cn} | {o['n']} | {o['flagged_share']:.3f} [{o['flagged_ci'][0]:.3f}, {o['flagged_ci'][1]:.3f}] | {o['ref']} | {o['corrected_smiling_share']:.3f} [{o['ci'][0]:.3f}, {o['ci'][1]:.3f}] | {o.get('neutral_only_status', '(DiM: README)')} |")

"""CB1: markdown tables from the per_arm.csv files (no computation beyond formatting).
  python3 -I compile_tables.py OUT.md DIR [DIR ...]"""
import csv
import sys

FAMS = {"mad22c": ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"],
        "frllm": ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]}
rows = []
for d in sys.argv[2:]:
    rows += list(csv.DictReader(open(f"{d}/per_arm.csv")))
L = []
f = lambda x: "" if x in ("", None) else f"{float(x):.2f}"
for bench, title in (("mad22c", "Corrected MAD22 (204 genuine + 4,483 morphs)"), ("frllm", "FRLL-Morphs")):
    L.append(f"\n### {title}: EER (%) per family, seed mean; MEAN5 with two-way person bootstrap 95% CI\n")
    L.append("| Arm | ckpt | genuine pool | n | " + " | ".join(FAMS[bench]) + " | MEAN5 [95% CI] | published mean | reading (90% seed t-interval of the difference vs M) |")
    L.append("|" + "---|" * (len(FAMS[bench]) + 7))
    keys = sorted({(r["arm"], r["ckpt"], r["pool"]) for r in rows if r.get("bench") == bench},
                  key=lambda k: (k[0], k[1] != "es" and k[1] != "model", k[1], k[2]))
    for arm, ck, pool in keys:
        sel = {r["family"]: r for r in rows if r.get("bench") == bench and r["arm"] == arm and r["ckpt"] == ck and r["pool"] == pool}
        m = sel.get("MEAN5")
        if not m:
            continue
        prim = " (primary)" if m["primary"] == "True" else ""
        rd = m.get("reading", "") or ""
        if rd:
            rd = f"{rd}; delta {float(m['delta']):+.2f} [{float(m['delta90_lo']):+.2f}, {float(m['delta90_hi']):+.2f}], M {float(m['margin']):.2f}"
        L.append(f"| {arm} | {ck}{prim} | {pool} | {m['n_seeds']} | " + " | ".join(f(sel[x]['eer_mean']) if x in sel else "" for x in FAMS[bench])
                 + f" | {f(m['eer_mean'])} [{f(m['eer_boot_lo'])}, {f(m['eer_boot_hi'])}] | {m.get('published', '')} | {rd} |")
    L.append(f"\n### {title}: BPCER (%) at APCER 1 / 5 / 10 / 20 %, native genuine pool, primary checkpoint, seed mean\n")
    L.append("| Arm | family | BPCER@1 | BPCER@5 | BPCER@10 | BPCER@20 |\n|---|---|---|---|---|---|")
    for r in rows:
        if r.get("bench") == bench and r["pool"] == "native" and r["primary"] == "True" and r["family"] in FAMS[bench]:
            L.append(f"| {r['arm']} | {r['family']} | {f(r['bpcer_at_apcer1'])} | {f(r['bpcer_at_apcer5'])} | {f(r['bpcer_at_apcer10'])} | {f(r['bpcer_at_apcer20'])} |")
ex = [r for r in rows if r["family"] in ("C1_EXCLUDED", "WITHHELD")]
if ex:
    L.append("\n### Networks excluded by the scorer gate C1\n")
    for r in ex:
        L.append(f"- {r['arm']} {r['ckpt']}: {r['family']}: {r['reading']}")
open(sys.argv[1], "w").write("\n".join(L) + "\n")
print("written", sys.argv[1], len(L), "lines")

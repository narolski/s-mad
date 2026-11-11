"""Fixed-threshold re-read (EV1): print the markdown tables of result.md from the CSV / JSON outputs (no computation
beyond selection and seed summaries). Run: python3 -I src/EV1/ev1_report.py > /mnt/t7/smad_next/EV1/report_tables.md
"""
import csv, json, sys, pathlib
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

O = K.OUT
rd = lambda fn: list(csv.DictReader(open(O / fn)))  # noqa: E731
MAIN = ["MADation ViT-L/14 release", "MADation ViT-B/16 release", "SelfMAD release, own preprocessing",
        "SelfMAD release, our pipeline", "MADation FE ViT-L/14 release", "MADation FE ViT-B/16 release",
        "MADation FS ViT-L/14 release", "MADation FS ViT-B/16 release", "MADation ViT-B/16 dnorm (diagnostic variant)",
        "MADation ViT-B/16 dscale (diagnostic variant)", "MixFaceNet-MAD release, our frames"]
SHORT = {"MADation ViT-L/14 release": "ViT-L/14 rel", "MADation ViT-B/16 release": "ViT-B/16 rel",
         "SelfMAD release, own preprocessing": "SelfMAD own crop", "SelfMAD release, our pipeline": "SelfMAD our frames",
         "MADation FE ViT-L/14 release": "FE ViT-L/14", "MADation FE ViT-B/16 release": "FE ViT-B/16",
         "MADation FS ViT-L/14 release": "FS ViT-L/14", "MADation FS ViT-B/16 release": "FS ViT-B/16",
         "MADation ViT-B/16 dnorm (diagnostic variant)": "ViT-B/16 dnorm", "MADation ViT-B/16 dscale (diagnostic variant)": "ViT-B/16 dscale",
         "MixFaceNet-MAD release, our frames": "MixFaceNet rel"}


def pct(x, nd=1):
    try:
        return f"{100 * float(x):.{nd}f}"
    except (TypeError, ValueError):
        return str(x) if x else "–"


def pci(r, k="false_alarm", lo="lo95", hi="hi95"):
    if r[k] in ("not scored", ""):
        return "n.s."
    s = pct(r[k])
    if r[lo] != "":
        s += f" [{pct(r[lo], 0)}–{pct(r[hi], 0)}]"
    return s


def seedsum(vals):
    v = [float(x) for x in vals if x not in ("", "not scored")]
    if not v:
        return "–"
    return f"{100 * np.mean(v):.1f} ({100 * min(v):.0f}–{100 * max(v):.0f})"


def partA():
    FA = rd("A1_false_alarms.csv")
    for a in ("0.05", "0.1"):
        print(f"\n### A1 False alarms at the fixed {pct(a, 0)}% development threshold (%, person-bootstrap 95% interval)\n")
        pools = ["FRLL orig", "FRLL jpeg90", "FRLL jpeg70", "FRLL jpeg50", "FRLL blur1", "FRLL resample50",
                 "FRLL orig, MorDIFF alignment"]
        hdr = ["detector", "dev"] + [p.replace("FRLL ", "") for p in pools] + ["resmatch max (pool)", "FEI all", "FFHQ orig"]
        print("| " + " | ".join(hdr) + " |")
        print("|" + "---|" * len(hdr))
        meta = json.load(open(O / "A_partA.json"))["meta"]
        for d in MAIN:
            R = {r["pool"]: r for r in FA if r["detector"] == d and r["alpha"] == a}
            rm = [r for p, r in R.items() if p.startswith("resmatch") and r["false_alarm"] != "not scored"]
            mx = max(rm, key=lambda r: float(r["false_alarm"]))
            dev = pct(meta[d][f"dev_fa_{float(a)}"]) + ("*" if "fallback" in meta[d]["threshold_source"] else "")
            cells = [pci(R[p]) if p in R else "–" for p in pools]
            print(f"| {SHORT[d]} | {dev} | " + " | ".join(cells) +
                  f" | {pci(mx)} ({mx['pool'].replace('resmatch ', '')}) | {pci(R['FEI all'])} | {pci(R['FFHQ orig'])} |")
        for meth in ("M3", "M3L"):
            R = [r for r in FA if r["block"] == meth and r["alpha"] == a]
            ns = sorted({r["detector"] for r in R})
            cells = [seedsum([r["false_alarm"] for r in R if r["pool"] == p]) for p in pools]
            rmx = [max(float(r["false_alarm"]) for r in R if r["detector"] == n and r["pool"].startswith("resmatch")) for n in ns]
            devs = [meta[n][f"dev_fa_{float(a)}"] for n in ns]
            print(f"| {meth} ({len(ns)} seeds: mean (range)) | {seedsum(devs)} | " + " | ".join(cells) +
                  f" | {seedsum(rmx)} | {seedsum([r['false_alarm'] for r in R if r['pool'] == 'FEI all'])} | n.s. |")
        R = [r for r in FA if r["block"] == "other recipe" and r["alpha"] == a]
        for meth in ("M1", "M2", "M4", "M5", "M6", "M8", "M8O"):
            RR = [r for r in R if r["detector"].startswith(meth + " ")]
            ns = sorted({r["detector"] for r in RR})
            cells = [seedsum([r["false_alarm"] for r in RR if r["pool"] == p]) for p in pools]
            rmx = [max(float(r["false_alarm"]) for r in RR if r["detector"] == n and r["pool"].startswith("resmatch")) for n in ns]
            print(f"| {meth} ({len(ns)} seeds, descriptive) | – | " + " | ".join(cells) +
                  f" | {seedsum(rmx)} | {seedsum([r['false_alarm'] for r in RR if r['pool'] == 'FEI all'])} | n.s. |")
    # resmatch per pool for the three highlighted detectors
    print("\n### A1b False alarms on the 12 E7 (resmatch) pools at the 5% threshold (%)\n")
    fams = list(K.FAMS)
    print("| detector | " + " | ".join(K.FAM_LABEL[f] for f in fams) + " |")
    print("|" + "---|" * (len(fams) + 1))
    for d in MAIN:
        R = {r["pool"]: r for r in FA if r["detector"] == d and r["alpha"] == "0.05"}
        print(f"| {SHORT[d]} | " + " | ".join(pci(R[f"resmatch {f}"]) for f in fams) + " |")
    for meth in ("M3", "M3L"):
        R = [r for r in FA if r["block"] == meth and r["alpha"] == "0.05"]
        print(f"| {meth} mean (range) | " + " | ".join(seedsum([r["false_alarm"] for r in R if r["pool"] == f"resmatch {f}"]) for f in fams) + " |")
    print("\nFFHQ resmatch pools and FEI by expression are in `A1_false_alarms.csv`.")
    # misses
    MS = rd("A2_miss.csv")
    for a in ("0.05", "0.1"):
        print(f"\n### A2 Miss rate per family at the native and the worst-pool threshold, α = {pct(a, 0)}% (%; native / worst-pool)\n")
        print("| detector | binding pool | " + " | ".join(K.FAM_LABEL[f] for f in fams) + " | family mean |")
        print("|" + "---|" * (len(fams) + 3))
        FMr = {r["detector"]: r for r in rd("A2_family_means.csv") if r["alpha"] == a}
        for d in MAIN:
            R = {(r["threshold_type"], r["family"]): r for r in MS if r["detector"] == d and r["alpha"] == a}
            cells = [f"{pct(R[('native', f)]['miss'])} / {pct(R[('worst-pool', f)]['miss'])}" for f in fams]
            fm = FMr[d]
            print(f"| {SHORT[d]} | {fm['binding_pool'].replace('resmatch ', 'E7 ')} | " + " | ".join(cells) +
                  f" | {pct(fm['native_family_mean_miss'])} / {pct(fm['worst_pool_family_mean_miss'])} |")
        for meth in ("M3", "M3L"):
            ns = sorted({r["detector"] for r in MS if r["block"] == meth})
            cells = []
            for f in fams:
                n_ = np.mean([float(r["miss"]) for r in MS if r["block"] == meth and r["alpha"] == a and r["family"] == f and r["threshold_type"] == "native"])
                w_ = np.mean([float(r["miss"]) for r in MS if r["block"] == meth and r["alpha"] == a and r["family"] == f and r["threshold_type"] == "worst-pool"])
                cells.append(f"{100 * n_:.1f} / {100 * w_:.1f}")
            fn = np.mean([float(FMr[n]["native_family_mean_miss"]) for n in ns])
            fw = np.mean([float(FMr[n]["worst_pool_family_mean_miss"]) for n in ns])
            print(f"| {meth} (seed mean of {len(ns)}) | – | " + " | ".join(cells) + f" | {100 * fn:.1f} / {100 * fw:.1f} |")
    # intervals for the three highlighted
    print("\n### A2b Worst-pool miss rate with intervals, α = 5% (%)\n")
    print("| detector | " + " | ".join(K.FAM_LABEL[f] for f in fams) + " |")
    print("|" + "---|" * (len(fams) + 1))
    for d in MAIN[:3]:
        R = {(r["threshold_type"], r["family"]): r for r in MS if r["detector"] == d and r["alpha"] == "0.05"}
        print(f"| {SHORT[d]} | " + " | ".join(pci(R[("worst-pool", f)], "miss") for f in fams) + " |")
    # ranking
    rk = json.load(open(O / "A_partA.json"))["ranking"]
    for a in ("0.05", "0.1"):
        r = rk[a]
        print(f"\n**Ranking, α = {pct(a, 0)}%:** Kendall τ-b (12 rows) = {r['kendall_tau_b']:.3f} (p {r['p']:.3f}); 23 rows "
              f"{r['kendall_tau_b_23rows']:.3f}; largest rise native → worst-pool {r['max_rise_points']:.1f} points; networks "
              f"with a rise ≥ 20 points: {r['n_rise_ge_20_points']} of 23. Falsifier reading: **{r['falsifier']}**.")
        print("\n| row | native family-mean EER (%) | worst-pool family-mean miss (%) |\n|---|---|---|")
        for n, x, y in zip(r["rows"], r["native_family_mean_eer"], r["worst_pool_family_mean_miss"]):
            print(f"| {SHORT.get(n, n)} | {x:.2f} | {100 * y:.1f} |")
    print("\nOwn-detector bar (false alarms > 10% on a gated pool at the 5% threshold), networks that would fail:")
    fails = rk["own_detector_bar_failures"]
    print(f"{len(fails)} of {len(json.load(open(O / 'A_partA.json'))['meta'])} networks;",
          "; ".join(f"{SHORT.get(k, k)}: {len(v)} pools" for k, v in list(fails.items())[:30]))
    # crossed table summary
    CR = rd("A3_crossed.csv")
    print("\n### A3 Crossed table (AUC; miss at 5% false alarms on that genuine variant), summary per label\n")
    print("| detector | family | native AUC | E7-matched AUC | G>M cells: min AUC (cell) | M>G cells: min AUC (cell) | matched: min AUC |")
    print("|---|---|---|---|---|---|---|")
    for d in MAIN[:3] + ["MADation FE ViT-L/14 release"]:
        for f in K.FRLLM:
            R = [r for r in CR if r["detector"] == d and r["family"] == f]
            if not R:
                continue
            g = lambda lab: [r for r in R if r["cell_label"] == lab]  # noqa: E731
            nat = g("native")
            e7 = g("E7-matched")
            mn = lambda L: (min(L, key=lambda r: float(r["auc"])) if L else None)  # noqa: E731
            gm, mg, mt = mn(g("G>M (genuine more processed)")), mn(g("M>G (morph more processed)")), mn(g("matched"))
            c = lambda r: f"{float(r['auc']):.3f} (m {r['morph_variant']} / g {r['genuine_variant']})" if r else "–"  # noqa: E731
            print(f"| {SHORT[d]} | {K.FAM_LABEL[f]} | {float(nat[0]['auc']):.3f} | {float(e7[0]['auc']):.3f} | {c(gm)} | {c(mg)} | "
                  f"{float(mt['auc']):.3f} ({mt['morph_variant']}) |" if mt else "")


def partB():
    C = rd("B_cells.csv")
    print("\n### B1 Null rows per cell (AUC; O = folded AUC for single attributes)\n")
    print("| cell | best non-content null | O | diagnostic | best aligned-frame null | O | thumbnail (content) | best morph-free network AUC |")
    print("|---|---|---|---|---|---|---|---|")
    for r in C:
        mfa = f"{float(r['best_morph_free_auc']):.3f}" if r["best_morph_free_auc"] else "–"
        print(f"| {r['cell']} | {r['best_noncontent_null']} | {float(r['best_noncontent_O']):.3f} | {r['diagnostic_primary']} | "
              f"{r['best_aligned_null']} | {float(r['best_aligned_O']):.3f} | {float(r['thumbnail_auc']):.3f} | "
              f"{mfa} |")
    N = rd("B_null_rows.csv")
    print("\n### B2 Selected null rows per cell (AUC or O)\n")
    names = ["file: width", "file: 5-attribute regression", "colour: 6 statistics, aligned frame", "colour: 6 statistics, stored file",
             "border: zero-border fraction", "expression label", "thumbnail 32 x 32 grey regression"]
    print("| cell | " + " | ".join(names) + " | morph-free M3 s1/s2/s3 | morph-free M1 s1/s2/s3 |")
    print("|" + "---|" * (len(names) + 3))
    for c in [r["cell"] for r in C]:
        R = {r["null"]: r for r in N if r["cell"] == c}
        v = [f"{float(R[n]['auc_or_O']):.3f}" if n in R else "–" for n in names]
        mf = lambda m: "/".join(f"{float(R[k]['auc_or_O']):.2f}" for k in sorted(R) if k.startswith(f"morph-free {m} ")) or "–"  # noqa: E731
        print(f"| {c} | " + " | ".join(v) + f" | {mf('M3')} | {mf('M1')} |")
    D = rd("B_detectors.csv")
    print("\n### B3 Detector AUC and paired excess over the best non-content null\n")
    cells = [r["cell"] for r in C if not r["cell"].startswith("MAD22c")]
    print("| detector | " + " | ".join(K.FAM_LABEL.get(c, c) for c in cells) + " |")
    print("|" + "---|" * (len(cells) + 1))
    for d in MAIN:
        R = {r["cell"]: r for r in D if r["detector"] == d}
        print(f"| {SHORT[d]} | " + " | ".join(f"{float(R[c]['auc']):.3f} ({float(R[c]['excess']):+.3f})" if c in R else "–" for c in cells) + " |")
    for meth in ("M3", "M3L"):
        R = [r for r in D if r["block"] == meth]
        print(f"| {meth} mean | " + " | ".join(f"{np.mean([float(r['auc']) for r in R if r['cell'] == c]):.3f}" for c in cells) + " |")
    print("\nNull-conditional AUC within quintiles of the best aligned-frame null (descriptive; ViT-L/14 / ViT-B/16 / SelfMAD own):\n")
    print("| cell | stratifying null | " + " | ".join(SHORT[d] for d in MAIN[:3]) + " |\n|---|---|---|---|---|")
    for c in cells:
        R = {r["detector"]: r for r in D if r["cell"] == c}
        print(f"| {K.FAM_LABEL.get(c, c)} | {R[MAIN[0]]['aligned_stratifying_null']} | " +
              " | ".join((f"{float(R[d]['nullcond_auc_aligned']):.3f} vs {float(R[d]['auc']):.3f} ({R[d]['usable_strata_aligned']} strata)"
                          if d in R and R[d]["nullcond_auc_aligned"] != "" else "no overlap") for d in MAIN[:3]) + " |")
    E = rd("B_expression.csv")
    print("\n### B4 Expression-balanced reading: AUC with all / neutral-only / smiling-only genuine photos; EER all / neutral / smiling (%)\n")
    print("| detector | cell | AUC all | AUC neutral-only [Δ 95%] | AUC smiling-only | EER all / neutral / smiling |\n|---|---|---|---|---|---|")
    for d in MAIN[:3]:
        for r in [r for r in E if r["detector"] == d]:
            print(f"| {SHORT[d]} | {K.FAM_LABEL.get(r['cell'], r['cell'])} | {float(r['auc_all']):.3f} | {float(r['auc_neutral_only']):.3f} "
                  f"[{float(r['d_neutral_lo95']):+.3f}, {float(r['d_neutral_hi95']):+.3f}] | {float(r['auc_smiling_only']):.3f} | "
                  f"{float(r['eer_all']):.1f} / {float(r['eer_neutral_only']):.1f} / {float(r['eer_smiling_only']):.1f} |")
    s = json.load(open(O / "B_partB.json"))["summary"]
    print("\nSummary:", json.dumps(s, indent=1))


def partC():
    OR = rd("C_oracle.csv")
    DS = rd("C_dose.csv")
    keys = [(r["family"], r["stratum"]) for r in OR]
    print("\n### C1 Oracle power check and contributor distance\n")
    print("| family | stratum | n | median δ | oracle ρ [95%] | power |\n|---|---|---|---|---|---|")
    for r in OR:
        o = "–" if r["rho_oracle"] == "" else f"{float(r['rho_oracle']):.3f} [{float(r['lo95']):.2f}, {float(r['hi95']):.2f}]"
        print(f"| {K.FAM_LABEL[r['family']]} | {r['stratum']} | {r['n']} | {float(r['delta_median']):.3f} | {o} | {r['power']} |")
    print("\n### C2 Spearman(score, δ) per family and stratum [95%]\n")
    lab = lambda k: f"{K.FAM_LABEL[k[0]]}{' smiling' if k[1] == 'smiling-smiling' else ''}"  # noqa: E731
    print("| detector | " + " | ".join(lab(k) for k in keys) + " |\n|" + "---|" * (len(keys) + 1))
    for d in MAIN:
        R = {(r["family"], r["stratum"]): r for r in DS if r["detector"] == d}
        print(f"| {SHORT[d]} | " + " | ".join((f"{float(R[k]['spearman']):+.2f} [{float(R[k]['lo95']):+.2f}, {float(R[k]['hi95']):+.2f}]"
                                                 if k in R else "–") for k in keys) + " |")
    for meth in ("M3", "M3L"):
        print(f"| {meth} seeds (range) | " + " | ".join(
            (lambda v: f"{min(v):+.2f} to {max(v):+.2f}")([float(r["spearman"]) for r in DS if r["block"] == meth and (r["family"], r["stratum"]) == k])
            for k in keys) + " |")
    fz = json.load(open(O / "C_partC.json"))["falsifiers"]
    print("\nFalsifiers:", json.dumps(fz["invariance_audit"], indent=1))
    for d in MAIN + sorted(k for k in fz["identity_audit"] if k.startswith("M3")):
        v = fz["identity_audit"].get(d)
        if v:
            print(f"- {SHORT.get(d, d)}: powered generator families {len(v['families_with_power'])}; UB ≤ 0.10 in "
                  f"{len(v['no_identity_reading_in'])}: {v['no_identity_reading_in']}; holds in every powered family: "
                  f"{v['statement_holds_in_every_powered_generator_family']}")




# ============================================================================ amendment 1 tables
SC = ("*Scores on our 512-pixel aligned frames (SelfMAD own preprocessing excepted); published release numbers are not "
      "reproduced there (released MADation ViT-L/14 on FRLL-Morphs AMSL: 17.7% EER here, 7.26% published). The own-crop "
      "re-score of the audit rows (RS1) redoes the key rows.*")


def amA():
    BL = rd("AM_A2_pool_block.csv")
    print("\n### AM-A2 Per-pool false alarms at the fixed 5% development threshold (FA %, exact 95% interval; photos that "
          "change side against FRLL orig: +flagged only in the pool / −flagged only in orig; persons with a change; exact McNemar p)\n")
    print(SC + "\n")
    for d in MAIN[:4]:
        print(f"\n**{d}**\n")
        print("| pool | neutral-only (102): FA [CP] | +/− | persons | p | all 204: FA [CP] | +/− | persons | p |\n|---|---|---|---|---|---|---|---|---|")
        R = [r for r in BL if r["detector"] == d and r["alpha"] == "0.05"]
        pools = []
        for r in R:
            if r["pool"] not in pools:
                pools.append(r["pool"])
        for p in pools:
            c = {r["subset"]: r for r in R if r["pool"] == p}
            def f(r):
                if r is None:
                    return ["–"] * 4
                if r["false_alarm"] == "not scored":
                    return ["not scored", "", "", ""]
                fa = f"{pct(r['false_alarm'])} [{pct(r['cp_lo'], 0)}–{pct(r['cp_hi'], 0)}]"
                if r["n_flagged_only_in_variant"] == "":
                    return [fa, "", "", ""]
                pv = float(r["mcnemar_exact_p"])
                return [fa, f"+{r['n_flagged_only_in_variant']}/−{r['n_flagged_only_in_orig']}", r["n_persons_changing_side"],
                        f"{pv:.1e}" if pv < 0.001 else f"{pv:.3f}"]
            if "neutral-only" in c:
                print(f"| {p} | " + " | ".join(f(c.get("neutral-only")) + f(c.get("all"))) + " |")
            else:
                print(f"| {p} | – | | | | " + " | ".join(f(c.get("all"))) + " |")
    PO = rd("AM_A1_class_policies.csv")
    for st in ("MorDIFF", "StyleGAN3"):
        print(f"\n### AM-A1 {st} controls under both class policies, 5% development threshold (rate %, exact 95% interval)\n")
        print(SC + "\n")
        dets = [d for d in MAIN if any(r["detector"] == d and r["set"] == st for r in PO)]
        rules = ["native threshold", "worst-pool, policy X (inadmissible)", "worst-pool, policy G (genuine)"]
        print("| detector | image set | rate | native threshold | worst-pool, policy X (left out) | worst-pool, policy G (counted genuine) |\n|---|---|---|---|---|---|")
        for d in dets:
            R = [r for r in PO if r["detector"] == d and r["set"] == st and r["alpha"] == "0.05"]
            sets = []
            for r in R:
                if r["pool"] not in sets:
                    sets.append(r["pool"])
            for p in sets:
                c = {r["threshold_rule"]: r for r in R if r["pool"] == p}
                cells = [f"{pct(c[k]['rate'])} [{pct(c[k]['cp_lo'], 0)}–{pct(c[k]['cp_hi'], 0)}]" for k in rules]
                print(f"| {SHORT[d]} | {p} | {c[rules[0]]['rate_type']} | " + " | ".join(cells) + " |")
    SH = rd("AM_A3_neutral_above_smiling.csv")
    print("\n### AM-A3 Within-person share of persons whose neutral photo scores above their smiling photo (95% person bootstrap)\n")
    print(SC + "\n")
    cols = ["FRLL orig", "stored-small arm E", "FRLL jpeg70", "FRLL jpeg50", "FRLL resample50", "FRLL orig, MorDIFF alignment",
            "E7 amsl", "E7 mordiff", "E7 dim_a", "E7 greedy_dim", "FEI neutral vs smiling frontal"]
    print("| detector | " + " | ".join(cols) + " |\n|" + "---|" * (len(cols) + 1))
    for d in MAIN:
        R = {r["pool"]: r for r in SH if r["detector"] == d}
        cell = lambda r: "–" if r is None else ("n.s." if r["share_neutral_above_smiling"] == "not scored" else  # noqa: E731
                                                f"{float(r['share_neutral_above_smiling']):.2f}" + (f" [{float(r['lo95']):.2f}, {float(r['hi95']):.2f}]" if r["lo95"] else ""))
        print(f"| {SHORT[d]} | " + " | ".join(cell(R.get(c)) for c in cols) + " |")
    for meth in ("M3", "M3L"):
        R = [r for r in SH if r["block"] == meth]
        out = []
        for c in cols:
            v = [float(r["share_neutral_above_smiling"]) for r in R if r["pool"] == c and r["share_neutral_above_smiling"] not in ("", "not scored")]
            out.append(f"{min(v):.2f}–{max(v):.2f}" if v else "–")
        print(f"| {meth} seeds (range) | " + " | ".join(out) + " |")
    note = [r["note"] for r in SH if r["pool"].startswith("FEI")]
    print(f"\nFEI label: {note[0] if note else '–'}; corner check: {json.dumps(json.load(open(O / 'AM_corner_check.json')))}")
    NE = rd("AM_A3_worstpool_neutral.csv")
    print("\n### AM-A3 Worst-pool miss rate, α = 5%: gated FRLL pools restricted to neutral photos (headline) / all photos (%)\n")
    print(SC + "\n")
    fams = list(K.FAMS)
    print("| detector | " + " | ".join(K.FAM_LABEL[f] for f in fams) + " |\n|" + "---|" * (len(fams) + 1))
    for d in MAIN[:4]:
        R = {(r["threshold_rule"], r["family"]): r for r in NE if r["detector"] == d and r["alpha"] == "0.05"}
        print(f"| {SHORT[d]} | " + " | ".join(f"{pct(R[('worst-pool, neutral-only gated pools', f)]['miss'])} / {pct(R[('worst-pool, all photos (Part A)', f)]['miss'])}" for f in fams) + " |")
    CN = rd("AM_A3_crossed_neutral.csv")
    print("\n### AM-A3 Crossed table, neutral-only genuine photos (AUC; all-photo AUC in brackets), morph orig column\n")
    print(SC + "\n")
    gvs = list(K.GVARS) + ["resmatch"]
    print("| detector | family | " + " | ".join(f"genuine {g}" for g in gvs) + " |\n|" + "---|" * (len(gvs) + 2))
    for d in MAIN[:3]:
        for f in K.FRLLM + K.DIM:
            R = {r["genuine_variant"]: r for r in CN if r["detector"] == d and r["family"] == f and r["morph_variant"] == "orig"}
            if not R:
                continue
            print(f"| {SHORT[d]} | {K.FAM_LABEL[f]} | " + " | ".join(
                (f"{float(R[g]['auc_neutral_only']):.3f} ({float(R[g]['auc_all_photos']):.3f})" if g in R else "n.s.") for g in gvs) + " |")


def amB():
    CE = rd("AM_B_cells_neutral.csv")
    print("\n### AM-B Null rows with the neutral-only genuine class (headline for the imbalanced cells) and all photos\n")
    print(SC + "\n")
    print("| cell | genuine class | best non-content null | O | diagnostic | best aligned-frame null | O | thumbnail |\n|---|---|---|---|---|---|---|---|")
    for r in CE:
        print(f"| {r['cell']} | {r['genuine_class']} | {r['best_noncontent_null']} | {float(r['O']):.3f} | {r['diagnostic']} | "
              f"{r['best_aligned_null']} | {float(r['O_aligned']):.3f} | {float(r['thumbnail_auc']):.3f} |")
    SP = rd("AM_B_splithalf.csv")
    print("\n### AM-B Split-half choice of the best per-image non-content null (chosen on one half of the persons, AUC on the other)\n")
    print("| cell | genuine class | split | chosen null | O on choice half | AUC on report half | diagnostic |\n|---|---|---|---|---|---|---|")
    for r in SP:
        a = r["auc_on_report_half"]
        print(f"| {r['cell']} | {r['genuine_class']} | {r['split']} | {r['chosen_null']} | {float(r['O_on_selection_half']):.3f} | "
              f"{'–' if a in ('', 'nan') else f'{float(a):.3f}'} | {r['diagnostic_on_report_half']} |")
    DT = rd("AM_B_detectors_neutral.csv")
    print("\n### AM-B Detector AUC / EER (%) with the neutral-only genuine class (headline) and all photos, imbalanced cells\n")
    print(SC + "\n")
    cells = sorted({r["cell"] for r in DT}, key=lambda c: list(K.FAMS).index(c) if c in K.FAMS else 99)
    print("| detector | " + " | ".join(K.FAM_LABEL.get(c, c) for c in cells) + " |\n|" + "---|" * (len(cells) + 1))
    for d in MAIN:
        R = {(r["cell"], r["genuine_class"]): r for r in DT if r["detector"] == d}
        def cc(c):
            n, a = R.get((c, "neutral-only")), R.get((c, "all photos"))
            if n is None and a is None:
                return "–"
            if n is None:
                return f"{float(a['auc']):.3f} / {float(a['eer_pct']):.1f} (balanced)"
            return f"**{float(n['auc']):.3f} / {float(n['eer_pct']):.1f}** ({float(a['auc']):.3f} / {float(a['eer_pct']):.1f})"
        print(f"| {SHORT[d]} | " + " | ".join(cc(c) for c in cells) + " |")
    print("\nSummary:", json.dumps(json.load(open(O / "AM_partB.json"))["summary"], indent=1))


def amC():
    CT = rd("AM_C_controls.csv")
    print("\n### AM-C Controls for the identity-dose slope: strata where a control's 95% interval excludes 0\n")
    for r in CT:
        if r["has_slope"] == "True":
            print(f"- {r['control']}: {K.FAM_LABEL[r['family']]} {r['stratum']}: {float(r['spearman']):+.3f} [{float(r['lo95']):+.3f}, {float(r['hi95']):+.3f}] (n {r['n']})")
    print("\nReadings:", json.dumps(json.load(open(O / "AM_partC.json"))["readings"], indent=1))
    DG = rd("AM_C_mordiff_gender.csv")
    print("\n### AM-C MorDIFF identity-dose slope by expression subset and gender (Spearman [95%])\n")
    st = sorted({r["stratum"] for r in DG})
    print("| detector | " + " | ".join(st) + " |\n|" + "---|" * (len(st) + 1))
    for d in MAIN:
        R = {r["stratum"]: r for r in DG if r["detector"] == d}
        print(f"| {SHORT[d]} | " + " | ".join(f"{float(R[s]['spearman']):+.2f} [{float(R[s]['lo95']):+.2f}, {float(R[s]['hi95']):+.2f}]" for s in st) + " |")
    for meth in ("M3", "M3L"):
        print(f"| {meth} seeds (range) | " + " | ".join(
            (lambda v: f"{min(v):+.2f} to {max(v):+.2f}")([float(r["spearman"]) for r in DG if r["block"] == meth and r["stratum"] == s]) for s in st) + " |")


# ============================================================================ amendment 2 tables
REL = [n for n in MAIN] + []


def am2():
    B1 = rd("AM2_B1_rule05.csv")
    print("\n### AM2-B1 Flag rate at each release's own 0.5 rule (probability of morph > 0.5), % [CP]\n")
    print(SC + "\n")
    pools = ["devbona", "FRLL orig", "FRLL jpeg50", "FRLL resample50", "FRLL orig, MorDIFF alignment", "stored-small (arm E)",
             "E7 amsl", "E7 webmorph", "E7 mordiff", "E7 dim_a", "E7 greedy_dim", "FEI neutral", "FEI smiling", "FFHQ orig", "FFHQ E7 landmark_complete",
             "H3 one-identity renders"]
    print("| detector | " + " | ".join(pools) + " |\n|" + "---|" * (len(pools) + 1))
    for d in MAIN:
        R = {r["pool"]: r for r in B1 if r["detector"] == d and r["subset"] == "all"}
        c = lambda r: "–" if r is None else ("n.s." if r["flag_rate"] == "not scored" else f"{pct(r['flag_rate'])}")  # noqa: E731
        print(f"| {SHORT[d]} | " + " | ".join(c(R.get(p)) for p in pools) + " |")
    print("\nMorph detection at the 0.5 rule (%), and the E7 genuine pool of the same family beside it (genuine flagged %):\n")
    print("| detector | " + " | ".join(K.FAM_LABEL[f] for f in K.FAMS) + " | family-mean miss |\n|" + "---|" * (len(K.FAMS) + 2))
    for d in MAIN:
        R = {r["pool"]: r for r in B1 if r["detector"] == d and r["subset"] == "all"}
        cells, det = [], []
        for f in K.FAMS:
            m, g = R.get(f"morph {f}"), R.get(f"E7 {f}")
            if m is None or m["flag_rate"] == "not scored":
                cells.append("n.s."); continue
            det.append(float(m["flag_rate"]))
            gg = "n.s." if g is None or g["flag_rate"] == "not scored" else pct(g["flag_rate"])
            mark = " **G≥M**" if gg != "n.s." and float(g["flag_rate"]) >= float(m["flag_rate"]) else ""
            cells.append(f"{pct(m['flag_rate'])} / {gg}{mark}")
        print(f"| {SHORT[d]} | " + " | ".join(cells) + f" | {100 - 100 * np.mean(det):.1f} |" if det else "")
    B2 = rd("AM2_B2_logit_shift.csv")
    print("\n### AM2-B2 Paired logit shift against the same photos' FRLL orig: median [95%], share of photos rising, crossings (dev threshold up/down; 0.5 rule up/down)\n")
    print(SC + "\n")
    for d in MAIN:
        R = [r for r in B2 if r["detector"] == d and r["n"] not in ("", "not scored") and r["median_shift"] != "not scored"]
        if not R:
            continue
        print(f"\n**{d}**\n\n| pool | effective IED px | median shift [95%] | mean shift [95%] | share rising | dev thr +/− | 0.5 rule +/− |\n|---|---|---|---|---|---|---|")
        for r in R:
            print(f"| {r['pool']} | {float(r['median_ied_px']):.0f} | {float(r['median_shift']):+.3f} [{float(r['median_lo95']):+.3f}, {float(r['median_hi95']):+.3f}] | "
                  f"{float(r['mean_shift']):+.3f} [{float(r['mean_lo95']):+.3f}, {float(r['mean_hi95']):+.3f}] | {100 * float(r['share_up']):.0f}% | "
                  f"+{r['devthr_up']}/−{r['devthr_down']} | +{r['rule05_up']}/−{r['rule05_down']} |")
    SA = rd("AM2_B2_saturation.csv")
    print("\n### AM2-B2 Saturation: logit 1st / 50th / 99th percentile\n")
    cols = ["devbona", "FRLL orig"] + [f"morph {f}" for f in K.FAMS]
    print("| detector | " + " | ".join(cols) + " |\n|" + "---|" * (len(cols) + 1))
    for d in MAIN:
        R = {r["pool"]: r for r in SA if r["detector"] == d}
        print(f"| {SHORT[d]} | " + " | ".join((f"{float(R[c]['logit_p1']):.2f} / {float(R[c]['logit_p50']):.2f} / {float(R[c]['logit_p99']):.2f}" if c in R else "–") for c in cols) + " |")
    B3 = rd("AM2_B3_miss_by_threshold_pool.csv")
    CI = rd("AM2_B3_summary_ci.csv")
    print("\n### AM2-B3 Family-mean miss % by threshold pool, 5% false alarms on that pool [95% person bootstrap, threshold refit]\n")
    print(SC + "\n")
    rules = ["devbona (Part A native)", "unprocessed FRLL photos (all 204)", "unprocessed FRLL photos (neutral-only 102)",
             "full-frame pools, inter-eye distance >= 100 px", "full-frame pools >= 100 px, with devbona",
             "every history-matched pool (Part A gated set, with devbona)"]
    print("| detector | " + " | ".join(rules) + " | range over single pools |\n|" + "---|" * (len(rules) + 2))
    for d in MAIN + ["M3", "M3L"]:
        if d in ("M3", "M3L"):
            R = [r for r in B3 if r["block"] == d and r["alpha"] == "0.05"]
            cell = lambda rn: f"{100 * np.mean([float(r['family_mean_miss']) for r in R if r['threshold_pool'] == rn]):.1f} (seed mean)"  # noqa: E731
            sp = [float(r["family_mean_miss"]) for r in R if r["threshold_pool"].startswith("single pool")]
            print(f"| {d} | " + " | ".join(cell(rn) for rn in rules) + f" | {100 * min(sp):.1f}–{100 * max(sp):.1f} |")
            continue
        R = {r["threshold_pool"]: r for r in B3 if r["detector"] == d and r["alpha"] == "0.05"}
        C = {r["threshold_pool"]: r for r in CI if r["detector"] == d and r["alpha"] == "0.05"}
        def cell(rn):
            if rn not in R:
                return "–"
            v = f"{100 * float(R[rn]['family_mean_miss']):.1f}"
            if rn in C:
                v += f" [{100 * float(C[rn]['lo95']):.0f}–{100 * float(C[rn]['hi95']):.0f}]"
            return v
        sp = [(float(r["family_mean_miss"]), k) for k, r in R.items() if k.startswith("single pool")]
        lo, hi = min(sp), max(sp)
        print(f"| {SHORT[d]} | " + " | ".join(cell(rn) for rn in rules) + f" | {100 * lo[0]:.1f} ({lo[1][13:]}) – {100 * hi[0]:.1f} ({hi[1][13:]}) |")
    B4 = rd("AM2_B4_border_pairing.csv")
    print("\n### AM2-B4 Border-matched pairing for the MorDIFF frame (paired logit shift, median [95%])\n")
    print(SC + "\n")
    print("| detector | pool | against | border pool / ref | IED pool / ref | median shift [95%] | share rising | dev thr +/− | 0.5 rule +/− |\n|---|---|---|---|---|---|---|---|---|")
    for d in MAIN:
        for r in [r for r in B4 if r["detector"] == d]:
            print(f"| {SHORT[d]} | {r['pool']} | {r['reference_pool']} | {float(r['median_border_pool']):.2f} / {float(r['median_border_ref']):.2f} | "
                  f"{float(r['median_ied_pool']):.0f} / {float(r['median_ied_ref']):.0f} | {float(r['median_logit_shift']):+.3f} [{float(r['lo95']):+.3f}, {float(r['hi95']):+.3f}] | "
                  f"{100 * float(r['share_up']):.0f}% | +{r['devthr_up']}/−{r['devthr_down']} | +{r['rule05_up']}/−{r['rule05_down']} |")
    A4 = rd("AM2_B4_mordiff_auc.csv")
    print("\nMorDIFF morphs against tight-frame genuine pools (AUC [95%]):\n\n| detector | genuine pool | border morph / genuine | AUC |\n|---|---|---|---|")
    for d in MAIN:
        for r in [r for r in A4 if r["detector"] == d]:
            print(f"| {SHORT[d]} | {r['genuine_pool']} | {float(r['median_border_morph']):.2f} / {float(r['median_border_genuine']):.2f} | {float(r['auc']):.3f} [{float(r['lo95']):.3f}, {float(r['hi95']):.3f}] |")
    B5 = rd("AM2_B5_ffhq_paired.csv")
    print("\n### AM2-B5 Paired FFHQ block: FFHQ orig against each E7 pool (2,000 pairs)\n")
    print(SC + "\n")
    print("| detector | E7 pool (history IED px) | FA dev thr orig → E7 (+/−, p) | 0.5 rule orig → E7 (+/−, p) | median logit shift [95%] | share rising |\n|---|---|---|---|---|---|")
    for d in MAIN:
        for r in [r for r in B5 if r["detector"] == d]:
            print(f"| {SHORT[d]} | {r['ffhq_e7_pool']} ({float(r['history_ied_px']):.0f}) | {pct(r['fa_devthr_orig'])} → {pct(r['fa_devthr_e7'])} (+{r['devthr_up']}/−{r['devthr_down']}, {float(r['devthr_mcnemar_p']):.1e}) | "
                  f"{pct(r['rule05_orig'], 2)} → {pct(r['rule05_e7'], 2)} (+{r['rule05_up']}/−{r['rule05_down']}, {float(r['rule05_mcnemar_p']):.1e}) | "
                  f"{float(r['median_logit_shift']):+.3f} [{float(r['median_lo95']):+.3f}, {float(r['median_hi95']):+.3f}] | {100 * float(r['share_up']):.0f}% |")


if __name__ == "__main__":
    for part in sys.argv[1:] or ["A", "B", "C", "amA", "amB", "amC", "am2"]:
        {"A": partA, "B": partB, "C": partC, "amA": amA, "amB": amB, "amC": amC, "am2": am2}[part]()

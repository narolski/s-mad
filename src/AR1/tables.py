"""Markdown tables for result.md from result_tables.json, gate_c.json, baselines.json (no computation)."""
import json
import sys

R = "/home/narolski/smad-next/experiments/AR1/"


def f(x, d=3):
    return "-" if x is None or x != x else f"{x:.{d}f}"


def ci(c, d=2):
    return "-" if not c or c[0] is None else f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"


def main():
    T = json.load(open(sys.argv[1] if len(sys.argv) > 1 else R + "result_tables.json"))
    out = []
    for variant, (base, twin) in (("A", ("R2", "R3")), ("B", ("R2w", "R3")), ("C", ("R2w", "R3m")),
                                  ("D", ("R2wm", "R3m")), ("E", ("R2w4", "R3"))):
        out.append(f"\n#### Ladder {variant}: R0 -> {base} -> {twin} -> R4 (main contrast {base} vs R4)\n")
        out.append(f"| Detector | Pool / tool | R0->{base} AUC [CI] (share) | {base}->{twin} AUC [CI] (share) | "
                   f"{twin}->R4 AUC [CI] (share) | {base} vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | "
                   f"side {twin} vs R4 | side {base} vs {twin} |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for name, r in T.items():
            for cell in ("frgcferet/opencv", "frgcferet/facemorpher", "frll/opencv", "frll/facemorpher",
                         "frll_clean/opencv", "frll_clean/facemorpher"):
                L = r.get(f"{cell}/{base}-{twin}") or (r.get(f"{cell}/{base}-{twin}-R4nn") if variant == "D" else None)
                if not L or "skipped" in L:
                    continue
                def st(k):
                    x = L[k]
                    return f"{f(x['auc'])} {ci(x['ci95'])} ({f(x.get('share'), 2)})"
                out.append(f"| {name} | {cell} | {st('R0->' + base)} | {st(base + '->' + twin)} | {st(twin + '->R4')} | "
                           f"{st(base + 'vsR4')} | {f(L['R0vsR4']['auc'])} {ci(L['R0vsR4']['ci95'])} | {L['main_verdict']} | "
                           f"{L['side_twin_vs_R4']} | {L['side_base_vs_twin']} |")
    # extra contrasts, baselines, sensitivity, flag rates (primary pool)
    out.append("\n#### Key contrasts on the primary pool (ladder B rows), with the best simple baseline\n")
    out.append("| Detector | tool | contrast | detector AUC [CI] | best simple baseline (AUC) | excess [CI] | best non-content (AUC) | excess [CI] |")
    out.append("|---|---|---|---|---|---|---|---|")
    for name, r in T.items():
        for tool in ("opencv", "facemorpher"):
            L = r.get(f"frgcferet/{tool}/R2w-R3")
            if not L or "skipped" in L:
                continue
            for cn, vb in (L.get("vs_baselines") or {}).items():
                src = L.get(cn) or {}
                si, nc = vb.get("simple", {}), vb.get("noncontent", {})
                out.append(f"| {name} | {tool} | {cn} | {f(vb.get('detector_auc'))} {ci(src.get('ci95'))} | "
                           f"{si.get('best')} ({f(si.get('best_auc'))}) | {f(si.get('excess'))} {ci(si.get('excess_ci95'))} | "
                           f"{nc.get('best')} ({f(nc.get('best_auc'))}) | {f(nc.get('excess'))} {ci(nc.get('excess_ci95'))} |")
    out.append("\n#### Extra warp contrasts (primary pool)\n")
    out.append("| Detector | tool | R0 vs R2w4 | R2w vs R2w4 | R2w4 vs R4 | R3m vs R3 |")
    out.append("|---|---|---|---|---|---|")
    for name, r in T.items():
        for tool in ("opencv", "facemorpher"):
            L = r.get(f"frgcferet/{tool}/R2w-R3")
            if not L or "skipped" in L:
                continue
            g = lambda k: f"{f(L[k]['auc'])} {ci(L[k]['ci95'])}" if k in L else "-"  # noqa
            out.append(f"| {name} | {tool} | {g('R0vsR2w4')} | {g('R2wvsR2w4')} | {g('R2w4vsR4')} | {g('R3mvsR3')} |")
    out.append("\n#### Sensitivity without the 8 validation-reserved hosts (primary, ladder B)\n")
    out.append("| Detector | tool | R2w vs R4 all | without 8 | R0 vs R4 all | without 8 |")
    out.append("|---|---|---|---|---|---|")
    for name, r in T.items():
        for tool in ("opencv", "facemorpher"):
            L = r.get(f"frgcferet/{tool}/R2w-R3")
            if not L or "skipped" in L or "sensitivity_without_val8" not in L:
                continue
            sv = L["sensitivity_without_val8"]
            out.append(f"| {name} | {tool} | {f(L['R2wvsR4']['auc'])} | {f(sv['R2wvsR4']['auc'])} {ci(sv['R2wvsR4']['ci95'])} | "
                       f"{f(L['R0vsR4']['auc'])} | {f(sv['R0vsR4']['auc'])} |")
    out.append("\n#### Flag rates at the detector's FRLL benchmark EER threshold (neutral genuine), primary pool\n")
    out.append("| Detector | tool | bench EER | R0 | R2w | R3 (twin) | R3m | R2w4 | R4 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for name, r in T.items():
        for tool in ("opencv", "facemorpher"):
            L = r.get(f"frgcferet/{tool}/R2w-R3")
            if not L or "bench_threshold" not in L:
                continue
            bt = L["bench_threshold"]
            g = lambda k: (f"{100*bt[k][0]:.1f}% [{100*bt[k][1][0]:.1f}, {100*bt[k][1][1]:.1f}]" if k in bt else "-")  # noqa
            out.append(f"| {name} | {tool} | {f(bt['bench_eer'], 2)} | {g('flag_rate_R0')} | {g('flag_rate_R2w')} | "
                       f"{g('flag_rate_R3')} | {g('flag_rate_R3m')} | {g('flag_rate_R2w4')} | {g('flag_rate_R4')} |")
    out.append("\n#### FRLL benchmark side and bridge\n")
    out.append("| Detector | tool | genuine | R4pub vs R0raw | R1f (E7) vs R0f | R4f vs R0f | E7 share | bench EER | bridge pub vs ours [CI] | detect pub / ours |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for name, r in T.items():
        for tool in ("opencv", "facemorpher"):
            Bk = r.get(f"frll_bench/{tool}")
            if not Bk:
                continue
            for gen in ("neutral_only", "all_photos"):
                o = Bk[gen]
                g = lambda k: f"{f(o[k]['auc'])} {ci(o[k]['ci95'])}" if k in o else "-"  # noqa
                br = Bk.get("bridge_pub_vs_ours", {})
                out.append(f"| {name} | {tool} | {gen} | {g('R4pub_vs_R0raw (benchmark, raw files)')} | {g('R1f_vs_R0f (E7 step)')} | "
                           f"{g('R4f_vs_R0f')} | {f(o.get('E7_share_of_R4f_vs_R0f'), 2)} | {f(o.get('bench_eer'), 2)} | "
                           f"{f(br.get('auc')) + ' ' + ci(br.get('ci95')) if gen == 'neutral_only' and br else ''} | "
                           f"{(f(Bk.get('detect_rate_published'), 2) + ' / ' + f(Bk.get('detect_rate_ours'), 2)) if gen == 'neutral_only' and 'detect_rate_ours' in Bk else ''} |")
    out.append("\n#### AR2 graded FaceMorpher mixing (300 hosts): mean logit per level, Page trend test, AUC vs m = 0\n")
    out.append("| Detector | mean logit m=0 / .1 / .2 / .3 / .4 / .5 | Page L, p | AUC(m vs 0) .1 / .2 / .3 / .4 / .5 |")
    out.append("|---|---|---|---|")
    for name, r in T.items():
        G = r.get("AR2_graded_fm")
        if not G:
            continue
        out.append(f"| {name} | {' / '.join(f(x, 2) for x in G['mean_logit'])} | {G['page_L']:.0f}, {G['page_p']:.2g} | "
                   f"{' / '.join(f(v['auc']) for v in G['auc_vs_m0'].values())} |")
    out.append("\n#### AR4 blanking (primary pool): AUC with background blanked / face blanked\n")
    out.append("| Detector | tool | variant | R2w vs R4 | R0 vs R4 | R3 vs R4 | R0 vs R2w | works? |")
    out.append("|---|---|---|---|---|---|---|---|")
    for name, r in T.items():
        for v in ("bg", "face"):
            for tool in ("opencv", "facemorpher"):
                o = r.get(f"AR4_{v}_blanked/frgcferet/{tool}")
                if not o:
                    continue
                g = lambda k: f"{f(o[k]['auc'])} {ci(o[k]['ci95'])}" if k in o else "-"  # noqa
                out.append(f"| {name} | {tool} | {v} blanked | {g('R2wvsR4')} | {g('R0vsR4')} | {g('R3vsR4')} | {g('R0vsR2w')} | {o['works']} |")
    print("\n".join(out))


if __name__ == "__main__":
    main()

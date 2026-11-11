"""AG1 facts table (no interpretation): from ag1_read.py's ag1_read.json and gates.json, one markdown file with, per
generator x pool x release row: every contrast's AUC [95% interval] (n), the best simple baseline and the excess over
it, flag rates at the corrected-MAD22 EER threshold under both class policies, and the gate labels.
Usage: python -I ag1_facts.py READ_DIR OUT.md
"""
import json
import pathlib
import sys

ORDER = ("R0>R1", "R1>R2", "R0>R2", "R2>R3m (mirror, own rung)", "R2>R3", "R3>R4", "R2>R4",
         "R2s>R4 (spread-matched one-person render)", "R3m>R4 (mirror, own rung)", "R0>R4", "R3>RT (noise floor)",
         "R0>PUB", "R2>PUB (AG2)", "bridge PUB vs BR")


def f(x, d=3):
    return "-" if x is None else f"{x:.{d}f}"


def main():
    rd = pathlib.Path(sys.argv[1])
    R = json.load(open(rd / "ag1_read.json"))
    G = json.load(open(rd / "gates.json"))
    L = ["# AG1 facts table (no interpretation)", "",
         "Contrast 'X>Y' = AUC of the detector score of rung Y against rung X (0.5 = no separation; above 0.5 = Y "
         "scores higher). Intervals: two-way person bootstrap. Excess = detector AUC minus the best simple baseline "
         "on the same images.", ""]
    L.append("## Gates")
    for k, v in G["G-b"].items():
        L.append(f"- G-b {k}: {v['label']}; oracle AUC R4 vs R3 {f(v['oracle_auc_R4_vs_R3'])}; R4 verifies both "
                 f"(input) {f(v['R4_verifies_both_input'])}, (unseen) {f(v['R4_verifies_both_unseen'])}; R3 verifies A "
                 f"{f(v['R3_verifies_A_input'])}; R2 false-match rate {f(v['R2_false_match_rate'], 4)}; thr {f(v['thr_fmr1e-3'])}")
    L.append(f"- RT: {G['RT']}")
    L.append("")
    for cell, v in R.items():
        if cell.startswith("_"):
            continue
        L += [f"## {cell} ({v['release_row']}{', primary cell' if v['primary'] else ''})", "",
              f"Reading A: {v['main_A']}; reading B: {v['main_B']}; R3 vs R4: {v['side_R3_R4']}; R2 vs R3: "
              f"{v['side_R2_R3']}; AG2: {v.get('AG2', '-')}; G-a: {v.get('G-a', '-')}; benchmark EER "
              f"{f(v.get('benchmark_eer_pct'), 2)}%; p(R2 vs R4 <= 0.65) {f(v['p_reads_morphing'], 4)}"
              + (f", Holm within AG1 {f(v['p_reads_morphing_holm_within_AG1'], 4)}" if 'p_reads_morphing_holm_within_AG1' in v else ""),
              "", "| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |", "|---|---|---|---|---|---|"]
        for k in ORDER:
            c = v.get(k)
            if not c:
                continue
            b = c.get("baselines", {})
            ex = c.get("excess_over_best_baseline", {})
            L.append(f"| {k} | {f(c['auc'])} [{f(c['ci'][0])}, {f(c['ci'][1])}] | {c['n'][0]} / {c['n'][1]} | "
                     f"{c.get('best_baseline', '-')} ({f(b.get(c.get('best_baseline')))}) | {f(b.get('sym'))} | "
                     f"{f(ex.get('excess'))} [{f((ex.get('ci') or [None])[0])}, {f((ex.get('ci') or [None, None])[1])}] |")
        fr = v.get("flag_rates_at_benchmark_thr")
        if fr:
            L += ["", "Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:"]
            for k, x in fr.items():
                if k == "single-subject table":
                    L.append("- single-subject: " + "; ".join(f"{kk} {f(xx[0])} [{f(xx[1])}, {f(xx[2])}]" for kk, xx in x.items()))
                else:
                    L.append(f"- {k}: {f(x[0])} [{f(x[1])}, {f(x[2])}]")
        L.append(f"- latent distance medians: {v.get('latdist_median')}")
        mb = v.get("R3_R4_matched_bins (also reported)")
        if mb:
            L.append(f"- R3 vs R4 matched bins (also reported): {mb.get('reading')}, pooled {f(mb.get('pooled_auc'))}, "
                     f"coverage {f(mb.get('covered_R4'))}")
        sg = v.get("R3_R4_session_gap")
        if sg and sg.get("within60"):
            w = sg["within60"]
            L.append(f"- R3 vs R4 within 60 days: {f(w['auc'])} [{f(w['ci'][0])}, {f(w['ci'][1])}] n {w['n']}")
        for arm, d in (v.get("dose") or {}).items():
            lv = "; ".join(f"{a}: {f(x['auc_vs_R2'])}" for a, x in d["levels"].items())
            L.append(f"- {arm} levels vs R2: {lv}; {d['reading']}")
        L.append("")
    L.append(f"Not scored: {R.get('_not_scored')}")
    pathlib.Path(sys.argv[2]).write_text("\n".join(L) + "\n")
    print("FACTS", sys.argv[2])


if __name__ == "__main__":
    main()

"""Markdown tables for result.md from result_tables.json, gate_c.json, baselines.json (no computation)."""
import json
import sys

R = "/home/narolski/smad-next/experiments/AR1/"


def f(x, d=3):
    return "-" if x is None or x != x else f"{x:.{d}f}"


def ci(c, d=2):
    return "-" if not c or c[0] is None else f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"


def main():
    T = json.load(open(R + "result_tables.json"))
    out = []
    for variant, (base, twin) in (("A", ("R2", "R3")), ("B", ("R2w", "R3")), ("C", ("R2w", "R3m"))):
        out.append(f"\n#### Ladder {variant}: R0 -> {base} -> {twin} -> R4 (main contrast {base} vs R4)\n")
        out.append(f"| Detector | Pool / tool | R0->{base} AUC [CI] (share) | {base}->{twin} AUC [CI] (share) | "
                   f"{twin}->R4 AUC [CI] (share) | {base} vs R4 AUC [CI] (share) | R0 vs R4 | main verdict | "
                   f"side {twin} vs R4 | side {base} vs {twin} |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for name, r in T.items():
            for cell in ("frgcferet/opencv", "frgcferet/facemorpher", "frll/opencv", "frll/facemorpher"):
                L = r.get(f"{cell}/{base}-{twin}")
                if not L:
                    continue
                def st(k):
                    x = L[k]
                    return f"{f(x['auc'])} {ci(x['ci95'])} ({f(x.get('share'), 2)})"
                out.append(f"| {name} | {cell} | {st('R0->' + base)} | {st(base + '->' + twin)} | {st(twin + '->R4')} | "
                           f"{st(base + 'vsR4')} | {f(L['R0vsR4']['auc'])} {ci(L['R0vsR4']['ci95'])} | {L['main_verdict']} | "
                           f"{L['side_twin_vs_R4']} | {L['side_base_vs_twin']} |")
    print("\n".join(out))


if __name__ == "__main__":
    main()

"""Compact tables from metrics_<backbone>_<tag>.json for result.md (markdown to stdout).
  python3 -I report.py metrics_clip224_full.json [key]
"""
import json
import sys

import numpy as np

RES = "/home/narolski/smad-next/experiments/AF0/"


def f(x, d=3):
    return "—" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def ci(c):
    return f"[{f(c['ci'][0])}, {f(c['ci'][1])}]" if c and c.get("ci") else ""


def main():
    d = json.load(open(RES + sys.argv[1]))
    key = sys.argv[2] if len(sys.argv) > 2 else "score"
    heads = list(d)
    print(f"\n#### {sys.argv[1]} ({key})\n")
    print("| head | F1 rho (face) | F1 after template | pair swap | F2 FM R2 vs R4 | FM R2w vs R4 | CV R2 vs R4 | CV R2w vs R4 | FM R3 vs R4 | CV R3 vs R4 | CV R3m vs R4 | lapvar floor (FM / CV R2w vs R4) | best simple (FM R2 vs R4) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for h in heads:
        r = d[h]
        F1 = r.get("F1") or {}
        ps = r.get("pair_swap") or {}
        P = r.get(key, {})
        fm = P.get("ladder/frgcferet/facemorpher", {})
        cv = P.get("ladder/frgcferet/opencv", {})
        g = lambda dd, k: (f(dd[k]["auc"]) + " " + ci(dd[k])) if dd.get(k) else "—"  # noqa
        lf = f"{f(fm.get('R2wvsR4', {}).get('lapvar_floor'))} / {f(cv.get('R2wvsR4', {}).get('lapvar_floor'))}"
        bs = f"{fm.get('R2vsR4', {}).get('best_simple', '—')} {f(fm.get('R2vsR4', {}).get('best_simple_auc'))}"
        print(f"| {h} | {f(F1.get('rho_face'))} {('[' + f(F1['rho_face_ci'][0]) + ', ' + f(F1['rho_face_ci'][1]) + ']') if F1.get('rho_face_ci') else ''} "
              f"| {f(F1.get('rho_after_template'))} | {f(ps.get('mean'))} {('[' + f(ps['ci'][0]) + ', ' + f(ps['ci'][1]) + ']') if ps.get('ci') else ''} "
              f"| {g(fm, 'R2vsR4')} | {g(fm, 'R2wvsR4')} | {g(cv, 'R2vsR4')} | {g(cv, 'R2wvsR4')} | {g(fm, 'R3vsR4')} | {g(cv, 'R3vsR4')} "
              f"| {g(cv, 'R3mvsR4')} | {lf} | {bs} |")
    print("\nShifts in R0 standard deviations (F3):\n")
    print("| head | FRLL native->E7 opencv | facemorpher | amsl | webmorph | MAD22 native->E7 FaceMorpher | R0->R2 FM | R0->R2w FM | R0->R2 CV | R0->R2w CV |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for h in heads:
        P = d[h].get(key, {})
        b = P.get("bench", {})
        fm = P.get("ladder/frgcferet/facemorpher", {})
        cv = P.get("ladder/frgcferet/opencv", {})
        s = lambda dd, k: (f(dd[k]["shift"], 2) + " " + (("[" + f(dd[k]["ci"][0], 2) + ", " + f(dd[k]["ci"][1], 2) + "]") if dd[k].get("ci") else "")) if dd.get(k) else "—"  # noqa
        print(f"| {h} | {s(b, 'FRLL_native_to_E7_opencv')} | {s(b, 'FRLL_native_to_E7_facemorpher')} | {s(b, 'FRLL_native_to_E7_amsl')} "
              f"| {s(b, 'FRLL_native_to_E7_webmorph')} | {s(b, 'MAD22_native_to_E7_FaceMorpher')} | {s(fm, 'shift_R0_to_R2')} "
              f"| {s(fm, 'shift_R0_to_R2w')} | {s(cv, 'shift_R0_to_R2')} | {s(cv, 'shift_R0_to_R2w')} |")
    print("\nEER % per benchmark landmark cell (F5), genuine native / E7:\n")
    cells = [f"frllm_{x}" for x in ("amsl", "facemorpher", "opencv", "webmorph")] + [f"mad22_{x}" for x in ("FaceMorpher", "OpenCV", "Webmorph")]
    print("| head | " + " | ".join(cells) + " | Poisson set AUC |")
    print("|---|" + "---|" * (len(cells) + 1))
    for h in heads:
        P = d[h].get(key, {})
        b = P.get("bench", {})
        row = []
        for c in cells:
            n, e = b.get(f"EER_{c}_native"), b.get(f"EER_{c}_e7")
            row.append(f"{f(n['eer'], 1) if n else '—'} / {f(e['eer'], 1) if e else '—'}")
        po = (P.get("poisson_h1") or {}).get("auc")
        print(f"| {h} | " + " | ".join(row) + f" | {f(po['auc']) + ' ' + ci(po) if po else '—'} |")


if __name__ == "__main__":
    main()

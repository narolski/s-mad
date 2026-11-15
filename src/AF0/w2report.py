"""Wave-2 comparison table (alpha, g, D, G targets; wave-1 scale + halves) from metrics_<bb>_w2_<T>.json, and the
registered wave-2 reading for g. Markdown to stdout, JSON to experiments/AF0/wave2_<bb>.json.
  python3 -I w2report.py clip224
"""
import json
import pathlib
import sys

RES = pathlib.Path("/home/narolski/smad-next/experiments/AF0")


def g(d, *ks):
    for k in ks:
        d = (d or {}).get(k)
    return d


def main():
    bb = sys.argv[1]
    out = {}
    rows = []
    for T in ("alpha", "g", "D", "G"):
        p = RES / f"metrics_{bb}_w2_{T}.json"
        if not p.exists():
            continue
        d = json.load(open(p))
        for h in ("ridge", "mlp_s401"):
            r = d.get(h)
            if not r:
                continue
            for key in ("score", "score_top10", "score_inner", "score_periph"):
                P = r.get(key, {})
                fm, cv = P.get("ladder/frgcferet/facemorpher", {}), P.get("ladder/frgcferet/opencv", {})
                b = P.get("bench", {})
                e7 = [g(b, f"FRLL_native_to_E7_{f}", "shift") for f in ("opencv", "facemorpher", "amsl", "webmorph")]
                e7 = [x for x in e7 if x is not None]
                row = dict(target=T, head=h, key=key, F1=g(r, "F1", "rho_face"), F1_ci=g(r, "F1", "rho_face_ci"),
                           pair_swap=g(r, "pair_swap", "mean"),
                           fm_R2w_R4=g(fm, "R2wvsR4", "auc"), fm_R2w_R4_floor=g(fm, "R2wvsR4", "lapvar_floor"),
                           cv_R2w_R4=g(cv, "R2wvsR4", "auc"), fm_R3_R4=g(fm, "R3vsR4", "auc"), cv_R3_R4=g(cv, "R3vsR4", "auc"),
                           cv_R3m_R4=g(cv, "R3mvsR4", "auc"), frll_e7_shift_max=max(e7, key=abs) if e7 else None,
                           mad22_fm_e7_shift=g(b, "MAD22_native_to_E7_FaceMorpher", "shift"),
                           r0_r2w_fm=g(fm, "shift_R0_to_R2w", "shift"), r0_r2w_cv=g(cv, "shift_R0_to_R2w", "shift"),
                           eer_amsl=g(b, "EER_frllm_amsl_native", "eer"), eer_webmorph=g(b, "EER_frllm_webmorph_native", "eer"),
                           poisson=g(P, "poisson_h1", "auc", "auc"))
                rows.append(row)
    out["rows"] = rows
    verdict = {}
    for h in ("ridge", "mlp_s401"):
        for key in ("score", "score_top10"):
            gg = next((r for r in rows if r["target"] == "g" and r["head"] == h and r["key"] == key), None)
            aa = next((r for r in rows if r["target"] == "alpha" and r["head"] == h and r["key"] == key), None)
            if not gg or not aa or gg["fm_R2w_R4"] is None:
                continue
            fails = gg["fm_R2w_R4"] < 0.75 or (gg["frll_e7_shift_max"] is not None and abs(gg["frll_e7_shift_max"]) > 0.3)
            gain = (gg["fm_R3_R4"] - aa["fm_R3_R4"] >= 0.03) or (
                gg["frll_e7_shift_max"] is not None and aa["frll_e7_shift_max"] is not None
                and abs(gg["frll_e7_shift_max"]) < abs(aa["frll_e7_shift_max"]))
            verdict[f"{h}/{key}"] = dict(g_fails=fails, g_brings_gain=gain, g_fm_R2w_R4=gg["fm_R2w_R4"],
                                        g_frll_e7_shift_max=gg["frll_e7_shift_max"], g_fm_R3_R4=gg["fm_R3_R4"],
                                        alpha_fm_R3_R4=aa["fm_R3_R4"], alpha_frll_e7_shift_max=aa["frll_e7_shift_max"])
    out["verdict_g"] = verdict
    json.dump(out, open(RES / f"wave2_{bb}.json", "w"), indent=1)
    f = lambda x: "—" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))  # noqa
    print(f"| target | head | pooling | F1 rho | pair swap | FM R2w vs R4 (floor) | CV R2w vs R4 | FM R3 vs R4 | CV R3 vs R4 | CV R3m vs R4 | FRLL E7 shift (max) | MAD22 FM E7 shift | R0->R2w FM / CV | EER AMSL / WebMorph | Poisson AUC |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['target']} | {r['head']} | {r['key'].replace('score_', '').replace('score', 'mean')} | {f(r['F1'])} | {f(r['pair_swap'])} "
              f"| {f(r['fm_R2w_R4'])} ({f(r['fm_R2w_R4_floor'])}) | {f(r['cv_R2w_R4'])} | {f(r['fm_R3_R4'])} | {f(r['cv_R3_R4'])} "
              f"| {f(r['cv_R3m_R4'])} | {f(r['frll_e7_shift_max'])} | {f(r['mad22_fm_e7_shift'])} | {f(r['r0_r2w_fm'])} / {f(r['r0_r2w_cv'])} "
              f"| {f(r['eer_amsl'])} / {f(r['eer_webmorph'])} | {f(r['poisson'])} |")
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()

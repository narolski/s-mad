"""Reader of follow-ups (b) and (c) of the morph-free networks experiment (AD4), prereg Amendment 4: the unblanked-score
gate, H-new-3 (border-blanked re-score), H-new-4 (held-out generator renders), H-new-5 (landmark-ladder same-person vs
two-person morphs). Uses summarise.py (loading, persons, bootstrap, tables) unchanged. CPU, one process.

  python fu_read.py --res DIR_WITH_ONE_FOLDER_PER_NETWORK [--out-dir experiments/AD4] [--test]
(--test: smoke output, B = 200, no verdicts written to the experiment folder unless --out-dir is given)
"""
import argparse
import csv
import io
import json
import pathlib
import tarfile

import numpy as np
from scipy.stats import kendalltau

import summarise as R

A, S = R.A, R.S
EXTRA = pathlib.Path("/mnt/t7/smad_next/AD4/fu/stage/fu/data/manifests/fu_extra.csv")


def logit(p):
    p = np.clip(np.asarray(p, np.float64), 1e-7, 1 - 1e-7)
    return np.log(p / (1 - p))


def aligned(npz, ids):
    z = np.load(npz)
    m = dict(zip(z["id"].tolist(), z["score"].astype(np.float64)))
    return np.array([m.get(i, np.nan) for i in ids]), z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    res = pathlib.Path(a.res)
    out_dir = pathlib.Path(a.out_dir) if a.out_dir else (R.EXP if not a.test else res)
    B = 200 if a.test else R.B_REAL
    rows = list(csv.DictReader(open(R.W / "ad4/data/manifests/ad4_eval.csv")))
    ids = [r["id"] for r in rows]
    extra = list(csv.DictReader(open(EXTRA)))
    eids = [r["id"] for r in extra]
    cl = S.cells(rows)
    nets_dirs = sorted(d for d in res.iterdir() if d.is_dir())
    out = {"amendment": "4 (b), (c)", "label": "post hoc follow-up", "test": a.test, "networks": [d.name for d in nets_dirs]}

    # gate: unblanked re-score against the registered scores
    gate = {}
    for d in nets_dirs:
        mine, z = aligned(d / "scores_ad4_eval.npz", ids)
        if d.name.startswith("AD4_m3zero"):
            ref = np.load("/mnt/t7/smad_next/AD4/zero_step/m3/scores_eval.npz")
        else:
            with tarfile.open(f"/mnt/t7/smad_next/AD4/results_vast/{d.name}.tar") as tf:
                ref = np.load(io.BytesIO(tf.extractfile(f"{d.name}/scores_eval.npz").read()))
        refs = dict(zip(ref["id"].tolist(), ref["score"].astype(np.float64)))
        cells, ok = {}, True
        for c, (m, b) in cl.items():
            ii = [i for i in list(m) + list(b) if np.isfinite(mine[i])]
            if len(ii) < 4 or not any(i in m for i in ii) or not any(i in b for i in ii):
                continue
            x = mine[ii]
            y = np.array([refs[ids[i]] for i in ii])
            nm = sum(i in set(m) for i in ii)
            im = [k for k, i in enumerate(ii) if i in set(m)]
            ib = [k for k, i in enumerate(ii) if i not in set(m)]
            da = abs(A.auc(x[im], x[ib]) - A.auc(y[im], y[ib]))
            tau = float(kendalltau(x, y).statistic)
            p = da <= 0.005 and tau >= 0.99
            ok &= p
            cells[c] = {"abs_auc_diff": da, "kendall_tau": tau, "n": len(ii), "pass": bool(p), "n_morph": nm}
        gate[d.name] = {"pass": bool(ok and cells),
                        "max_abs_auc_diff": max([v["abs_auc_diff"] for v in cells.values()], default=float("nan")),
                        "min_tau": min([v["kendall_tau"] for v in cells.values()], default=float("nan")),
                        "device": str(z["device"]),
                        "limit": int(z["limit"])}
    out["gate_unblanked"] = gate
    passed = [n for n, g in gate.items() if g["pass"]]
    print("gate (unblanked re-score vs registered):", {n: (g["pass"], round(g["max_abs_auc_diff"], 5),
                                                          round(g["min_tau"], 4)) for n, g in gate.items()})

    def arm(n):
        return "mf" if "m3mf" in n else "perm" if "m3perm" in n else "zero"

    def seed(n):
        return int(n.rsplit("_s", 1)[1])

    pers = sorted({p for i in cl["frllm/amsl/native"][1] for p in R.persons(rows[i])})
    D = R.Draw(pers, B, R.BOOT_SEED)
    # H-new-3: blanked cells, read with the AD4 reading code (descriptive)
    bl_rows = [dict(r, path="blank/" + r["path"]) for r in rows]
    nets = {}
    for d in nets_dirs:
        if d.name not in passed and not a.test:
            continue
        s, z = aligned(d / "scores_ad4_eval_blank.npz", ids)
        nets[d.name] = dict(arm=arm(d.name), seed=seed(d.name), score=s, train=None, meta=None, info={},
                            platform=f"Athena, {z['device']}, blanked")
    if a.test:
        keep = [i for i in range(len(rows)) if all(np.isfinite(n["score"][i]) for n in nets.values())]
        sub = [rows[i] for i in keep]
        for n in nets.values():
            n["score"] = n["score"][keep]
        rows_b = sub
    else:
        rows_b = rows
    if len({c for c in S.cells(rows_b)}) and all(np.all(np.isfinite(n["score"])) for n in nets.values()):
        res_b, cl_b = R.compute(nets, rows_b, D, a.test)
        cells = sorted(cl_b, key=R.cell_key)
        rd = R.reading(nets, res_b, cells, "m3", {}, {"mf": [n["seed"] for n in nets.values() if n["arm"] == "mf"],
                                                     "perm": [n["seed"] for n in nets.values() if n["arm"] == "perm"]})
        md = R.md_tables(rd, nets, cells, "m3", {}, [])
        md = md.replace("reading, our frames", "border-blanked re-score (H-new-3, post hoc follow-up), our frames with "
                        "everything outside the fixed face ellipse set to grey")
        mfm = rd["cells"].get("mordiff/mordiff/e7", {}).get("mf")
        e = mfm["eer_mean"] if mfm else None
        k3 = len(mfm["eer"]) if mfm else 0
        v3 = (f"incomplete ({k3} of 5)" if k3 < 5 else
              "supported" if e > 15 else "falsified" if e <= 5 else "mixed")
        out["H-new-3"] = {"mordiff_e7_mf_eer_mean": e, "per_seed": mfm["eer"] if mfm else None, "verdict": v3,
                          "status": rd["status"]}
        md = (f"**H-new-3 (post hoc follow-up): {v3}.** Blanked MorDIFF history-matched, morph-free seed mean EER "
              f"{e:.1f}% over {k3} networks that passed the unblanked-score gate (per seed {', '.join(f'{x:.1f}' for x in mfm['eer'])}); rule: above 15% supported, at most 5% "
              "falsified. Flag on the networks: not reproduced on this stack. The 'passable' and 'A1' columns apply the AD4 "
              "rule to blanked images descriptively; they are not the registered AD4 verdicts.\n\n" + md)
        (out_dir / "fu_blank_m3.md").write_text(md)
        json.dump(rd, open(out_dir / "fu_blank_m3.json", "w"), indent=1, default=float)

    # extra pools: scores per network
    ex = {}
    for d in nets_dirs:
        if d.name not in passed and not a.test:
            continue
        ex[d.name] = aligned(d / "scores_fu_extra.npz", eids)[0]
    unbl = {d.name: aligned(d / "scores_ad4_eval.npz", ids)[0] for d in nets_dirs if d.name in ex}
    ifr = cl["frllm/amsl/native"][1]
    # H-new-4
    h4 = {}
    for pool in ("smdd_eval", "h3", "h4b"):
        ii = [k for k, r in enumerate(extra) if r["set"] == pool]
        h4[pool] = {}
        for n, s in ex.items():
            si = s[ii][np.isfinite(s[ii])]
            fr = unbl[n][ifr][np.isfinite(unbl[n][ifr])]
            if len(si) and len(fr):
                h4[pool][n] = {"pool_median_logit": float(np.median(logit(si))), "frll_median_logit": float(np.median(logit(fr))),
                               "diff": float(np.median(logit(si)) - np.median(logit(fr))), "n": int(len(si))}
    mfn = sorted([n for n in ex if arm(n) == "mf"], key=seed)
    mfm_ok = [n for n in mfn if n in h4["smdd_eval"]]
    below = sum(h4["smdd_eval"][n]["diff"] < 0 for n in mfm_ok)
    out["H-new-4"] = {"pools": h4, "mf_seeds_below": below, "n_mf": len(mfn),
                      "verdict": (f"incomplete ({len(mfm_ok)} of 5)" if len(mfm_ok) < 5 else
                                  "supported" if below >= 3 else "falsified")}
    # H-new-5
    pp = sorted({p for r in extra if r["set"] == "ar1" for p in (r["p1"], r["p2"])})
    D5 = R.Draw(pp, B, [20261111, 4, 5])
    fam = {f: [k for k, r in enumerate(extra) if r["set"] == "ar1" and r["family"] == f] for f in
           {r["family"] for r in extra if r["set"] == "ar1"}}

    def contrast(s, pos, neg):
        a_ = A.auc(s[pos], s[neg])
        wp = D5.wm([(extra[k]["p1"], extra[k]["p2"]) for k in pos])
        wn = D5.wm([(extra[k]["p1"], extra[k]["p2"]) for k in neg])
        return a_, R.wauc(s[pos], s[neg], wp, wn)

    h5 = {}
    for tool in ("opencv", "facemorpher"):
        r0, r2w, r3, r4 = fam["R0_none"], fam[f"R2w_{tool}"], fam[f"R3_{tool}"], fam[f"R4_{tool}"]
        if a.test:
            r0, r2w, r3, r4 = ([k for k in x if all(np.isfinite(s[k]) for s in ex.values())] for x in (r0, r2w, r3, r4))
        h5[tool] = {}
        gaps_rep = []
        for n, s in ex.items():
            row, reps = {}, {}
            for name, (pos, neg) in {"R3_vs_R0": (r3, r0), "R4_vs_R0": (r4, r0), "R4_vs_R3": (r4, r3),
                                     "R3_vs_R2w": (r3, r2w), "R4_vs_R2w": (r4, r2w)}.items():
                if len(pos) and len(neg):
                    row[name], reps[name] = contrast(s, pos, neg)
            if "R4_vs_R0" in row and "R3_vs_R0" in row:
                row["gap"] = row["R4_vs_R0"] - row["R3_vs_R0"]
                row["gap_ci95"] = R.ci(reps["R4_vs_R0"] - reps["R3_vs_R0"])
                if arm(n) == "mf":
                    gaps_rep.append(reps["R4_vs_R0"] - reps["R3_vs_R0"])
            h5[tool][n] = row
        g = [h5[tool][n]["gap"] for n in mfn if "gap" in h5[tool].get(n, {})]
        h5[tool]["_mf_gap_mean"] = float(np.mean(g)) if g else None
        h5[tool]["_mf_gap_mean_ci95"] = R.ci(np.mean(gaps_rep, 0)) if gaps_rep else None
    gm = [h5[t]["_mf_gap_mean"] for t in ("opencv", "facemorpher")]
    v5 = (f"incomplete ({len(mfn)} of 5)" if len(mfn) < 5 else None if None in gm else
          "supported" if all(x <= 0.1 for x in gm) else "falsified" if all(x > 0.1 for x in gm) else "mixed")
    out["H-new-5"] = {"by_tool": h5, "verdict": v5}
    json.dump(out, open(out_dir / ("fu_pools_m3_test.json" if a.test else "fu_pools_m3.json"), "w"), indent=1, default=float)
    L = ["# Follow-ups (c): landmark-ladder morphs (H-new-5) and held-out generator renders (H-new-4), ViT-B/16 networks (AD4 "
         "Amendment 4), post hoc follow-up", "", "Flag on the networks: not reproduced on this stack. The ladder images are the "
         "landmark ladder's (AR1) own 512 frames, not our benchmark frames. The networks were trained only to flag "
         "shrink-and-enlarge copies of synthetic faces.", "",
         "Unblanked re-score gate: " + ", ".join(f"{n} {'pass' if g['pass'] else 'MISS'} (max |dAUC| "
                                                 f"{g['max_abs_auc_diff']:.4f}, min tau {g['min_tau']:.3f})" for n, g in gate.items()),
         "", f"## H-new-5: {v5}. Morph-free seed-mean gap AUC(R4 vs R0) − AUC(R3 vs R0): OpenCV "
             f"{R.f1(gm[0], 3)} {R.fci(h5['opencv']['_mf_gap_mean_ci95'] or [None, None], 3)}, FaceMorpher {R.f1(gm[1], 3)} "
             f"{R.fci(h5['facemorpher']['_mf_gap_mean_ci95'] or [None, None], 3)} (rule: at most 0.1 for both tools supported).", "",
         "| tool | network | R3 vs R0 | R4 vs R0 | gap | R4 vs R3 | R3 vs R2w | R4 vs R2w |", "|---|---|---|---|---|---|---|---|"]
    for tool in ("opencv", "facemorpher"):
        for n in sorted(ex, key=lambda x: (arm(x) != "mf", arm(x), seed(x))):
            v = h5[tool].get(n, {})
            L.append(f"| {tool} | `{n}` | " + " | ".join(R.f1(v.get(k), 3) for k in
                                                         ("R3_vs_R0", "R4_vs_R0", "gap", "R4_vs_R3", "R3_vs_R2w", "R4_vs_R2w"))
                     + " |")
    L += ["", f"## H-new-4: {out['H-new-4']['verdict']}. SMDD evaluation renders below the FRLL genuine median in {below} of "
              f"{len(mfn)} morph-free seeds.", "",
          "| pool | network | n | pool median logit | FRLL genuine median logit | difference |", "|---|---|---|---|---|---|"]
    for pool, d in h4.items():
        for n in sorted(d, key=lambda x: (arm(x) != "mf", arm(x), seed(x))):
            v = d[n]
            L.append(f"| {pool} | `{n}` | {v['n']} | {v['pool_median_logit']:.2f} | {v['frll_median_logit']:.2f} | "
                     f"{v['diff']:.2f} |")
    (out_dir / ("fu_pools_m3_test.md" if a.test else "fu_pools_m3.md")).write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

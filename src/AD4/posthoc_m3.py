"""Post hoc addendum (prereg Amendment 3) of the morph-free networks experiment (AD4): floor logits, own-genuine flag rates at
FRLL-5%, file-size null per cell, seed spread, label-permuted accuracies. Descriptive; zero GPU; one CPU process. Uses the
reader's loading, persons and bootstrap (summarise.py) unchanged.

  python posthoc_m3.py --results /mnt/t7/smad_next/AD4/results_vast --recipe m3
"""
import argparse
import csv
import json
import os
import pathlib

import numpy as np
from scipy.stats import spearmanr

import summarise as R

A, S = R.A, R.S


def logit(p):
    p = np.clip(np.asarray(p, np.float64), 1e-7, 1 - 1e-7)
    return np.log(p / (1 - p))


def q(x):
    return [float(np.percentile(x, 5)), float(np.median(x)), float(np.percentile(x, 95))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--recipe", choices=("m3", "m3l"), required=True)
    ap.add_argument("--out-dir", default=str(R.EXP))
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out_dir)
    man = R.W / "ad4/data/manifests/ad4_eval.csv"
    assert R.sha(man) == R.EVAL_SHA
    rows = list(csv.DictReader(open(man)))
    perm_sha = {k: v["sha256"] for k, v in json.load(open(R.W / "ad4/build_info.json"))["perms"].items()}
    results = pathlib.Path(a.results)
    nets, refused, _, _ = R.load_trained(results, a.recipe, rows, perm_sha, results.name)
    if refused:
        R.die(f"refused networks: {refused}")
    nets.update(R.load_zero(pathlib.Path(f"/mnt/t7/smad_next/AD4/zero_step/{a.recipe}"), a.recipe))
    # training-set scores (not kept by the reader)
    train = {}
    for t, n in nets.items():
        if n["arm"] == "zero":
            z = np.load(f"/mnt/t7/smad_next/AD4/zero_step/{a.recipe}/scores_train.npz")
        else:
            z = R.read_tar(results / f"{t}.tar", t)[3]
        train[t] = (z["score_noTTA"].astype(np.float64), z["label_true"].astype(int), z["label_train"].astype(int))
    nbytes = np.array([os.path.getsize(R.W / "data" / r["path"]) for r in rows], np.float64)
    cl = S.cells(rows)
    cells = sorted(cl, key=R.cell_key)
    pers = sorted({p for i in cl["frllm/amsl/native"][1] for p in R.persons(rows[i])})
    assert len(pers) == R.N_PERSONS
    D = R.Draw(pers, R.B_REAL, R.BOOT_SEED)
    ifr = np.array(cl["frllm/amsl/native"][1])
    mf = sorted([t for t, n in nets.items() if n["arm"] == "mf"], key=lambda t: nets[t]["seed"])
    perm = sorted([t for t, n in nets.items() if n["arm"] == "perm"], key=lambda t: nets[t]["seed"])
    zero = [t for t, n in nets.items() if n["arm"] == "zero"]
    out = {"amendment": 3, "recipe": a.recipe, "frames": "our frames", "bootstrap": {"B": D.B, "seed": R.BOOT_SEED}}

    # 1. floor logits
    fl = {}
    for t in mf + perm + zero:
        s, yt, ytr = train[t]
        thr = R.thresholds(nets[t]["score"], ifr)["FRLL-5%"][1]
        fl[t] = {"train_native_p5_med_p95": q(logit(s[yt == 0])), "train_copy_p5_med_p95": q(logit(s[yt == 1])),
                 "frll5_threshold_p": thr, "frll5_threshold_logit": float(logit(thr))}
    out["floor"] = fl
    ev = {}
    for c in cells:
        m, b = cl[c]
        st = c.split("/")[0]
        nat = cl[[k for k in cl if k.startswith(st + "/") and k.endswith("/native")][0]][1]
        ev[c] = {t: {"morph": float(np.median(logit(nets[t]["score"][m]))),
                     "cell_genuine": float(np.median(logit(nets[t]["score"][b]))),
                     "set_unprocessed_genuine": float(np.median(logit(nets[t]["score"][nat])))} for t in mf + zero}
    out["eval_median_logits"] = ev

    # 2. own-genuine flag rate at FRLL-5%, with the miss rate of each family
    C = D.C
    own = {}
    for st in ("mordiff", "dim", "frllm", "mad22c"):
        fams = [k for k in cells if k.startswith(st + "/") and k.endswith("/native")]
        nat = cl[fams[0]][1]
        wb = D.wb([R.persons(rows[i]) for i in nat])
        per, rep = [], []
        for t in mf:
            f = R.flagged(nets[t]["score"][nat], R.thresholds(nets[t]["score"], ifr)["FRLL-5%"]).astype(float)
            per.append(float(f.mean()))
            rep.append((wb * f).sum(1) / wb.sum(1))
        miss = {}
        for k in fams:
            mi = cl[k][0]
            miss[k] = [float((~R.flagged(nets[t]["score"][mi], R.thresholds(nets[t]["score"], ifr)["FRLL-5%"])).mean())
                       for t in mf]
        own[st] = {"flag_per_seed": per, "flag_mean": float(np.mean(per)), "flag_mean_ci95": R.ci(np.mean(rep, 0)),
                   "miss_per_seed_by_family": miss}
    out["own_genuine_frll5"] = own

    # 3. file-size null
    fs = {}
    for c in cells:
        m, b = cl[c]
        sm, sb = -nbytes[m], -nbytes[b]
        pm, pb = [R.persons(rows[i]) for i in m], [R.persons(rows[i]) for i in b]
        er, ar = np.empty(D.B), np.empty(D.B)
        for k in range(0, D.B, R.CHUNK):
            Cc = C[k:k + R.CHUNK]
            wm, wb = D.wm(pm, Cc), D.wb(pb, Cc)
            er[k:k + R.CHUNK] = 100 * A.eer_weighted(sb, sm, wb, wm)
            ar[k:k + R.CHUNK] = R.wauc(sm, sb, wm, wb)
        idx = list(m) + list(b)
        fs[c] = {"auc": A.auc(sm, sb), "auc_ci95": R.ci(ar), "eer": 100 * A.eer(sb, sm), "eer_ci95": R.ci(er),
                 "median_kb_morph": float(np.median(nbytes[m]) / 1024), "median_kb_genuine": float(np.median(nbytes[b]) / 1024),
                 "spearman_score_vs_smaller_file": [float(spearmanr(nets[t]["score"][idx], -nbytes[idx])[0]) for t in mf]}
    out["file_size_null"] = fs

    # 4. seed spread (morph-free arm)
    sp = {}
    for c in cells:
        m, b = cl[c]
        e = [100 * A.eer(nets[t]["score"][b], nets[t]["score"][m]) for t in mf]
        u = [A.auc(nets[t]["score"][m], nets[t]["score"][b]) for t in mf]
        rng = max(e) - min(e)
        kind = ("reversed" if all(x < 0.5 for x in u) else "split" if min(u) < 0.4 and max(u) > 0.6 else
                "wide" if rng > 30 else "")
        sp[c] = {"eer": e, "auc": u, "eer_range": rng, "kind": kind,
                 "eer_mean": None if kind in ("reversed", "split") else float(np.mean(e))}
    out["seed_spread"] = sp

    # 5. label-permuted accuracies
    out["permuted_training"] = {t: nets[t]["train"] for t in perm}
    json.dump(out, open(out_dir / f"posthoc_{a.recipe}.json", "w"), indent=1, default=float)

    # tables
    f1 = R.f1
    L = [f"# Morph-free networks (AD4), {R.RECIPE_NAME[a.recipe]}: post hoc addendum (Amendment 3), our frames", "",
         "Descriptive readings asked for by the independent review after the numbers were seen; no verdict changes. In our "
         "preprocessing. The networks were trained only to flag shrink-and-enlarge copies of synthetic faces (no morph, no "
         "blending). 95% intervals: the registered person bootstrap.", ""]
    if a.recipe == "m3":
        L += ["Flag: not reproduced on this stack (reproduction gate, Fast-DiM-ODE native 4.01% against 3.0; per seed 8.72, "
              "1.88, 3.96, 0.10, 5.40).", ""]
    L += ["## A. Floor logits", "", "| network | training natives: p5 / median / p95 | training copies: p5 / median / p95 | "
          "FRLL-5% threshold (p; logit) |", "|---|---|---|---|"]
    for t, v in fl.items():
        L.append(f"| `{t}` | {' / '.join(f1(x, 2) for x in v['train_native_p5_med_p95'])} | "
                 f"{' / '.join(f1(x, 2) for x in v['train_copy_p5_med_p95'])} | {v['frll5_threshold_p']:.4f}; "
                 f"{v['frll5_threshold_logit']:.2f} |")
    L += ["", "Median logits on the evaluation cells, morph-free seeds 401 to 405 (morphs; the cell's genuine photos; the set's "
          "unprocessed genuine photos):", "", "| cell | " + " | ".join(f"seed {nets[t]['seed']}" for t in mf) +
          " | untrained |", "|---" * (len(mf) + 2) + "|"]
    for c in cells:
        L.append(f"| {R.nice(c)} | " + " | ".join(
            f"{ev[c][t]['morph']:.2f}; {ev[c][t]['cell_genuine']:.2f}; {ev[c][t]['set_unprocessed_genuine']:.2f}"
            for t in mf + zero) + " |")
    L += ["", "## B. Flag rate of each set's own unprocessed genuine photos at the FRLL-5% threshold, with miss rates, %", "",
          "| set | genuine flag rate: mean [95% CI] (per seed) | family: miss rate per seed |", "|---|---|---|"]
    for st, v in own.items():
        L.append(f"| {st} | {100 * v['flag_mean']:.1f} {R.fci([100 * x for x in v['flag_mean_ci95']])} "
                 f"({', '.join(f'{100 * x:.1f}' for x in v['flag_per_seed'])}) | " + "; ".join(
                     f"{R.NICE.get(k.rsplit('/', 1)[0], k)} {', '.join(f'{100 * x:.1f}' for x in mm)}"
                     for k, mm in v["miss_per_seed_by_family"].items()) + " |")
    L += ["", "## C. File-size null per cell (score = smaller PNG file is more morph)", "",
          "| cell | AUC [95% CI] | EER % [95% CI] | median KB morph / genuine | Spearman(network score, smaller file) per "
          "seed |", "|---|---|---|---|---|"]
    for c in cells:
        v = fs[c]
        L.append(f"| {R.nice(c)} | {v['auc']:.3f} {R.fci(v['auc_ci95'], 3)} | {v['eer']:.1f} {R.fci(v['eer_ci95'])} | "
                 f"{v['median_kb_morph']:.0f} / {v['median_kb_genuine']:.0f} | "
                 f"{', '.join(f'{x:.2f}' for x in v['spearman_score_vs_smaller_file'])} |")
    L += ["", "## D. Seed spread of the morph-free networks (no seed mean for reversed or split cells)", "",
          "| cell | EER % per seed | AUC per seed | EER range | kind | EER mean |", "|---|---|---|---|---|---|"]
    for c in cells:
        v = sp[c]
        L.append(f"| {R.nice(c)} | {', '.join(f1(x) for x in v['eer'])} | {', '.join(f'{x:.3f}' for x in v['auc'])} | "
                 f"{v['eer_range']:.1f} | {v['kind'] or '-'} | {'not printed' if v['eer_mean'] is None else f1(v['eer_mean'])} |")
    L += ["", "## E. Label-permuted networks, training set (threshold 0.5, no TTA)", "",
          "| network | own labels: accuracy / AUC | true labels: accuracy / AUC |", "|---|---|---|"]
    for t, v in out["permuted_training"].items():
        L.append(f"| `{t}` | {v['acc_vs_training_labels']:.3f} / {v['auc_vs_training_labels']:.3f} | "
                 f"{v['acc_vs_true_labels']:.3f} / {v['auc_vs_true_labels']:.3f} |")
    (out_dir / f"posthoc_{a.recipe}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

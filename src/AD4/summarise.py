"""Reader of the morph-free networks experiment (AD4), per pre-registration + Amendment 1.

For each verified result tar (sha256 file matches) of the recipe: refuses the network unless meta.json steps == 6250,
the scoring limit is 0, every eval score is finite, the eval manifest sha256 is the registered one and the training
manifest sha256 is the registered one for its arm. Recomputes per cell EER (analyze.eer) and signed AUC (analyze.auc)
from scores_eval.npz. Writes experiments/AD4/ad4_cells_<recipe>.csv and ad4_train_<recipe>.csv, prints per-network
tables, the sample-order gate (gates.py prediction vs recorded composition) and, for M3, the reproduction gate.
With --reading: the fixed AD4 reading (11_AUDIT_PLAN.md + Amendment 1); "provisional" unless all six references.

  python summarise.py --results /mnt/t7/smad_next/AD4/results_vast --recipe m3 [--reading] [--order]
"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
W = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401")
sys.path.insert(0, str(W / "ad4/code/smadcvpr"))
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402
import ad4_score as S  # noqa: E402

EXP = pathlib.Path("/home/narolski/smad-next/experiments/AD4")
SEEDS = (401, 402, 403, 404, 405)
EVAL_SHA = "5d3950ab5ccdeed4d376a15126cff660da2a35041579b3513eb7a1059baaa061"
I3_SHA = "0273c11bd0fe4b70fc9c5490859bc185ea50b9ed971a783993b843a399e7b880"
PRIMARY = ["mordiff/mordiff/native"]
SECONDARY = [f"dim/{f}/native" for f in ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")]
LANDMARK = [f"frllm/{f}/native" for f in ("amsl", "facemorpher", "opencv", "webmorph")] + \
    [f"mad22c/{f}/native" for f in ("FaceMorpher", "OpenCV", "Webmorph")]
E7_NA = {"frllm/stylegan/e7", "mad22c/MIPGAN_I/e7", "mad22c/MIPGAN_II/e7"}
E7_PARTIAL = {"mad22c/OpenCV/e7": 108, "mad22c/Webmorph/e7": 104}
REPRO = {**{c: (None, 3.0) for c in PRIMARY + SECONDARY},
         "frllm/facemorpher/native": (None, 5.6), "frllm/webmorph/native": (None, 5.6),
         "frllm/amsl/native": (None, 5.6), "frllm/opencv/native": (8.8, 26.0)}
ARCH = {"m3": "a12_clip_vitb16_madation", "m3l": "a12_clip_vitl14_madation"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cell_label(c):
    if c in E7_NA:
        return "E7 not applicable"
    if c in E7_PARTIAL:
        return f"E7 partial ({E7_PARTIAL[c]}/204 identical)"
    return ""


def metrics_from_scores(score, rows):
    out = {}
    for name, (m, b) in S.cells(rows).items():
        sm, sb = score[m], score[b]
        out[name] = {"n_morph": len(m), "n_bona": len(b), "eer": 100 * A.eer(sb, sm), "auc": A.auc(sm, sb)}
    return out


def load(results, recipe, rows, perm_sha):
    nets, refused = {}, {}
    for arm in ("mf", "perm"):
        for s in SEEDS:
            t = f"AD4_{recipe}{arm}_s{s}"
            tar, sf = results / f"{t}.tar", results / f"{t}.tar.sha256"
            if not (tar.is_file() and sf.is_file()):
                continue
            if sf.read_text().split()[0] != sha(tar):
                refused[t] = "result tar sha256 mismatch"
                continue
            with tarfile.open(tar) as tf:
                g = lambda n: tf.extractfile(f"{t}/{n}").read()  # noqa: E731
                m = json.loads(g("metrics.json"))
                meta = json.loads(g("meta.json"))
                ev = np.load(io.BytesIO(g("scores_eval.npz")))
                tr = np.load(io.BytesIO(g("scores_train.npz")))
            why = []
            if meta.get("steps") != 6250:
                why.append(f"steps {meta.get('steps')}")
            if m["info"].get("limit") != 0:
                why.append(f"limit {m['info'].get('limit')}")
            if str(ev["manifest_sha256"]) != EVAL_SHA:
                why.append("eval manifest sha256")
            want = I3_SHA if arm == "mf" else perm_sha[str(s)]
            if str(tr["manifest_sha256"]) != want:
                why.append("training manifest sha256")
            sc = ev["score"].astype(np.float64)
            if not np.all(np.isfinite(sc)):
                why.append("non-finite score")
            if list(ev["id"]) != [r["id"] for r in rows]:
                why.append("eval ids differ from ad4_eval.csv")
            if why:
                refused[t] = "; ".join(why)
                continue
            nets[t] = dict(arm=arm, seed=s, cells=metrics_from_scores(sc, rows), train=m["train"], meta=meta,
                           info=m["info"])
    zs = EXP / "zero_step" / f"metrics_{recipe}.json"
    zn = pathlib.Path(f"/mnt/t7/smad_next/AD4/zero_step/{recipe}/scores_eval.npz")
    if zs.is_file() and zn.is_file():
        z = np.load(zn)
        if str(z["manifest_sha256"]) == EVAL_SHA and np.all(np.isfinite(z["score"])):
            m = json.load(open(zs))
            nets[f"AD4_{recipe}zero_s401"] = dict(arm="zero", seed=401,
                                                  cells=metrics_from_scores(z["score"].astype(np.float64), rows),
                                                  train=m["train"], meta=None, info=m["info"])
    return nets, refused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--recipe", choices=("m3", "m3l"), required=True)
    ap.add_argument("--reading", action="store_true")
    ap.add_argument("--order", action="store_true", help="run the sample-order gate (CPU, about 1 min per network)")
    a = ap.parse_args()
    man = W / "ad4/data/manifests/ad4_eval.csv"
    assert sha(man) == EVAL_SHA
    rows = list(csv.DictReader(open(man)))
    perm_sha = {k: v["sha256"] for k, v in json.load(open(W / "ad4/build_info.json"))["perms"].items()}
    nets, refused = load(pathlib.Path(a.results), a.recipe, rows, perm_sha)
    cells = sorted({c for n in nets.values() for c in n["cells"]})
    with open(EXP / f"ad4_cells_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "cell", "n_morph", "n_bona", "eer_pct", "auc_signed", "note"])
        for t, n in sorted(nets.items()):
            for c in cells:
                v = n["cells"][c]
                w.writerow([t, n["arm"], n["seed"], c, v["n_morph"], v["n_bona"], round(v["eer"], 2),
                            round(v["auc"], 4), cell_label(c)])
    with open(EXP / f"ad4_train_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "n", "acc_training_labels", "acc_true_labels", "auc_training_labels",
                    "auc_true_labels", "frac_permuted", "train_hours"])
        for t, n in sorted(nets.items()):
            tr = n["train"]
            w.writerow([t, n["arm"], n["seed"], tr["n"], round(tr["acc_vs_training_labels"], 4),
                        round(tr["acc_vs_true_labels"], 4), round(tr["auc_vs_training_labels"], 4),
                        round(tr["auc_vs_true_labels"], 4), round(tr["frac_labels_permuted"], 4),
                        n["info"].get("train_hours")])
    if refused:
        print("REFUSED:", json.dumps(refused))
    for kind in ("native", "e7"):
        cs = [c for c in cells if c.endswith("/" + kind)]
        print(f"\n{kind} cells, EER % / signed AUC" + (" (E7 n/a: StyleGAN, MIPGAN-I, MIPGAN-II; partial: MAD22 "
                                                        "OpenCV, Webmorph)" if kind == "e7" else ""))
        print("| network | " + " | ".join(c.rsplit("/", 1)[0] for c in cs) + " |")
        print("|---" * (len(cs) + 1) + "|")
        for t, n in sorted(nets.items()):
            print(f"| {t} | " + " | ".join(f"{n['cells'][c]['eer']:.1f} / {n['cells'][c]['auc']:.2f}" for c in cs)
                  + " |")
    print("\ntraining: | network | acc own labels | acc true labels | AUC own labels | train h |")
    for t, n in sorted(nets.items()):
        tr = n["train"]
        print(f"| {t} | {tr['acc_vs_training_labels']:.3f} | {tr['acc_vs_true_labels']:.3f} | "
              f"{tr['auc_vs_training_labels']:.3f} | {n['info'].get('train_hours')} |")
    gates = {}
    if a.order:
        for t, n in sorted(nets.items()):
            if n["meta"] is None:
                continue
            mf = pathlib.Path(f"/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/"
                              f"scratchpad/ad4_meta_{t}.json")
            mf.write_text(json.dumps(n["meta"]))
            man_t = "train_i3.csv" if n["arm"] == "mf" else f"train_perm_s{n['seed']}.csv"
            p = subprocess.run([sys.executable, str(HERE / "gates.py"), "order", "--arch", ARCH[a.recipe], "--seed",
                                str(n["seed"]), "--manifest", man_t, "--meta", str(mf)], capture_output=True,
                               text=True, env={"CUDA_VISIBLE_DEVICES": "", "PATH": "/usr/bin:/bin"})
            r = json.loads(p.stdout.strip().splitlines()[-1])
            gates[t] = {"order_gate_pass": r["gate_pass"], "equal_rows": r["equal_rows"]}
            print(f"order gate {t}: {'pass' if r['gate_pass'] else 'MISS'} ({r['equal_rows']}/200)")
    mf = sorted([n for n in nets.values() if n["arm"] == "mf"], key=lambda x: x["seed"])
    if a.recipe == "m3" and mf:
        print(f"\nreproduction gate (morph-free seed means, n = {len(mf)}):")
        rep = {}
        for c, (lo, hi) in REPRO.items():
            mean = float(np.mean([n["cells"][c]["eer"] for n in mf]))
            ok = (lo is None or mean >= lo) and mean <= hi
            rep[c] = {"mean_eer": round(mean, 2), "bound": [lo, hi], "pass": ok}
            print(f"  {c}: {mean:.2f} (bound {lo}-{hi}) {'pass' if ok else 'MISS'}")
        gates["reproduction"] = rep
    json.dump(gates, open(EXP / f"ad4_gates_{a.recipe}.json", "w"), indent=1)
    if not a.reading:
        return
    perm = [n for n in nets.values() if n["arm"] == "perm"]
    zero = [n for n in nets.values() if n["arm"] == "zero"]
    if len(mf) != 5:
        raise SystemExit(f"reading refused: {len(mf)} morph-free networks (5 needed)")
    ref = perm + zero
    status = "final" if len(perm) == 5 and len(zero) == 1 else f"provisional ({len(ref)} of 6 references)"
    out = {"status": status, "cells": {}}
    print(f"\nAD4 reading ({status}); EER % (seeds 401-405)")
    print("| cell | role | morph-free mean (seeds) | references: lowest / range | folded ref AUC max | "
          "passable without morphs | seeds meeting margin | seeds > 15% | A1 | note |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        e = [n["cells"][c]["eer"] for n in mf]
        re = [n["cells"][c]["eer"] for n in ref]
        lo, hi = min(re), max(re)
        fold = max(abs(n["cells"][c]["auc"] - 0.5) + 0.5 for n in ref)
        mean = float(np.mean(e))
        passable = mean <= lo - 10
        k_margin = sum(x <= lo - 10 for x in e)
        k15 = sum(x > 15 for x in e)
        role = "primary" if c in PRIMARY else "secondary" if c in SECONDARY else "descriptive"
        a1 = ("falsified" if k15 >= 3 else "not falsified") if role != "descriptive" else "-"
        verdict = ("yes" if passable else "no") if status == "final" else ("yes (provisional)" if passable
                                                                           else "no (provisional)")
        named = passable and k15 >= 3
        note = "; ".join(x for x in (cell_label(c), "below every reference but above 15% in >=3 seeds" if named
                                     else "", "landmark: 'at least 10 points below every label-free reference', "
                                     "not 'above chance'" if c in LANDMARK else "") if x)
        out["cells"][c] = dict(role=role, mf_eer=e, mf_mean=mean, ref_lowest=lo, ref_range=[lo, hi],
                               folded_ref_auc_max=fold, passable=passable, verdict=verdict, seeds_margin=k_margin,
                               seeds_above_15=k15, a1=a1, named_case=named, note=note)
        print(f"| {c} | {role} | {mean:.1f} ({', '.join(f'{x:.1f}' for x in e)}) | {lo:.1f} / {lo:.1f}-{hi:.1f} | "
              f"{fold:.2f} | {verdict} | {k_margin}/5 | {k15}/5 | {a1} | {note} |")
    json.dump(out, open(EXP / f"ad4_reading_{a.recipe}.json", "w"), indent=1)


if __name__ == "__main__":
    main()

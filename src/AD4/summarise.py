"""Collects the verified AD4 result tars (results_vast/ and, later, WCSS copy-backs) and the zero-step metrics into
experiments/AD4/ad4_cells.csv (one row per network x cell) and ad4_train.csv (training accuracy), and prints a
markdown table of the native cells (EER % / signed AUC) per network. With --reading it applies the fixed AD4 reading
(11_AUDIT_PLAN.md "AD4 reading") per recipe and cell; it refuses unless all five morph-free and all five permuted
networks of that recipe and the zero-step network are present.

  python3 summarise.py --results /mnt/t7/smad_next/AD4/results_vast --recipe m3 [--reading]
"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import tarfile

EXP = pathlib.Path("/home/narolski/smad-next/experiments/AD4")
SEEDS = (401, 402, 403, 404, 405)
PRIMARY = ["mordiff/mordiff/native"]
SECONDARY = [f"dim/{f}/native" for f in ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(results, recipe):
    nets = {}
    for arm in ("mf", "perm"):
        for s in SEEDS:
            t = f"AD4_{recipe}{arm}_s{s}"
            tar, sf = results / f"{t}.tar", results / f"{t}.tar.sha256"
            if not (tar.is_file() and sf.is_file()):
                continue
            if sf.read_text().split()[0] != sha(tar):
                raise SystemExit(f"{tar}: sha256 mismatch")
            with tarfile.open(tar) as tf:
                m = json.load(tf.extractfile(f"{t}/metrics.json"))
                info = tf.extractfile(f"{t}/task_info.txt").read().decode()
            if "steps 6250 limit 0" not in info:
                raise SystemExit(f"{t}: not a full run ({info.strip()})")
            nets[t] = dict(arm=arm, seed=s, m=m)
    zs = EXP / "zero_step" / f"metrics_{recipe}.json"
    if zs.is_file():
        nets[f"AD4_{recipe}zero_s401"] = dict(arm="zero", seed=401, m=json.load(open(zs)))
    return nets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--recipe", choices=("m3", "m3l"), required=True)
    ap.add_argument("--reading", action="store_true")
    a = ap.parse_args()
    nets = load(pathlib.Path(a.results), a.recipe)
    cells = sorted({c for n in nets.values() for c in n["m"]["cells"]})
    with open(EXP / f"ad4_cells_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "cell", "n_morph", "n_bona", "eer_pct", "auc_signed"])
        for t, n in sorted(nets.items()):
            for c in cells:
                v = n["m"]["cells"][c]
                w.writerow([t, n["arm"], n["seed"], c, v["n_morph"], v["n_bona"],
                            round(100 * v["eer"], 2), round(v["auc"], 4)])
    with open(EXP / f"ad4_train_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "n", "acc_training_labels", "acc_true_labels", "auc_training_labels",
                    "auc_true_labels", "frac_permuted", "train_hours"])
        for t, n in sorted(nets.items()):
            tr = n["m"]["train"]
            w.writerow([t, n["arm"], n["seed"], tr["n"], round(tr["acc_vs_training_labels"], 4),
                        round(tr["acc_vs_true_labels"], 4), round(tr["auc_vs_training_labels"], 4),
                        round(tr["auc_vs_true_labels"], 4), round(tr["frac_labels_permuted"], 4),
                        n["m"]["info"].get("train_hours")])
    native = [c for c in cells if c.endswith("/native")]
    print("| network | " + " | ".join(c.replace("/native", "") for c in native) + " | train acc (own labels) |")
    print("|---" * (len(native) + 2) + "|")
    for t, n in sorted(nets.items()):
        row = [f"{100 * n['m']['cells'][c]['eer']:.1f} / {n['m']['cells'][c]['auc']:.2f}" for c in native]
        print(f"| {t} | " + " | ".join(row) + f" | {n['m']['train']['acc_vs_training_labels']:.3f} |")
    if not a.reading:
        return
    mf = [n for n in nets.values() if n["arm"] == "mf"]
    ref = [n for n in nets.values() if n["arm"] in ("perm", "zero")]
    if len(mf) != 5 or len([n for n in ref if n["arm"] == "perm"]) != 5 or not any(n["arm"] == "zero" for n in ref):
        raise SystemExit("reading refused: need 5 morph-free, 5 permuted and the zero-step network")
    out = {}
    print("\n| cell | role | morph-free EER mean (seeds) | lowest reference EER | passable without morphs | "
          "seeds meeting margin | seeds > 15% | A1 |")
    print("|---|---|---|---|---|---|---|---|")
    for c in cells:
        e = [100 * n["m"]["cells"][c]["eer"] for n in sorted(mf, key=lambda x: x["seed"])]
        lo = min(100 * n["m"]["cells"][c]["eer"] for n in ref)
        mean = sum(e) / 5
        passable = mean <= lo - 10
        k_margin = sum(x <= lo - 10 for x in e)
        k15 = sum(x > 15 for x in e)
        role = "primary" if c in PRIMARY else "secondary" if c in SECONDARY else "descriptive"
        a1 = ("falsified" if k15 >= 3 else "not falsified") if role != "descriptive" else "-"
        out[c] = dict(role=role, mf_eer=e, mf_mean=mean, ref_lowest=lo, passable=passable, seeds_margin=k_margin,
                      seeds_above_15=k15, a1=a1)
        print(f"| {c} | {role} | {mean:.1f} ({', '.join(f'{x:.1f}' for x in e)}) | {lo:.1f} | "
              f"{'yes' if passable else 'no'} | {k_margin}/5 | {k15}/5 | {a1} |")
    json.dump(out, open(EXP / f"ad4_reading_{a.recipe}.json", "w"), indent=1)


if __name__ == "__main__":
    main()

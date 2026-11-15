"""Cross-platform repeat of the morph-free networks experiment (AD4), prereg Amendments 1c and 5: per network (same task,
same seed) and cell, the difference in EER (points) and signed AUC between two result sets, read from the reader's
ad4_cells_<recipe>*.csv files. Descriptive; never replaces or is averaged with the registered numbers.

  python xplat.py --a CELLS_A.csv --a-name WCSS --b CELLS_B.csv --b-name rented --out OUT.md
"""
import argparse
import csv
import json

import numpy as np

import summarise as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--a-name", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--b-name", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ra = {(r["network"], r["cell"]): r for r in csv.DictReader(open(a.a))}
    rb = {(r["network"], r["cell"]): r for r in csv.DictReader(open(a.b))}
    keys = sorted(set(ra) & set(rb), key=lambda k: (k[0], R.cell_key(k[1])))
    keys = [k for k in keys if ra[k]["arm"] in ("mf", "perm")]
    nets = sorted({k[0] for k in keys})
    cells = sorted({k[1] for k in keys}, key=R.cell_key)
    de = {k: float(ra[k]["eer_pct"]) - float(rb[k]["eer_pct"]) for k in keys}
    da = {k: float(ra[k]["auc_signed"]) - float(rb[k]["auc_signed"]) for k in keys}
    out = {"a": a.a_name, "b": a.b_name, "n_pairs": len(keys), "networks": nets,
           "max_abs_eer_diff": max(abs(v) for v in de.values()), "max_abs_auc_diff": max(abs(v) for v in da.values()),
           "median_abs_eer_diff": float(np.median([abs(v) for v in de.values()])),
           "per_network": {n: {"max_abs_eer_diff": max(abs(de[k]) for k in keys if k[0] == n),
                               "max_abs_auc_diff": max(abs(da[k]) for k in keys if k[0] == n)} for n in nets}}
    L = [f"# Cross-platform repeat ({a.a_name} minus {a.b_name}), our frames", "",
         f"{len(keys)} network-cell pairs; largest |EER difference| {out['max_abs_eer_diff']:.2f} points, median "
         f"{out['median_abs_eer_diff']:.2f}; largest |AUC difference| {out['max_abs_auc_diff']:.4f}. Descriptive.", "",
         "| cell | " + " | ".join(f"`{n}` dEER / dAUC" for n in nets) + " |", "|---" * (len(nets) + 1) + "|"]
    for c in cells:
        L.append(f"| {R.nice(c)} | " + " | ".join(
            f"{de[(n, c)]:+.1f} / {da[(n, c)]:+.3f}" if (n, c) in de else "-" for n in nets) + " |")
    open(a.out, "w").write("\n".join(L) + "\n")
    json.dump(out, open(a.out.replace(".md", ".json"), "w"), indent=1)
    print(L[2])


if __name__ == "__main__":
    main()

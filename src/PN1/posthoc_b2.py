"""PN1 post hoc tables requested by the batch-2 review (REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md, F2 and F4).
POST HOC, descriptive, no GPU, no new score; recomputed here from the tars (not copied from the review).
  FFHQ paired history table (8 networks with HN2 scores): the same 2,000 FFHQ persons, history-matched
    (landmark_complete resmatch) vs native (ffhq_bona orig), paired by key: AUC (resmatch vs native), share whose logit
    rises, mean and median shift, own-rule flag change; 95% intervals from 2,000 person bootstraps (rng 20261116).
  H1 paired table (12 networks): share of Poisson morphs scored above their own host's genuine photo (same 112 px
    history), own-rule genuine flags and morph misses; 95% intervals from 2,000 host bootstraps (rng 20261116).
  python3 -I posthoc_b2.py -> experiments/PN1_.../tier1/posthoc_b2.json"""
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402

U = K.PN1 / "results_rented" / "unpacked"
HN2 = K.PN1 / "hn2_tree" / "pn1h" / "data" / "manifests" / "pn1_hn2.csv"
H1M = pathlib.Path("/mnt/t7/smad_heldout/h1_poisson/data/manifests/h1poisson.csv")


def load(p):
    z = np.load(p)
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def ci(f, n, rng, B=2000):
    v = [f(rng.integers(0, n, n)) for _ in range(B)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    rng = np.random.default_rng(20261116)
    out = {"post_hoc": True}
    rows = list(csv.DictReader(open(HN2)))
    nat = {r["host"]: r["id"] for r in rows if r["rung"] == "ffhq_bona_orig"}
    rm = {r["host"]: r["id"] for r in rows if r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(nat) & set(rm))
    ff = {}
    for seed in (401, 402):
        for arm in ("A", "B", "Bn", "C"):
            s = load(U / f"PN1_HN2_s{seed}" / f"scores_hn2_{arm}.npz")
            a = np.array([s[nat[k]] for k in keys])
            b = np.array([s[rm[k]] for k in keys])
            d = b - a
            ff[f"{arm}_s{seed}"] = dict(
                n=len(keys), auc_resmatch_vs_native=float(K.auc(b, a)), auc_ci=ci(lambda i: K.auc(b[i], a[i]), len(keys), rng),
                share_rising=float(np.mean(d > 0)), share_ci=ci(lambda i: np.mean(d[i] > 0), len(keys), rng),
                mean_shift=float(d.mean()), mean_ci=ci(lambda i: d[i].mean(), len(keys), rng), median_shift=float(np.median(d)),
                flag_own_native=float(np.mean(a > 0)), flag_own_resmatch=float(np.mean(b > 0)))
    out["ffhq_paired_history"] = ff
    h1 = {"h1_" + r["id"]: r for r in csv.DictReader(open(H1M)) if r["variant"] == "orig"}
    mor = sorted(i for i, r in h1.items() if r["family"] == "h1_poisson")
    bon = {r["host"]: i for i, r in h1.items() if r["family"] == "h1_bona"}
    mor = [i for i in mor if h1[i]["host"] in bon]
    hh = {}
    for seed in (401, 402):
        for arm in ("A", "B", "Bn", "C", "Sb", "Bv"):
            s = load(U / f"PN1_{arm}_s{seed}" / "scores_eval.npz")
            m = np.array([s[i] for i in mor])
            g = np.array([s[bon[h1[i]["host"]]] for i in mor])
            hh[f"{arm}_s{seed}"] = dict(
                n_pairs=len(mor), share_morph_above_own_host=float(np.mean(m > g)), share_ci=ci(lambda i: np.mean(m[i] > g[i]), len(mor), rng),
                auc=float(K.auc(m, g)), auc_ci=ci(lambda i: K.auc(m[i], g[i]), len(mor), rng),
                genuine_flag_own=float(np.mean(g > 0)), morph_miss_own=float(np.mean(m <= 0)))
    out["h1_paired"] = hh
    K.dump(out, K.RES / "tier1" / "posthoc_b2.json")
    for k, v in ff.items():
        print("FFHQ", k, round(v["auc_resmatch_vs_native"], 3), [round(x, 3) for x in v["auc_ci"]], round(v["share_rising"], 3),
              [round(x, 3) for x in v["share_ci"]], round(v["mean_shift"], 2), [round(x, 2) for x in v["mean_ci"]],
              round(v["median_shift"], 3), round(v["flag_own_native"], 3), round(v["flag_own_resmatch"], 3))
    for k, v in hh.items():
        print("H1", k, round(v["share_morph_above_own_host"], 3), [round(x, 3) for x in v["share_ci"]], round(v["auc"], 3),
              round(v["genuine_flag_own"], 3), round(v["morph_miss_own"], 3))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

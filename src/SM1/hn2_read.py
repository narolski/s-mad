"""SM1 A18 reader (H-n2): the m3 recipe trained on DG1 shards 0-5 (arm RS: X20 vs REC20 + SAME20), read on shards 6-7.

Input: OUT/results_rented/hn2/HN2_RS_s{401,402,403}.tar (sha256 checked, extracted) — or the WCSS copies placed there:
<T>/hn2test/scores_eval.npz (logit of the no-TTA score on the test rows), <T>/hn2test/metrics.json (training-row AUC).
Primary (registered): ΔAUC of (floor inputs + network logit) over the floor F, cross-fit on test partner-cycle folds,
partner-cycle bootstrap (hn2_incr.py); decision on the mean of seeds 401 and 402: falsified if ΔAUC ≥ 0.05 with lower
bound > 0, supported if upper bound < 0.03, otherwise undecided; "undecided (incomplete)" unless both seeds exist and
are finite. Reported with and without flagged rows, and over the image-statistics floor F_img. Seed 403 is reported
and enters a 3-seed mean as a stability check. Secondary: raw, Laplacian- and θ-stratified X20 over SAME20, X20 / SAME20
over REC20 (partner-cycle bootstrap); training-row AUC per fit.

  python3 -I hn2_read.py -> RES/hn2_read.json
"""
import csv
import hashlib
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import hn2_incr as I  # noqa: E402

D = K.OUT / "results_rented/hn2"


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    test = list(csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv")))
    items = {f"hn2:{r['key']}:{r['host']}": r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv"))
             if r["key"] in ("X20", "SAME20", "REC20")}
    fits, train_auc, scores = {}, {}, {}
    for f in sorted(D.glob("HN2_RS_s40?.tar")):
        assert hashlib.sha256(open(f, "rb").read()).hexdigest() == open(str(f) + ".sha256").read().split()[0], f
        T = f.stem
        if not (D / T).exists():
            with tarfile.open(f) as t:
                t.extractall(D)
        z = np.load(D / T / "hn2test/scores_eval.npz")
        if not np.isfinite(z["score_noTTA"]).all():
            fits[T] = "non-finite"
            continue
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        scores[T] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        m = json.load(open(D / T / "hn2test/metrics.json"))
        train_auc[T] = m["train"]["auc_vs_training_labels"]
        fits[T] = "ok"
    out = dict(fits=fits, train_row_auc=train_auc)
    need = ("HN2_RS_s401", "HN2_RS_s402")
    complete = all(fits.get(t) == "ok" for t in need)
    for tag, drop in (("all", False), ("unflagged", True)):
        rows = I.test_rows(drop_flagged=drop)
        per = {T: I.incremental(rows, sc) for T, sc in scores.items()}
        o = {}
        if complete:
            o["decision_2seed"] = I.summarise([per[t] for t in need])
            o["decision_2seed"]["verdict"] = I.verdict(o["decision_2seed"]["dAUC_over_F"])
        else:
            o["decision_2seed"] = dict(verdict="undecided (incomplete)")
        if len(per) >= 3:
            o["all_seeds"] = I.summarise(list(per.values()))
        out[tag] = o
    cyc_of = {r["id"]: items[r["id"]]["cycle"] for r in test}
    cyc = sorted(set(cyc_of.values()), key=int)
    cp = {c: i for i, c in enumerate(cyc)}
    C = np.random.default_rng(K.SEED).multinomial(len(cyc), np.full(len(cyc), 1 / len(cyc)), size=I.B).astype(float)
    W = lambda ids: C[:, [cp[cyc_of[i]] for i in ids]]  # noqa: E731
    fam = {}
    for r in test:
        fam.setdefault(r["family"], []).append(r["id"])
    X, SA, REC = fam["X20"], fam["SAME20"], fam["REC20"]
    rows = {r["id"]: r for r in I.test_rows()}
    strata = {}
    for j, nm in ((1, "lap"), (0, "theta")):
        v = np.array([rows[i]["f"][j] for i in X + SA])
        q = np.quantile(v, [0.2, 0.4, 0.6, 0.8])
        strata[nm] = {i: int(np.searchsorted(q, rows[i]["f"][j])) for i in X + SA}
    sec = {}
    for T, sc in scores.items():
        g = lambda ids: np.array([sc[i] for i in ids])  # noqa: E731
        wa = lambda a, b: (float(S.wauc(g(a), g(b), np.ones((1, len(a))), np.ones((1, len(b))))[0]),  # noqa: E731
                           S.wauc(g(a), g(b), W(a), W(b)))
        m = {"X20_over_SAME20": wa(X, SA), "X20_over_REC20": wa(X, REC), "SAME20_over_REC20": wa(SA, REC)}
        for nm, sm in strata.items():
            pt, dr, wt = 0.0, 0.0, 0.0
            for k in range(5):
                xs, ss = [i for i in X if sm[i] == k], [i for i in SA if sm[i] == k]
                if xs and ss:
                    a, b = wa(xs, ss)
                    w = len(xs) * len(ss)
                    pt, dr, wt = pt + w * a, dr + w * b, wt + w
            m[f"X20_over_SAME20_{nm}strat"] = (pt / wt, dr / wt)
        sec[T] = {k: dict(auc=round(v[0], 4), ci=[round(x, 4) for x in S.ci(v[1])]) for k, v in m.items()}
    out["secondary"] = sec
    json.dump(out, open(K.RES / "hn2_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

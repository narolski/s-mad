"""SM1 H-n2 reader (DRAFT A18): the m3 recipe trained on DG1 shards 0-5, read on the held-out shards 6-7.

Input: OUT/results_rented/hn2/HN2_{R,RS}_s{401,402}.tar (sha256 checked, extracted): <T>/hn2test/scores_eval.npz
(logit of the no-TTA score). Test: 133 X20, 134 SAME20, 134 REC20 of 134 hosts never seen in training.
Host bootstrap B = 10,000 (seed 20261111); 2-seed means per arm.
Reads per arm: X20 over SAME20 raw, Laplacian-stratified (face-box Laplacian quintiles over the test X20 + SAME20),
θ-stratified (θ quintiles, DG1 theta_xT); X20 over REC20; SAME20 over REC20. Floors: oriented AUC (max(A, 1 − A))
of each simple statistic for X20 vs SAME20 on the same test rows: face-box Laplacian, PNG bytes, asymmetry, input
disagreement d, θ.
Decision (registered on arm RS, Laplacian-stratified X20 over SAME20, 2-seed mean): supported (no learnable second
identity) if ≤ 0.65; falsified (a signal exists) if ≥ 0.75 with the lower bound > 0.65; otherwise undecided.

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

D = K.OUT / "results_rented/hn2"
B = 10000


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    test = list(csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv")))
    fam = {}
    for r in test:
        fam.setdefault(r["family"], []).append(r["id"])
    host = {r["id"]: r["src_id"] for r in test}
    hosts = sorted(set(host.values()))
    hp = {h: i for i, h in enumerate(hosts)}
    C = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=B).astype(float)
    W = lambda ids: C[:, [hp[host[i]] for i in ids]]  # noqa: E731
    it = {f"hn2:{r['key']}:{r['host']}": r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv"))
          if r["key"] in ("X20", "SAME20")}
    th = {}
    for k in range(8):
        f = K.OUT.parent / "DG1/gen" / f"addon_s{k}" / f"out_addon_s{k}" / f"addon_s{k}" / "gen_rows.csv"
        for r in csv.DictReader(open(f)):
            th[(f"addon_s{k}", r["pool"], r["name"])] = float(r["theta_xT"]) if r["theta_xT"] not in ("", "nan") else np.nan
    X, SA, REC = fam["X20"], fam["SAME20"], fam["REC20"]
    stat = {}
    for i in X + SA:
        r = it[i]
        parts = r["id"].split("/")
        stat[i] = dict(lap=float(r["lapvar_box"]), png=float(r["png_bytes"]), asym=float(r["asym_box"]), d=float(r["d"]),
                       theta=th[(r["list"], parts[-2], parts[-1])])
    strata = {}
    for nm in ("lap", "theta"):
        v = np.array([stat[i][nm] for i in X + SA])
        q = np.quantile(v, [0.2, 0.4, 0.6, 0.8])
        strata[nm] = {i: int(np.searchsorted(q, stat[i][nm])) for i in X + SA}

    def wauc(gp, gn, pos, neg):
        return float(S.wauc(gp, gn, np.ones((1, len(pos))), np.ones((1, len(neg))))[0]), S.wauc(gp, gn, W(pos), W(neg))
    floors = {}
    for nm in ("lap", "png", "asym", "d", "theta"):
        gx, gs = np.array([stat[i][nm] for i in X]), np.array([stat[i][nm] for i in SA])
        pt, dr = wauc(gx, gs, X, SA)
        if pt < 0.5:
            pt, dr = 1 - pt, 1 - dr
        floors[nm] = dict(auc_oriented=round(pt, 4), ci=[round(x, 4) for x in S.ci(dr)])
    per = {}
    for f in sorted(D.glob("HN2_*_s40?.tar")):
        assert hashlib.sha256(open(f, "rb").read()).hexdigest() == open(str(f) + ".sha256").read().split()[0], f
        T = f.stem
        if not (D / T).exists():
            with tarfile.open(f) as t:
                t.extractall(D)
        z = np.load(D / T / "hn2test/scores_eval.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        m = {"X20_over_SAME20": wauc(g(X), g(SA), X, SA), "X20_over_REC20": wauc(g(X), g(REC), X, REC),
             "SAME20_over_REC20": wauc(g(SA), g(REC), SA, REC)}
        for nm, sm in strata.items():
            pt, dr, wt = 0.0, 0.0, 0.0
            for k in range(5):
                xs, ss = [i for i in X if sm[i] == k], [i for i in SA if sm[i] == k]
                if xs and ss:
                    a, b = wauc(g(xs), g(ss), xs, ss)
                    w = len(xs) * len(ss)
                    pt, dr, wt = pt + w * a, dr + w * b, wt + w
            m[f"X20_over_SAME20_{nm}strat"] = (pt / wt, dr / wt)
        per.setdefault(T.split("_")[1], []).append(m)
    out = {}
    for arm, lst in per.items():
        out[arm] = {k: dict(mean=round(float(np.mean([m[k][0] for m in lst])), 4),
                            seeds=[round(m[k][0], 4) for m in lst],
                            ci=[round(x, 4) for x in S.ci(np.mean([m[k][1] for m in lst], 0))]) for k in lst[0]}
    out["floors_X20_vs_SAME20"] = floors
    if "RS" in out:
        v = out["RS"]["X20_over_SAME20_lapstrat"]
        out["decision"] = dict(value=v, verdict="supported: no learnable second-identity signal on this generator"
                               if v["mean"] <= 0.65 else ("falsified: a signal exists" if v["mean"] >= 0.75 and v["ci"][0] > 0.65
                                                         else "undecided"))
    json.dump(out, open(K.RES / "hn2_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

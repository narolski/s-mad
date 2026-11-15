"""MS1 part 3b (printed-only amendment, registered before computing): rank-AUC memorisation read and within-sex reads.

(a) Rank-AUC memorisation per kind and network: P[training row scored more confidently than a held-out row of the same
    kind] (attack kinds: train logit > held-out logit; negative kinds: train logit < held-out logit; ties half), with the
    same kinds, rows and held-out pools as part 3 (ms1_part3.HELD, HELD_FFHQ); A = mean over the 11 FRGC / colorFERET
    kinds. Printed per network and the count of seeds with A(SbM3) < A(Sb). This is the memorisation statistic adopted
    for any later arm (lead, 13 Nov).
(b) Within-sex reads on CFD (main set, U.S. norming): Spearman rho of the CFD logit with 'Feminine' within each
    self-reported sex, pooled over race groups and per race group x sex, per seed; median over seeds. Own-rule flag
    rates by race group x sex per seed. Printed only; no decision.
  python3 -I ms1_part3b.py [--mock] --out OUT.json
"""
import argparse
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1_part3 as P3  # noqa: E402


def rank_auc(pos, neg):
    """P[pos > neg], ties half."""
    pos, neg = np.sort(np.asarray(pos, float)), np.asarray(neg, float)
    lo = np.searchsorted(pos, neg, side="left")
    hi = np.searchsorted(pos, neg, side="right")
    greater = len(pos) - hi
    ties = hi - lo
    return float((greater.sum() + 0.5 * ties.sum()) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    M = list(csv.DictReader(open(P3.EVAL)))
    rng = np.random.default_rng(2)
    ev, tr, cfd = {}, {}, {}
    for arm in P3.ARMS:
        man = {r["path"]: r for r in csv.DictReader(open(P3.MAN[arm]))}
        for s in P3.SEEDS:
            if a.mock:
                ev[(arm, s)] = {r["id"]: float(rng.normal(-3 if r["label"] == "0" else 3, 0.5)) for r in M}
                tr[(arm, s)] = [(p, float(rng.normal(-3.2 if x["label"] == "0" else 3.2, 0.3)), x["kind"], x["db"])
                                for p, x in man.items()]
                cfd[(arm, s)] = {f"cfd_{i:04d}": float(rng.normal(-3.3, 0.4)) for i in range(831)}
                continue
            tar = P3.RES / f"MS1_{arm}_s{s}.tar"
            z = P3.load_npz(tar, "scores_eval.npz")
            ev[(arm, s)] = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            z = P3.load_npz(tar, "scores_train.npz")
            rows = []
            for p, lg in zip([str(x) for x in z["path"]], z["logit"].astype(float)):
                key = p[p.index("train/"):] if "train/" in p else p
                x = man.get(key)
                if x is not None:
                    rows.append((key, lg, x["kind"], x["db"]))
            tr[(arm, s)] = rows
            zc = np.load(P3.RES / "heldout" / f"MS1H_{arm}_s{s}_cfd.npz")
            cfd[(arm, s)] = dict(zip([str(i) for i in zc["id"]], zc["logit"].astype(float)))
    out = {"mock": a.mock}
    per, Aval = {}, {}
    for (arm, s), rows in tr.items():
        E = ev[(arm, s)]
        g = {}
        for name, held, dbs in (("", P3.HELD, ("frgc", "feret")), ("ffhq_", P3.HELD_FFHQ, ("ffhq",))):
            for kind, sel in held.items():
                t = [lg for _, lg, k, db in rows if k == kind and db in dbs]
                h = [E[r["id"]] for r in M if sel(r) and r["id"] in E]
                if t and h:
                    au = rank_auc(t, h) if kind in P3.ATTACK else rank_auc([-x for x in t], [-x for x in h])
                    g[name + kind] = dict(n_train=len(t), n_held=len(h), rank_auc=au)
        per[f"{arm}_s{s}"] = g
        Aval[(arm, s)] = float(np.mean([g[k]["rank_auc"] for k in P3.HELD if k in g]))
    out["rank_auc_memorisation"] = dict(
        per_kind=per, A={f"{k[0]}_s{k[1]}": v for k, v in Aval.items()},
        seeds_SbM3_lower=sum(1 for s in P3.SEEDS if Aval[("SbM3", s)] < Aval[("Sb", s)]),
        seeds_SbV_lower=sum(1 for s in P3.SEEDS if Aval[("SbV", s)] < Aval[("Sb", s)]))
    norm = P3.norming()
    model_of = {}
    for r in csv.DictReader(open(P3.CFD_POOL)):
        mm = re.search(r"CFD-([ABLW][FM]-\d+)-\d+-N\.jpg$", r["raw"])
        if mm and r["aligned"] == "1" and "/CFD/" in r["raw"]:
            model_of[r["id"]] = mm.group(1)
    ids = [i for i in sorted(model_of) if model_of[i] in norm and isinstance(norm[model_of[i]]["Feminine"], float)]
    ws = {}
    for arm in P3.ARMS:
        d = {}
        cells = [("F", None), ("M", None)] + [(sx, g) for g in "ABLW" for sx in "FM"]
        for sx, grp in cells:
            gi = [i for i in ids if model_of[i][1] == sx and (grp is None or model_of[i][0] == grp)]
            rhos = [P3.spearman([cfd[(arm, s)][i] for i in gi], [norm[model_of[i]]["Feminine"] for i in gi]) for s in P3.SEEDS]
            flags = [float(np.mean([cfd[(arm, s)][i] > 0 for i in gi])) for s in P3.SEEDS]
            nflag = [int(sum(cfd[(arm, s)][i] > 0 for i in gi)) for s in P3.SEEDS]
            d[(grp or "all") + sx] = dict(n=len(gi), rho_per_seed=rhos, rho_median=float(np.median(rhos)),
                                          flag_per_seed=flags, n_flagged_per_seed=nflag)
        ws[arm] = d
    out["within_sex"] = ws
    json.dump(out, open(a.out, "w"), indent=1, default=float)
    r = out["rank_auc_memorisation"]
    print(json.dumps(dict(seeds_SbM3_lower=r["seeds_SbM3_lower"], seeds_SbV_lower=r["seeds_SbV_lower"],
                          rho_F={arm: round(ws[arm]["allF"]["rho_median"], 3) for arm in ws},
                          rho_M={arm: round(ws[arm]["allM"]["rho_median"], 3) for arm in ws})))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

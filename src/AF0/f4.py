"""AF0 F4, shortcut stress test, from one image pool (AF0 training split for fits, validation split for tests).

  confounded training : every mixed image (u25, u50, grad, bump) from FRGC pairs + every zero-field image from colorFERET
  unconfounded (ref.) : same class sizes, each class drawn half from FRGC and half from colorFERET (seed 401)
  crossed test        : mixed from colorFERET + zero-field from FRGC, validation persons
Dense heads ((i) ridge, (ii) MLP seeds 401-405) are trained on all images of the set (mixed: their maps; zero: 0);
baseline (iii) logistic regression on mean-pooled tokens uses the u50 images of the set (1) vs its zero images (0).
Unprocessed photos are left out of both F4 training sets (the zero class is the zero-field images for every head).
Test AUC, primary: positives = colorFERET u50 validation images, negatives = FRGC zero-field validation images
(both heads see the same test images); secondary: positives = all colorFERET mixed validation images.
Interval: AR1's pigeonhole person bootstrap. Drop = AUC(unconfounded) - AUC(confounded).
  python3 -I f4.py make --af0 af0_w1,af0_w2          (writes the id lists)
  then heads.py --train-ids ... --tag f4_conf / f4_unconf; then  python3 -I f4.py read --backbone B
"""
import argparse
import json
import pathlib
import random
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

MIXED = ("u25", "u50", "grad", "bump")


def make(a):
    R = [r for n in a.af0.split(",") for r in L.rows(n) if r["cell"] == "train" and r["rung"] != "photo"]
    conf = [r["id"] for r in R if (r["rung"] in MIXED and r["tool"] == "frgc") or (r["rung"] == "zero" and r["tool"] == "feret")]
    cs = set(conf)
    rng = random.Random(401)
    unconf = []
    for cls in ("mixed", "zero"):
        want = sum(1 for r in R if r["id"] in cs and ((r["rung"] in MIXED) == (cls == "mixed")))
        for db in ("frgc", "feret"):
            pool = [r["id"] for r in R if r["tool"] == db and ((r["rung"] in MIXED) == (cls == "mixed"))]
            # keep the field-type mix of the confounded mixed class (all four types, equal shares)
            rng.shuffle(pool)
            unconf += pool[: want // 2]
    d = L.OUT / "f4"
    d.mkdir(parents=True, exist_ok=True)
    np.save(d / "conf_ids.npy", np.array(conf))
    np.save(d / "unconf_ids.npy", np.array(unconf))
    import collections
    c = lambda ids: dict(collections.Counter((r["tool"], r["rung"]) for r in R if r["id"] in set(ids)))  # noqa
    json.dump(dict(conf={"/".join(k): v for k, v in c(conf).items()}, unconf={"/".join(k): v for k, v in c(unconf).items()}),
              open(L.RES / "f4_sets.json", "w"), indent=1)
    print(len(conf), len(unconf))


def read(a):
    out = {}
    for tag in ("f4_conf", "f4_unconf"):
        d = L.OUT / "heads" / a.backbone / tag
        for p in sorted(d.glob("pred_*_af0_*.npz")):
            head = p.name[5:].split("_af0_")[0]
            out.setdefault(head, {}).setdefault(tag, []).append(p)
    rows = {r["id"]: r for n in a.af0.split(",") for r in L.rows(n)}
    res = {}
    for head, d in out.items():
        res[head] = {}
        for tag, paths in d.items():
            S = {}
            for p in paths:
                z = np.load(p)
                S.update(dict(zip(z["ids"], z["score"])))
            V = [rows[i] for i in S if rows[i]["cell"] == "val"]

            def grp(fn):
                rr = [r for r in V if fn(r)]
                return [float(S[r["id"]]) for r in rr], [(r["p1"], r["p2"]) for r in rr]

            neg, negp = grp(lambda r: r["tool"] == "frgc" and r["rung"] == "zero")
            r1 = {}
            for name, fn in (("crossed_u50", lambda r: r["tool"] == "feret" and r["rung"] == "u50"),
                             ("crossed_allmixed", lambda r: r["tool"] == "feret" and r["rung"] in MIXED)):
                pos, posp = grp(fn)
                auc, ci = L.auc_ci(pos, posp, neg, negp)
                r1[name] = dict(auc=round(auc, 4), ci=[round(x, 4) for x in ci], n=[len(pos), len(neg)])
            # unconfounded-style test on all validation images (both databases), u50 vs zero
            pos, posp = grp(lambda r: r["rung"] == "u50")
            n2, n2p = grp(lambda r: r["rung"] == "zero")
            auc, ci = L.auc_ci(pos, posp, n2, n2p)
            r1["allval_u50_vs_zero"] = dict(auc=round(auc, 4), ci=[round(x, 4) for x in ci], n=[len(pos), len(n2)])
            res[head][tag] = r1
        if "f4_conf" in res[head] and "f4_unconf" in res[head]:
            res[head]["drop_crossed_u50"] = round(res[head]["f4_unconf"]["crossed_u50"]["auc"] -
                                                  res[head]["f4_conf"]["crossed_u50"]["auc"], 4)
    json.dump(res, open(L.RES / f"f4_{a.backbone}.json", "w"), indent=1)
    for h, r in res.items():
        print(h, r.get("drop_crossed_u50"), {t: r[t]["crossed_u50"] for t in ("f4_conf", "f4_unconf") if t in r})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("make", "read"))
    ap.add_argument("--af0", default="af0_w1,af0_w2")
    ap.add_argument("--backbone", default="dinov3_512")
    a = ap.parse_args()
    make(a) if a.cmd == "make" else read(a)

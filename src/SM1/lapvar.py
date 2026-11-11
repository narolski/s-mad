"""SM1 rebuild acceptance (amendments A3, A4): Laplacian-variance AUC of an arm's morphs against its genuine class.

Measurement only (no image is written): variance of cv2.Laplacian(grey, CV_64F)
  stored : cv2.imread(IMREAD_GRAYSCALE) of the stored file
  loader : common.ImageItems(...).load(p) (the loader's own PIL bilinear resize to 224), RGB -> grey (cv2.cvtColor)
AUC = P(variance of a morph < variance of a genuine-class image) (lower variance = morph), 2,000 + 2,000 seeded
images per arm (seed 401 composition for d / e); also morph against its own two halves (arm c, 2,000 pairs); size
check (PNG header) of every rebuilt file. Accepted iff AUC <= 0.65 (stored for a..d, loader for e).

  python3 -I lapvar.py [--arms a,b,...] [--n 2000] [--workers 2]
-> RES/lapvar.json
"""
import argparse
import csv
import json
import pathlib
import struct
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

FL = K.OUT / "flists"
_IT = None


def _init():
    global _IT
    for p in (K.MC, K.W46 / "smadcvpr"):
        sys.path.insert(0, str(p))
    import common as C
    _IT = C.ImageItems([], 224, root="/")


def lv(p):
    import cv2
    cv2.setNumThreads(1)
    g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    a = float(cv2.Laplacian(g, cv2.CV_64F).var()) if g is not None else np.nan
    img, _ = _IT.load(p)
    g2 = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    return a, float(cv2.Laplacian(g2, cv2.CV_64F).var())


def paths(name):
    return [r["path"] for r in csv.DictReader(open(FL / f"{name}.csv"))]


def size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    return struct.unpack(">II", h[16:24])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="a,b,bp,c,cr,d,e,d50,d500")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    from multiprocessing import Pool
    rng = np.random.default_rng(401)
    bf = paths("train_bf")
    arma = [r["path"] for r in csv.DictReader(open(FL / "train_arma.csv"))]
    src = {"a": arma, "b": paths("train_armb"), "bp": paths("train_armbp"), "c": paths("train_armc"),
           "cr": paths("train_armcr")}
    for k, f in (("d50", "train_armd50"), ("d500", "train_armd500")):
        if (FL / f"{f}.csv").exists():
            src[k] = paths(f)
    hal = paths("train_armc_halves")
    pick = lambda L, n: [L[i] for i in rng.choice(len(L), size=min(n, len(L)), replace=False)]  # noqa: E731
    jobs, plan = {}, {}
    n = a.n
    for arm in a.arms.split(","):
        if arm in src:
            m = pick(src[arm], n)
            g = pick(bf, n)
        elif arm == "d":
            m = pick(src["c"], n)
            g = pick(bf, n // 2) + pick(hal, n - n // 2)
        elif arm == "f":                                    # A10: the seed-401 composition of compose.py
            import json as _j
            idp = {}
            for n in ("train_bf", "train_arme_bfS", "train_armc_halves", "train_arme_hS", "train_armc",
                      "train_arme_cS", "train_armf_jpeg"):
                for r in csv.DictReader(open(FL / f"{n}.csv")):
                    idp[r["id"]] = r["path"]
            c = _j.load(open(K.OUT / "compose/f_s401.json"))
            m = pick([idp[i] for i in c["morph"]], n)
            g = pick([idp[i] for i in c["genuine"]], n)
        elif arm == "e":
            bfs, cs, hs = paths("train_arme_bfS"), paths("train_arme_cS"), paths("train_arme_hS")
            m = pick(src["c"], n // 2) + pick(cs, n - n // 2)
            g = pick(bf, n // 4) + pick(bfs, n // 4) + pick(hal, n // 4) + pick(hs, n - 3 * (n // 4))
        else:
            continue
        plan[arm] = (m, g)
    cpairs = list(csv.DictReader(open(K.OUT / "lists/armc.csv")))
    cp = [cpairs[i] for i in rng.choice(len(cpairs), size=min(n, len(cpairs)), replace=False)]
    allp = sorted({p for m, g in plan.values() for p in m + g} |
                  {x for r in cp for x in (r["out"], r["out"][:-4] + "_hA.png", r["out"][:-4] + "_hB.png")})
    with Pool(a.workers, initializer=_init) as pool:
        vals = dict(zip(allp, pool.map(lv, allp, chunksize=32)))
    out = {}
    for arm, (m, g) in plan.items():
        o = {}
        for j, key in ((0, "stored"), (1, "loader224")):
            vm = np.array([vals[p][j] for p in m])
            vg = np.array([vals[p][j] for p in g])
            o[key] = dict(auc=float(S.wauc(-vm, -vg, np.ones((1, len(vm))), np.ones((1, len(vg))))[0]),
                          median_morph=float(np.median(vm)), median_genuine=float(np.median(vg)))
        acc_key = "loader224" if arm in ("e", "f") else "stored"
        o["accepted"] = bool(o[acc_key]["auc"] <= 0.65) if arm != "a" else None
        o["acceptance_on"] = acc_key
        if arm not in ("a", "f"):
            sz = [size(p) for p in src.get(arm, src["c"])]
            o["files_not_256"] = int(sum(s != (256, 256) for s in sz))
        out[arm] = o
    vm = np.array([vals[r["out"]][0] for r in cp])
    vh = np.array([[vals[r["out"][:-4] + "_hA.png"][0], vals[r["out"][:-4] + "_hB.png"][0]] for r in cp])
    out["c_morph_vs_own_halves"] = dict(
        auc=float(S.wauc(-vm, -vh.ravel(), np.ones((1, len(vm))), np.ones((1, vh.size)))[0]),
        median_ratio_morph_over_mean_halves=float(np.median(vm / vh.mean(1))))
    json.dump(out, open(K.RES / ("lapvar.json" if a.arms != "f" else "lapvar_f.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

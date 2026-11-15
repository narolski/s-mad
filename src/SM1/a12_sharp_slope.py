"""SM1 amendment A12 item 9 (post hoc, H-new-2): head logit against sharpness, per arm and class of training images.

Per arm, seed-401 composition: 2,000 seeded morphs and 2,000 seeded genuine-class images (numpy default_rng(401);
the renders-only arms share one draw of genuine renders); log variance of the Laplacian of the grey image at the
loader's 224 px (lapvar.py); the seed-401 head's logit on those training images (heads/<arm>_s401.npz W, b on the
Athena features). Spearman correlation within each class, with a 500-draw image bootstrap interval (seed 20261111).
Prediction (review): more negative from b -> K = 50 -> b' ; falsified if |delta rho| < 0.05 from b to b'.
Descriptive extra: the same with the release-recipe heads (heads_fz1) when present.

  python3 -I a12_sharp_slope.py -> RES/a12_sharp_slope.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import lapvar as L  # noqa: E402
import heads as H  # noqa: E402

ARMS = ("a", "b", "d50", "d500", "bp", "cr", "c", "d", "e", "f")
N = 2000


def rank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return r


def spear(a, b):
    return float(np.corrcoef(rank(a), rank(b))[0, 1])


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    idp = {}
    for nm in H.TRAIN:
        p = K.OUT / f"flists/{nm}.csv"
        if p.exists():
            for r in csv.DictReader(open(p)):
                idp[r["id"]] = r["path"]
    for r in csv.DictReader(open(K.OUT / "flists/train_arma.csv")):
        idp.setdefault(r["id"], r["path"])
    L._init()
    bank = H.Bank(H.TRAIN)
    rng0 = np.random.default_rng(401)
    bf = json.load(open(K.OUT / "compose/a_s401.json"))["genuine"]
    g_bf = [bf[i] for i in rng0.choice(len(bf), N, replace=False)]
    cache = {}

    def var224(ids):
        out = []
        for i in ids:
            if i not in cache:
                cache[i] = L.lv(idp[i])[1]
            out.append(cache[i])
        return np.log(np.maximum(np.array(out), 1e-6))

    bt = np.random.default_rng(K.SEED).integers(0, N, (2000, N))
    res = {}
    for arm in ARMS:
        c = json.load(open(K.OUT / f"compose/{arm}_s401.json"))
        rng = np.random.default_rng([401, ARMS.index(arm)])
        m = [c["morph"][i] for i in rng.choice(len(c["morph"]), N, replace=False)]
        g = g_bf if arm in ("a", "b", "d50", "d500", "bp", "cr", "c") else \
            [c["genuine"][i] for i in rng.choice(len(c["genuine"]), N, replace=False)]
        vm, vg = var224(m), var224(g)
        o = {}
        for tag, d in (("ours", K.OUT / "heads"), ("fz1_recipe", K.OUT / "heads_fz1")):
            f = d / f"{arm}_s401.npz"
            if not f.exists():
                continue
            z = np.load(f)
            W, b = z["W"], z["b"]
            if tag == "ours":
                lg = lambda ids: bank.get(ids) @ W + b  # noqa: E731
            else:
                def lg(ids, W=W, b=b):
                    F_ = bank.get(ids)
                    F_ = F_ / np.maximum(np.linalg.norm(F_, axis=1, keepdims=True), 1e-12)
                    zz = F_ @ W.T + b
                    return zz[:, 0] - zz[:, 1]
            zm, zg = lg(m), lg(g)
            o[tag] = {}
            for cls, zz, vv in (("morph", zm, vm), ("genuine", zg, vg)):
                bs = [spear(zz[ix], vv[ix]) for ix in bt[:500]]
                o[tag][cls] = dict(rho=round(spear(zz, vv), 4), ci=[round(x, 4) for x in S.ci(bs)])
        o["median_log_var224"] = dict(morph=round(float(np.median(vm)), 3), genuine=round(float(np.median(vg)), 3))
        res[arm] = o
        print(arm, json.dumps(o), flush=True)
    pr = {}
    for tag in ("ours", "fz1_recipe"):
        if all(tag in res[x] for x in ("b", "d50", "bp")):
            pr[tag] = {cls: dict(b=res["b"][tag][cls]["rho"], d50=res["d50"][tag][cls]["rho"],
                                 bp=res["bp"][tag][cls]["rho"],
                                 delta_b_to_bp=round(res["bp"][tag][cls]["rho"] - res["b"][tag][cls]["rho"], 4))
                       for cls in ("morph", "genuine")}
    res["prediction"] = dict(text="rho more negative from b -> K = 50 -> b'; falsified if |delta rho| < 0.05 from b to "
                                  "b'", values=pr, bootstrap="500 image-bootstrap draws per class (seed 20261111)")
    json.dump(res, open(K.RES / "a12_sharp_slope.json", "w"), indent=1)


if __name__ == "__main__":
    main()

"""PD1 DiffAE family: shared helpers (data loading, folds, bootstrap, AUC, heads).

wauc, Draw, ci and weer are copied verbatim from src/FZ1/fz1_common.py (themselves verbatim from src/AD1/ad1_read.py,
the a41_read.py pigeonhole two-way person bootstrap).
"""
import csv, hashlib, json, pathlib
import numpy as np

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/diffae")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/PD1_signal-isolation-paired-differences/diffae")
ITEMS = BIG / "lists/items.csv"
SEED_TR = [20261111, 1, 1]
SEED_FRLL = [20261107, 43, 1]
CS = (1e-3, 1e-2, 1e-1, 1.0, 10.0)
FEATS = ("clip_pool", "clip_patch", "dino_pool", "dino_patch")
PRIMARY = "clip_pool"
STEPS = {"P": ("x0", "x1"), "M": ("x1", "x2"), "I": ("x2", "x3"), "W": ("x1", "x3"), "G": ("x0", "x3")}
STEP_NAMES = {"P": "pipeline trace (x0 to x1)", "M": "same-person mixing (x1 to x2)", "I": "second identity (x2 to x3)",
              "W": "whole morph (x1 to x3)", "G": "genuine to morph (x0 to x3)", "S": "softening (SMDD original to shrunk copy)"}


# ---------------------------------------------------------------- verbatim copies (FZ1 / AD1)
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    return (wp * (below + 0.5 * tie)).sum(1) / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def auc(pos, neg):
    return float(wauc(np.asarray(pos, float), np.asarray(neg, float), np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


class Draw:
    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, pp):
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[-1]] for p in pp])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        w[:, same] = self.C[:, a[same]]
        return w


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def weer(pos, neg, wp, wn):
    s = np.r_[neg, pos]
    ispos = np.r_[np.zeros(len(neg), bool), np.ones(len(pos), bool)]
    o = np.argsort(s, kind="stable")
    ss, ip = s[o], ispos[o]
    W = np.concatenate([wn, wp], 1)[:, o]
    WN = np.where(ip[None, :], 0.0, W)
    WP = np.where(ip[None, :], W, 0.0)
    cN = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(WN, 1)], 1)
    cP = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(WP, 1)], 1)
    _, first = np.unique(ss, return_index=True)
    fpr = 1 - cN[:, first] / np.maximum(cN[:, -1:], 1e-12)
    fnr = cP[:, first] / np.maximum(cP[:, -1:], 1e-12)
    i = np.argmin(np.abs(fpr - fnr), 1)
    r = np.arange(W.shape[0])
    return 100 * (fpr[r, i] + fnr[r, i]) / 2


# ---------------------------------------------------------------- PD1 helpers
def items():
    return list(csv.DictReader(open(ITEMS)))


def hsh(s):
    return hashlib.sha256(s.encode()).hexdigest()


def folds_of(blocks, k=5, salt="PD1:"):
    order = sorted(blocks, key=lambda b: hsh(salt + b))
    return {b: i % k for i, b in enumerate(order)}


def load_feats(model_feat, sets, ids_needed=None):
    """model_feat e.g. 'clip_pool' -> {id: L2-normalised vector} for the given sets."""
    model, kind = model_feat.split("_")
    out = {}
    for s in sets:
        p = BIG / "feat" / model / f"{s}.npz"
        if not p.exists():
            continue
        z = np.load(p, allow_pickle=False)
        F = z[kind].astype(np.float64)
        F /= np.linalg.norm(F, axis=1, keepdims=True)
        for i, f in zip(z["id"].tolist(), F):
            out[i] = f
    return out


def load_stats(sets):
    out = {}
    names = None
    for s in sets:
        p = BIG / "stats" / f"{s}.npz"
        if not p.exists():
            continue
        z = np.load(p, allow_pickle=False)
        names = z["names"].tolist()
        for i, v in zip(z["id"].tolist(), z["stats"]):
            out[i] = v
    return out, names


def training_pool(rows):
    """Hosts of the training pool: list of dicts with block, host, person, partner, x0..x3 ids, cohort."""
    tr = [r for r in rows if r["set"] == "tr"]
    by_host = {}
    for r in tr:
        for h in r["host"].split(";"):
            by_host.setdefault(h, {})[r["rung"]] = r
    hosts = []
    for h, d in sorted(by_host.items()):
        assert set(d) == {"x0", "x1", "x2", "x3"}, (h, d.keys())
        A = d["x0"]["persons"]
        pp = d["x3"]["persons"].split(";")
        partner = pp[1] if pp[0] == A else pp[0]
        hosts.append(dict(host=h, block=d["x0"]["block"], person=A, partner=partner, cohort=d["x0"]["split"],
                          **{k: d[k]["id"] for k in ("x0", "x1", "x2", "x3")}))
    return hosts


def persons_of(row):
    return tuple(row["persons"].split(";"))


def clopper(k, n):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


def fit_pair_head(Zp, Zn, C):
    """Linear head, no intercept, paired logistic loss on Zp - Zn (both orientations). Returns w."""
    from sklearn.linear_model import LogisticRegression
    D = Zp - Zn
    X = np.vstack([D, -D])
    y = np.r_[np.ones(len(D)), np.zeros(len(D))]
    m = LogisticRegression(C=C, fit_intercept=False, max_iter=5000, solver="lbfgs")
    m.fit(X, y)
    return m.coef_[0]


def dump(obj, name):
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(obj, open(OUT / name, "w"), indent=1, default=float)

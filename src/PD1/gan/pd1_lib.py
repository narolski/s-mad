"""Signal isolation by paired differences (PD1), GAN family: shared helpers.

wauc is copied from src/FZ1/fz1_common.py (itself from the MorDIFF ladder re-read, AD1). Cluster bootstrap: each
cluster (block, pair, image or FRLL person) gets a multinomial count per draw; an image's weight is the count of its
cluster, or the product of its two persons' counts for a two-person FRLL morph (AD1's two-way draw).
"""
import csv, json, pathlib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/PD1_signal-isolation-paired-differences/gan")
CS = (1e-3, 1e-2, 1e-1, 1.0, 10.0)
FEATS = (("clip", "pool"), ("clip", "patch"), ("dinov3", "pool"), ("dinov3", "patch"))
FNAME = {("clip", "pool"): "CLIP pooled", ("clip", "patch"): "CLIP mean patch token",
         ("dinov3", "pool"): "DINOv3 pooled", ("dinov3", "patch"): "DINOv3 mean patch token"}


def items():
    return list(csv.DictReader(open(BIG / "items.csv")))


def hosts():
    return list(csv.DictReader(open(BIG / "hosts.csv")))


def load_feats(backbone, kind, sets):
    """id -> L2-normalised vector."""
    F = {}
    for s in sets:
        p = BIG / "feats" / backbone / f"{s}.npz"
        if not p.exists():
            continue
        z = np.load(p, allow_pickle=False)
        X = z[kind].astype(np.float64)
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        F.update(zip(z["id"].tolist(), X))
    return F


def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    return (wp * (below + 0.5 * tie)).sum(1) / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def auc(pos, neg):
    return float(wauc(np.asarray(pos, float), np.asarray(neg, float), np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


def ci(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))]


class Draw:
    """multinomial cluster counts; w(list of cluster tuples) -> (B, n) weights."""

    def __init__(self, clusters, B, seed):
        self.per = sorted(set(clusters))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, cl):
        cl = [c if isinstance(c, tuple) else (c,) for c in cl]
        a = np.array([self.pos[c[0]] for c in cl])
        b = np.array([self.pos[c[-1]] for c in cl])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        w[:, same] = self.C[:, a[same]]
        return w


def folds(clusters, k, seed):
    u = sorted(set(clusters))
    perm = np.random.default_rng(seed).permutation(len(u))
    return {u[j]: int(i % k) for i, j in enumerate(perm)}


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def project_out(X, U):
    """remove the span of the rows of U (orthonormalised) from the rows of X."""
    if U is None or len(U) == 0:
        return X
    Q, _ = np.linalg.qr(np.asarray(U, float).T)
    return X - (X @ Q) @ Q.T


class PairHead:
    """linear head, logistic loss on z(pos) - z(neg), no intercept, both signs fed."""

    def __init__(self, C):
        self.C = C

    def fit(self, Xtrain_imgs, Dp, Dn):
        self.sc = StandardScaler().fit(Xtrain_imgs)
        D = self.sc.transform(Dp) - self.sc.transform(Dn)
        X = np.r_[D, -D]
        y = np.r_[np.ones(len(D)), np.zeros(len(D))]
        self.lr = LogisticRegression(C=self.C, fit_intercept=False, max_iter=5000).fit(X, y)
        self.w = self.lr.coef_[0]
        return self

    def score(self, X):
        return self.sc.transform(X) @ self.w


def paired_auc(sp, sn):
    d = np.asarray(sp) - np.asarray(sn)
    return float(np.mean((d > 0) + 0.5 * (d == 0)))


def fit_head(F, pairs, groups, img_ids, seed, C=None):
    """pairs: list of (pos_id, neg_id); groups: cluster per pair; img_ids: training images for the scaler.
    C by inner 3-fold grouped CV (paired AUC; ties to smaller C) unless given."""
    Xi = np.array([F[i] for i in img_ids])
    P = np.array([F[p] for p, _ in pairs])
    N = np.array([F[n] for _, n in pairs])
    if C is None:
        fo = folds(groups, 3, seed)
        g = np.array([fo[c] for c in groups])
        best, bestC = -1, None
        for c in CS:
            accs = []
            for k in range(3):
                tr, te = g != k, g == k
                trimg = sorted({i for (p, n), t in zip(pairs, tr) if t for i in (p, n)})
                h = PairHead(c).fit(np.array([F[i] for i in trimg]), P[tr], N[tr])
                accs.append(paired_auc(h.score(P[te]), h.score(N[te])) * te.sum())
            a = sum(accs) / len(pairs)
            if a > best + 1e-12:
                best, bestC = a, c
        C = bestC
    return PairHead(C).fit(Xi, P, N), C


def dump(obj, name):
    json.dump(obj, open(OUT / name, "w"), indent=1, default=float)

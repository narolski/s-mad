"""Verifier helpers for PD1 GAN (independent of src/PD1/gan). Read-only on /mnt/t7/smad_next/PD1/gan."""
import csv, pathlib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
OUT = pathlib.Path(__file__).resolve().parent
CS = (1e-3, 1e-2, 1e-1, 1.0, 10.0)


def rows(name):
    return list(csv.DictReader(open(BIG / name)))


def feats(bb, kind, sets):
    F = {}
    for s in sets:
        z = np.load(BIG / "feats" / bb / f"{s}.npz", allow_pickle=False)
        X = z[kind].astype(np.float64)
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        F.update(zip(z["id"].tolist(), X))
    return F


def auc(p, n):
    p, n = np.asarray(p, float), np.asarray(n, float)
    return float(roc_auc_score(np.r_[np.ones(len(p)), np.zeros(len(n))], np.r_[p, n]))


def boot_auc(sp, cp, sn, cn, B=2000, seed=11):
    """cluster bootstrap of AUC; cp/cn cluster labels of each pos/neg score."""
    sp, sn = np.asarray(sp, float), np.asarray(sn, float)
    cl = sorted(set(cp) | set(cn))
    ix = {c: i for i, c in enumerate(cl)}
    ip, inn = np.array([ix[c] for c in cp]), np.array([ix[c] for c in cn])
    rng = np.random.default_rng(seed)
    # rank-based weighted AUC
    order = np.argsort(sn)
    sns = sn[order]
    lo, hi = np.searchsorted(sns, sp, "left"), np.searchsorted(sns, sp, "right")
    out = []
    for _ in range(B):
        cnt = rng.multinomial(len(cl), np.full(len(cl), 1 / len(cl))).astype(float)
        wp, wn = cnt[ip], cnt[inn][order]
        C = np.r_[0, np.cumsum(wn)]
        v = (wp * (C[lo] + 0.5 * (C[hi] - C[lo]))).sum() / max(wp.sum() * C[-1], 1e-12)
        out.append(v)
    return [float(np.quantile(out, .025)), float(np.quantile(out, .975))]


def block_folds(blocks, k, seed):
    u = sorted(set(blocks))
    p = np.random.default_rng(seed).permutation(len(u))
    return {u[j]: i % k for i, j in enumerate(p)}


class Std:
    def fit(self, X):
        self.m, self.s = X.mean(0), X.std(0) + 1e-9
        return self

    def __call__(self, X):
        return (X - self.m) / self.s


def fit_paired(Ximg, P, N, C):
    st = Std().fit(Ximg)
    D = st(P) - st(N)
    lr = LogisticRegression(C=C, fit_intercept=False, max_iter=5000).fit(np.r_[D, -D], np.r_[np.ones(len(D)), np.zeros(len(D))])
    w = lr.coef_[0]
    return lambda X: st(X) @ w


def fit_unpaired(P, N, C):
    st = Std().fit(np.r_[P, N])
    lr = LogisticRegression(C=C, max_iter=5000).fit(st(np.r_[P, N]), np.r_[np.ones(len(P)), np.zeros(len(N))])
    w, b = lr.coef_[0], lr.intercept_[0]
    return lambda X: st(X) @ w + b


def fit_head(kind, F, pairs, groups, seed, C=None):
    """pairs: (pos_id, neg_id); groups: block of each pair. C by inner 3-fold grouped CV
    (kind=paired: paired win share; kind=unpaired: image AUC), ties -> smaller C."""
    groups = np.asarray(groups)

    def build(idx, c):
        pp = [pairs[i] for i in idx]
        P = np.array([F[p] for p, _ in pp]); N = np.array([F[n] for _, n in pp])
        if kind == "paired":
            img = sorted({x for pr in pp for x in pr})
            return fit_paired(np.array([F[i] for i in img]), P, N, c)
        Pu = np.array([F[i] for i in sorted({p for p, _ in pp})]); Nu = np.array([F[i] for i in sorted({n for _, n in pp})])
        return fit_unpaired(Pu, Nu, c)

    if C is None:
        fo = block_folds(groups, 3, seed)
        g = np.array([fo[x] for x in groups])
        best, C = -1, None
        for c in CS:
            sc = []
            for k in range(3):
                tr, te = np.where(g != k)[0], np.where(g == k)[0]
                h = build(tr, c)
                pp = [pairs[i] for i in te]
                sp = h(np.array([F[p] for p, _ in pp])); sn = h(np.array([F[n] for _, n in pp]))
                if kind == "paired":
                    sc.append(np.mean(sp > sn) * len(te))
                else:
                    up, un = sorted({p for p, _ in pp}), sorted({n for _, n in pp})
                    sc.append(auc(h(np.array([F[i] for i in up])), h(np.array([F[i] for i in un]))) * len(te))
            a = sum(sc) / len(pairs)
            if a > best + 1e-12:
                best, C = a, c
    return build(np.arange(len(pairs)), C), C

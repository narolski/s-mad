"""ID0 identity-subspace shrinkage statistic (prereg section "The statistic"), fitted on genuine photos only.

ISS(X, pid): PCA (95% variance, at most kmax components) -> pooled within-person S_w (ridge 1e-3 tr/k) and between-
person S_b (cov of person means minus mean(1/n_p) S_w) -> generalised eigenproblem S_b v = lam S_w v (V' S_w V = I).
Scores (higher = more morph-like): iss = -sum_{lam>1} w z^2, w = 1/(lam/2+1) - 1/(lam+1); typ = -sum z^2/(lam+1);
ses = -sum_{lam<=1} z^2/(lam+1). Predictions: physics closed form and the fitted-spectrum simulation.
"""
import collections

import numpy as np
from scipy.stats import norm


class ISS:
    def __init__(self, X, pid, kmax=64, var=0.95, ridge=1e-3, k=None):
        X = np.asarray(X, np.float64)
        self.m = X.mean(0)
        Xc = X - self.m
        _, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        ev = S ** 2 / (len(X) - 1)
        cum = np.cumsum(ev) / ev.sum()
        self.k95 = int(np.searchsorted(cum, var) + 1)
        self.k = int(k if k is not None else min(self.k95, kmax))
        self.k = min(self.k, len(S))
        self.P = Vt[: self.k].T
        self.var_kept = float(cum[self.k - 1])
        Y = Xc @ self.P
        g = collections.defaultdict(list)
        for i, p in enumerate(pid):
            g[p].append(i)
        Sw = np.zeros((self.k, self.k))
        dof = 0
        means, invn = [], []
        for p, ix in g.items():
            yp = Y[ix]
            mu = yp.mean(0)
            means.append(mu)
            invn.append(1.0 / len(ix))
            if len(ix) >= 2:
                d = yp - mu
                Sw += d.T @ d
                dof += len(ix) - 1
        Sw /= dof
        self.dof_w = dof
        self.n_persons = len(g)
        Swr = Sw + ridge * np.trace(Sw) / self.k * np.eye(self.k)
        M = np.array(means)
        Sb = np.cov(M.T) - np.mean(invn) * Sw
        L = np.linalg.cholesky(Swr)
        Li = np.linalg.inv(L)
        lam, W = np.linalg.eigh(Li @ Sb @ Li.T)
        o = np.argsort(lam)[::-1]
        self.lam = lam[o]
        self.V = Li.T @ W[:, o]
        self.J = self.lam > 1
        lp = np.clip(self.lam, 0, None)
        self.lp = lp
        self.w = 1.0 / (lp / 2 + 1) - 1.0 / (lp + 1)

    # -- scores
    def z(self, X):
        return ((np.asarray(X, np.float64) - self.m) @ self.P) @ self.V

    def scores(self, X):
        z = self.z(X)
        J = self.J
        return dict(iss=-(z[:, J] ** 2 * self.w[J]).sum(1),
                    typ=-(z ** 2 / (self.lp + 1)).sum(1),
                    ses=-(z[:, ~J] ** 2 / (self.lp[~J] + 1)).sum(1))

    def c_pair(self, XA, XB):
        za, zb = self.z(XA), self.z(XB)
        J = self.J
        return (za[:, J] * zb[:, J]).sum(1) / self.lam[J].sum()

    # -- predictions
    @property
    def d(self):
        return int(self.J.sum())

    @property
    def n_ratio(self):
        return float(self.d / self.lam[self.J].sum()) if self.d else float("nan")

    def pred_closed(self, c):
        d, n = self.d, self.n_ratio
        if not d:
            return 0.5
        s = ((1 + c) / 2 + n) / (1 + n)
        return float(norm.cdf(np.sqrt(d / 2) * (1 - s) / np.sqrt(1 + s ** 2)))

    def pred_spectrum(self, c, N=200000, seed=20261111):
        if not self.d:
            return 0.5
        r = np.random.default_rng(seed)
        lam, w = self.lam[self.J], self.w[self.J]
        g = r.standard_normal((N, len(lam))) * np.sqrt(lam + 1)
        m = r.standard_normal((N, len(lam))) * np.sqrt(lam * (1 + c) / 2 + 1)
        sg, sm = -(g ** 2 * w).sum(1), -(m ** 2 * w).sum(1)
        return auc_fast(sm, sg)

    def summary(self):
        return dict(k=self.k, k95=self.k95, var_kept=round(self.var_kept, 4), persons=self.n_persons, dof_w=self.dof_w,
                    d=self.d, n_ratio=round(self.n_ratio, 4), lam_top=[round(float(x), 3) for x in self.lam[:10]],
                    lam_sum_J=round(float(self.lam[self.J].sum()), 3))


def auc_fast(pos, neg):
    """Mann-Whitney AUC, P(pos > neg) + 0.5 ties."""
    from scipy.stats import rankdata
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))

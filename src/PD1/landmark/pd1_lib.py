"""PD1 landmark: feature loading, the AR1 host table, paired heads, directions and projections."""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402

LISTS = ("ar1", "smdd", "af0", "bench", "h1", "ar1g", "ar1soft", "af0h")


def sources(feat, lst):
    if feat == "dino_mean":
        return {"ar1": [("dinov3_512", "af0_ar1_mean", "mean"), ("dinov3_512", "ar1_R2wm", "mean")],
                "smdd": [("dinov3_512", "smdd", "mean")],
                "af0": [("dinov3_512", "af0_af0_w1_mean", "mean"), ("dinov3_512", "af0_af0_w2_mean", "mean")],
                "bench": [("dinov3_512", "af0_bench_s_mean", "mean")],
                "h1": [("dinov3_512", "af0_h1_mean", "mean")],
                "ar1g": [("dinov3_512", "af0_ar1g_mean", "mean")],
                "ar1soft": [("dinov3_512", "ar1soft", "mean")],
                "af0h": [("dinov3_512", "af0_af0_h_mean", "mean"), ("dinov3_512", "af0h", "mean")]}[lst]
    key = {"clip_cls": "cls", "clip_mean": "mean"}[feat]
    return [("clip224", lst, key)]


def load(feat, lst):
    """dict id -> float32 vector, restricted to the ids of PD1's list (missing sources are skipped)."""
    want = {r["id"] for r in K.rows(K.OUT / "lists" / f"{lst}.csv")}
    out = {}
    for bb, name, key in sources(feat, lst):
        p = K.OUT / "feat" / bb / f"{name}.npz"
        if not p.exists():
            continue
        z = np.load(p)
        for i, v in zip(z["ids"], z[key]):
            i = str(i)
            if i in want:
                out[i] = v.astype(np.float32)
    return out


class Table:
    """AR1 primary pool: hosts in pool.csv order; Z[(tool, rung)] = (n, D); R0 is stored under tool 'none'."""

    def __init__(self, feat, pool="frgcferet"):
        pr = K.rows(K.POOL) if pool == "frgcferet" else K.rows(K.AR1 / "pool_frll.csv")
        self.hosts = [r["pid"] for r in pr]
        self.partner = {r["pid"]: r["B_pid"] for r in pr}
        self.cosHB = {r["pid"]: float(r["cos_HB"]) for r in pr}
        self.ix = {h: i for i, h in enumerate(self.hosts)}
        F = load(feat, "ar1")
        self.Z, self.ids = {}, {}
        n = len(self.hosts)
        for r in K.rows(K.OUT / "lists/ar1.csv"):
            if r["pool"] != pool or r["id"] not in F:
                continue
            k = (r["tool"], r["rung"])
            if k not in self.Z:
                self.Z[k] = np.full((n, len(F[r["id"]])), np.nan, np.float32)
                self.ids[k] = [None] * n
            i = self.ix[r["p1"]]
            if r["rung"] == "R4":
                assert r["p2"] == self.partner[r["p1"]], (r["p1"], r["p2"])
            self.Z[k][i] = F[r["id"]]
            self.ids[k][i] = r["id"]
        for k, v in self.Z.items():
            assert not np.isnan(v).any(), ("missing features", feat, k)

    def get(self, tool, rung):
        return self.Z[("none", "R0")] if rung == "R0" else self.Z[(tool, rung)]

    def has(self, tool, rung):
        return ("none", "R0") in self.Z if rung == "R0" else (tool, rung) in self.Z

    def persons(self, rung, idx):
        """bootstrap person tuples of the images of hosts idx at a rung."""
        if rung == "R4":
            return [(self.hosts[i], self.partner[self.hosts[i]]) for i in idx]
        return [(self.hosts[i],) for i in idx]


def fold_split(T, fold, k):
    test = [i for i, h in enumerate(T.hosts) if fold[h] == k]
    excl = {T.partner[T.hosts[i]] for i in test}
    train = [i for i, h in enumerate(T.hosts) if fold[h] != k and h not in excl]
    train2 = [i for i in train if fold[T.partner[T.hosts[i]]] != k]
    return np.array(train), np.array(train2), np.array(test)


# ------------------------------------------------------------------------------------------------ heads
def unit(v):
    return v / max(np.linalg.norm(v), 1e-12)


def orth_basis(vs):
    U = []
    for v in vs:
        v = v.astype(np.float64).copy()
        for u in U:
            v -= (v @ u) * u
        if np.linalg.norm(v) > 1e-9:
            U.append(unit(v))
    return np.array(U) if U else None


def remove(Z, U):
    return Z if U is None else Z - (Z @ U.T) @ U


class Head:
    def __init__(self, mu, sd, w, C, U):
        self.mu, self.sd, self.w, self.C, self.U = mu, sd, w, C, U

    def z(self, X):
        return remove((np.asarray(X, np.float64) - self.mu) / self.sd, self.U)

    def score(self, X):
        return self.z(X) @ self.w


def _fit_lr(Dz, C):
    from sklearn.linear_model import LogisticRegression
    X = np.vstack([Dz, -Dz])
    y = np.r_[np.ones(len(Dz)), np.zeros(len(Dz))]
    m = LogisticRegression(C=C, fit_intercept=False, max_iter=5000, tol=1e-6)
    m.fit(X, y)
    return m.coef_[0].copy()


def fit_paired(P, N, g, Cs=(1e-3, 1e-2, 1e-1, 1.0), proj=None, extra_fit=None):
    """P, N: (m, D) raw features of row-aligned (positive, negative) pairs; g: (m,) group ids (inner CV by group).
    proj(mu, sd) -> list of directions in z space to project out (or None). Returns Head."""
    from sklearn.model_selection import GroupKFold
    X = np.vstack([P, N]).astype(np.float64)
    mu, sd = X.mean(0), X.std(0) + 1e-6
    U = orth_basis(proj(mu, sd)) if proj is not None else None
    zP, zN = remove((P - mu) / sd, U), remove((N - mu) / sd, U)
    best, bestC = -1, Cs[0]
    if len(Cs) > 1:
        gkf = GroupKFold(n_splits=3)
        res = {C: [] for C in Cs}
        for tr, va in gkf.split(zP, groups=g):
            for C in Cs:
                w = _fit_lr(zP[tr] - zN[tr], C)
                res[C].append(K.auc(zP[va] @ w, zN[va] @ w))
        for C in Cs:                       # ties -> smaller C (first in order)
            m = float(np.mean(res[C]))
            if m > best + 1e-12:
                best, bestC = m, C
    w = _fit_lr(zP - zN, bestC)
    return Head(mu, sd, w, bestC, U)


# ------------------------------------------------------------------------------------------------ AUC helpers
def auc_ci(D, pos, pos_p, neg, neg_p):
    rep = K.wauc(pos, neg, D.w(pos_p), D.w(neg_p))
    return K.auc(pos, neg), K.ci(rep), rep


def fold_auc(a):
    return max(a, 1 - a)

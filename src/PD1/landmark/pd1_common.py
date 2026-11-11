"""Signal isolation by paired differences (PD1), landmark family: shared paths, lists, folds and statistics.

Statistics re-implement the record's helpers exactly (checked against them in analyse.py --check):
  Draw  = a41_read.Draw (pigeonhole person bootstrap: persons ~ Multinomial(n, 1/n); one-person image weighs its
          host's count; two-person image the product of its two contributors' counts)
  wauc  = a36_read.wauc (weighted Mann-Whitney AUC, ties one half)
"""
import csv
import pathlib

import numpy as np

SEED = 20261111
B_BOOT = 2000
MC = pathlib.Path("/home/narolski/mambamorph-code")
REPO = pathlib.Path("/home/narolski/smad-next")
RES = REPO / "experiments/PD1_signal-isolation-paired-differences/landmark"
OUT = pathlib.Path("/mnt/t7/smad_next/PD1/landmark")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
AF0 = pathlib.Path("/mnt/t7/smad_next/AF0")
POOL = REPO / "experiments/AR1/pool.csv"
SMDD_ROOT = MC / "smadcvpr_data"
A47 = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3")
TOOLS = ("opencv", "facemorpher")
RUNGS = ("R0", "R2w", "R2wm", "R3m", "R3", "R4")
# rung names in the task's notation
XN = {"R0": "x0", "R2w": "x1", "R2wm": "x1m", "R3m": "xm", "R3": "x2", "R4": "x3"}
FEATS = ("clip_cls", "clip_mean", "dino_mean")


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def rows(path):
    return list(csv.DictReader(open(path)))


def write_rows(path, rr):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rr[0]))
        w.writeheader()
        w.writerows(rr)


# ------------------------------------------------------------------------------------------------ folds
def groups_and_folds(pool_rows, max_run=22, k=5, seed=SEED):
    """Groups = consecutive runs (<= max_run) along the cycles of the partner permutation; folds by greedy size balance
    over a seeded shuffle of the groups. Returns dict pid -> group id, dict pid -> fold."""
    Bp = {r["pid"]: r["B_pid"] for r in pool_rows}
    seen, groups = set(), []
    for p in sorted(Bp):
        if p in seen:
            continue
        cyc, q = [], p
        while q not in seen:
            seen.add(q)
            cyc.append(q)
            q = Bp[q]
        n = len(cyc)
        nrun = int(np.ceil(n / max_run))
        for j in range(nrun):                      # near-equal runs
            groups.append(cyc[j * n // nrun:(j + 1) * n // nrun])
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(groups))
    order = sorted(order, key=lambda i: -len(groups[i]))   # stable: big first, seeded tie order
    load = np.zeros(k)
    gid, fold = {}, {}
    for i in order:
        f = int(np.argmin(load))
        load[f] += len(groups[i])
        for p in groups[i]:
            gid[p], fold[p] = i, f
    return gid, fold


# ------------------------------------------------------------------------------------------------ statistics
class Draw:
    def __init__(self, pers, B=B_BOOT, seed=SEED):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)
        self.B = B

    def w(self, pp):
        """pp: list of (p,) or (p, q). Self-pairs and one-person tuples weigh the host count."""
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[-1]] for p in pp])
        W = self.C[:, a] * self.C[:, b]
        same = a == b
        if same.any():
            W[:, same] = self.C[:, a[same]]
        return W


def wauc(pos, neg, wp, wn):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    num = (wp * (below + 0.5 * tie)).sum(1)
    return num / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    return float(wauc(pos, neg, np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


def ci(rep, lo=2.5, hi=97.5):
    rep = np.asarray(rep, float)
    rep = rep[np.isfinite(rep)]
    return [float(x) for x in np.percentile(rep, [lo, hi])] if len(rep) else [None, None]


def cp_interval(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def flag_rate(untouched, softened, q=0.05):
    """threshold = the ceil(q n)-th highest untouched score; flagged = score >= threshold."""
    u = np.sort(np.asarray(untouched, float))[::-1]
    t = u[int(np.ceil(q * len(u))) - 1]
    s = np.asarray(softened, float)
    k = int((s >= t).sum())
    return dict(threshold=float(t), untouched_rate=float((u >= t).mean()), k=k, n=len(s), rate=k / len(s),
                ci=cp_interval(k, len(s)))


def eer(bona, morph):
    b, m = np.asarray(bona, float), np.asarray(morph, float)
    t = np.unique(np.concatenate([b, m]))
    fpr = np.array([(b >= x).mean() for x in t])
    fnr = np.array([(m < x).mean() for x in t])
    i = int(np.argmin(np.abs(fpr - fnr)))
    return float((fpr[i] + fnr[i]) / 2)

"""SM1 statistics: pigeonhole person bootstrap (a41_read.Draw, as re-implemented and checked in src/AD1/ad1_read.py),
weighted Mann-Whitney AUC (a36_read.wauc, same), weighted EER with the threshold rule of amendment A1.5."""
import numpy as np


class Draw:
    """B multinomial person-count draws; an image's weight = count(p1) * count(p2), or count(p) if p1 == p2."""

    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, p1, p2):
        a = np.array([self.pos[x] for x in p1])
        b = np.array([self.pos[x] for x in p2])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        w[:, same] = self.C[:, a[same]]
        return w


def wauc(pos, neg, wp, wn):
    """AUC(pos > neg) for each row of weights (B x n). Unit weights: pass np.ones((1, n))."""
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    return (wp * (below + 0.5 * tie)).sum(1) / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def weer(gen, mor, wg, wm):
    """Weighted EER (%) and threshold per row: thresholds t over the observed scores, flag = score >= t,
    FPR = weighted share of genuine flagged, FNR = weighted share of morphs not flagged; the t minimising |FPR - FNR|
    (first on ties); EER = (FPR + FNR) / 2 there. Returns (eer (B,), thr (B,))."""
    t = np.unique(np.concatenate([gen, mor]))
    og, om = np.argsort(gen), np.argsort(mor)
    gs, ms = gen[og], mor[om]
    ig = np.searchsorted(gs, t, "left")                     # genuine below t
    im = np.searchsorted(ms, t, "left")                     # morphs below t
    Cg = np.concatenate([np.zeros((wg.shape[0], 1)), np.cumsum(wg[:, og], 1)], 1)
    Cm = np.concatenate([np.zeros((wm.shape[0], 1)), np.cumsum(wm[:, om], 1)], 1)
    fpr = 1 - Cg[:, ig] / np.maximum(Cg[:, -1:], 1e-12)
    fnr = Cm[:, im] / np.maximum(Cm[:, -1:], 1e-12)
    j = np.argmin(np.abs(fpr - fnr), 1)
    r = np.arange(len(j))
    return 100 * (fpr[r, j] + fnr[r, j]) / 2, t[j]


def ci(x, q=(2.5, 97.5)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, q[0])), float(np.percentile(x, q[1]))] if len(x) else [np.nan, np.nan]


def eer_unit(gen, mor):
    e, t = weer(gen, mor, np.ones((1, len(gen))), np.ones((1, len(mor))))
    return float(e[0]), float(t[0])

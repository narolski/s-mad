"""Sealed MAD22 read (FINAL): the ONE metrics module for every detector (pinned by sha256 in the registration).
Convention: label 1 = morph (attack), higher score = more morph-like. A sample is FLAGGED (classified as morph) at
threshold t when score > t.
- ROC: thresholds at every distinct score; FPR = BPCER = weighted share of genuine scores >= threshold, TPR = weighted
  share of morph scores >= threshold, from (0, 0) to (1, 1). Tied scores move FPR and TPR together, so the linear
  segment between ROC points counts ties half.
- EER: the point on the piecewise-linear ROC where FPR = FNR (FNR = APCER = 1 - TPR), by linear interpolation.
- BPCER@APCER x: FPR on the piecewise-linear ROC where FNR = x (linear interpolation; if FNR = x on a vertical
  segment, the lowest FPR there).
- AUC: Mann-Whitney with ties counted half (equals the trapezoid area of the ROC).
- Rates at a fixed threshold t: APCER = share of morphs with score <= t; BPCER = share of genuine with score > t;
  exact Clopper-Pearson 95% intervals (unweighted counts).
All weighted functions take weights of shape (R, n) (bootstrap replicates) and return shape (R,)."""
import numpy as np
from scipy.stats import beta


def _roc_w(s, y, W):
    """s (n,), y (n,) in {0,1}, W (R, n) >= 0 -> FPR, FNR of shape (R, G+1) along descending distinct thresholds."""
    s = np.asarray(s, np.float64)
    y = np.asarray(y).astype(bool)
    W = np.atleast_2d(np.asarray(W, np.float64))
    o = np.argsort(-s, kind="stable")
    s, y, W = s[o], y[o], W[:, o]
    last = np.r_[s[1:] != s[:-1], True]                        # end of each group of equal scores
    cp = np.cumsum(W * y, 1)[:, last]
    cn = np.cumsum(W * ~y, 1)[:, last]
    P = np.maximum((W * y).sum(1, keepdims=True), 1e-300)
    N = np.maximum((W * ~y).sum(1, keepdims=True), 1e-300)
    z = np.zeros((W.shape[0], 1))
    tpr = np.c_[z, cp / P]
    fpr = np.c_[z, cn / N]
    return fpr, 1.0 - tpr


def eer_w(s, y, W):
    fpr, fnr = _roc_w(s, y, W)
    d = fpr - fnr                                              # -1 at the start, +1 at the end, non-decreasing
    k = np.argmax(d >= 0, 1)                                   # first index with d >= 0 (k >= 1 since d[0] = -1)
    r = np.arange(len(k))
    d0, d1 = d[r, k - 1], d[r, k]
    t = np.where(d1 > d0, -d0 / np.where(d1 > d0, d1 - d0, 1.0), 0.0)
    f0, f1 = fpr[r, k - 1], fpr[r, k]
    return f0 + t * (f1 - f0)


def bpcer_at_apcer_w(s, y, W, x):
    fpr, fnr = _roc_w(s, y, W)
    out = np.empty(fpr.shape[0])
    for i in range(fpr.shape[0]):
        a, b = fnr[i], fpr[i]                                  # fnr non-increasing from 1 to 0
        k = int(np.argmax(a <= x))                             # first point with FNR <= x
        if k == 0:
            out[i] = b[0]
            continue
        a0, a1, b0, b1 = a[k - 1], a[k], b[k - 1], b[k]
        out[i] = b0 + (b1 - b0) * ((a0 - x) / (a0 - a1)) if a0 > a1 else b1
    return out


def auc_w(s, y, W):
    s = np.asarray(s, np.float64)
    y = np.asarray(y).astype(bool)
    W = np.atleast_2d(np.asarray(W, np.float64))
    pos, neg, wp, wn = s[y], s[~y], W[:, y], W[:, ~y]
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.c_[np.zeros((W.shape[0], 1)), np.cumsum(wn[:, ob], 1)]
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    num = (wp * (below + 0.5 * tie)).sum(1)
    return num / np.maximum(wp.sum(1) * C[:, -1], 1e-300)


def ones(n):
    return np.ones((1, n))


def eer(s, y):
    return float(eer_w(s, y, ones(len(s)))[0])


def auc(s, y):
    return float(auc_w(s, y, ones(len(s)))[0])


def bpcer_at_apcer(s, y, x):
    return float(bpcer_at_apcer_w(s, y, ones(len(s)), x)[0])


def cp(k, n, a=0.05):
    if n == 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def rates(s, y, t):
    s = np.asarray(s, np.float64)
    y = np.asarray(y).astype(bool)
    ka, na = int((s[y] <= t).sum()), int(y.sum())
    kb, nb = int((s[~y] > t).sum()), int((~y).sum())
    return dict(apcer=ka / na if na else float("nan"), apcer_ci=cp(ka, na), n_morph=na,
                bpcer=kb / nb if nb else float("nan"), bpcer_ci=cp(kb, nb), n_genuine=nb)


def self_test():
    """known values: perfect, inverted, all ties, a hand-computed small case, weights = duplication."""
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    assert eer(np.r_[0, 1, 2, 3, 4, 5, 6, 7], y) == 0.0
    assert eer(np.r_[7, 6, 5, 4, 3, 2, 1, 0], y) == 1.0
    assert abs(eer(np.zeros(8), y) - 0.5) < 1e-12 and abs(auc(np.zeros(8), y) - 0.5) < 1e-12
    s = np.r_[0, 1, 2, 5, 3, 4, 6, 7]                         # one genuine (5) above two morphs (3, 4)
    assert abs(auc(s, y) - 14 / 16) < 1e-12
    assert abs(eer(s, y) - 0.25) < 1e-12, eer(s, y)
    w = np.array([[1, 2, 1, 1, 1, 1, 3, 1]], float)
    s2 = np.repeat(s, w[0].astype(int)); y2 = np.repeat(y, w[0].astype(int))
    assert abs(eer_w(s, y, w)[0] - eer(s2, y2)) < 1e-12
    assert abs(auc_w(s, y, w)[0] - auc(s2, y2)) < 1e-12
    for x in (0.0, 0.25, 0.5):
        assert abs(bpcer_at_apcer_w(s, y, w, x)[0] - bpcer_at_apcer(s2, y2, x)) < 1e-12
    assert abs(bpcer_at_apcer(s, y, 0.25) - 0.25) < 1e-12 and bpcer_at_apcer(s, y, 0.5) == 0.0
    r = rates(s, y, 4.5)
    assert r["apcer"] == 0.5 and r["bpcer"] == 0.25
    return True


if __name__ == "__main__":
    print("final_metrics self_test", self_test())

"""AR1 statistics, reusing the record's code: a41_read.Draw (pigeonhole two-way person bootstrap), a36_read.wauc
(weighted Mann-Whitney AUC), a41_read.dprime / ci; analyze.eer. Imported unchanged from the frozen A46 runtime."""
import numpy as np

import ar1_common as K

K.add_paths(K.MC, K.W46 / "smadcvpr")
import a41_read as M  # noqa: E402
import a36_read as R36  # noqa: E402
import analyze as A  # noqa: E402

Draw = M.Draw
dprime = M.dprime
ci = M.ci


def auc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    return float(R36.wauc(pos, neg, np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


def weights(D, pp):
    """single-person tuples (p,) -> host counts; pairs (p, q) -> product (a self-pair: the count), as Draw.wm."""
    if all(len(p) == 1 or p[0] == p[1] for p in pp):
        return D.wb([(p[0],) for p in pp])
    return D.wm([(p[0], p[1] if len(p) > 1 else p[0]) for p in pp])


def wauc_rep(D, pos, pos_p, neg, neg_p):
    return R36.wauc(np.asarray(pos, float), np.asarray(neg, float), weights(D, pos_p), weights(D, neg_p))


def wauc_ci(D, pos, pos_p, neg, neg_p, lo=2.5, hi=97.5):
    return auc(pos, neg), ci(wauc_rep(D, pos, pos_p, neg, neg_p), lo, hi)


def fold(a):
    return max(a, 1 - a)

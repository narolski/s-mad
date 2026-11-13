"""Standing adversary (ADV): the registered "exceeds its shortcut floor" rule for one network on one contrast
(experiments/ADV_shortcut-floors/prereg.md section 6). For arm owners' readers; reads only the committed floor files.

  from check import exceeds
  r = exceeds("lcomb", {row_id: logit, ...})   # every row id of floors/lcomb_heldout.csv must be scored
  r -> dict(arm_auc, floor_auc, diff, diff_lo, diff_hi, exceeds)

Rule: the floor's held-out scores (its registered model) and the network's scores are read on the same rows; 2,000
draws of person components with replacement (numpy default_rng(20261115)); the network exceeds the floor on this
contrast if the 2.5% bound of (network AUC - floor AUC), re-taken in the same draw, is above 0. An arm's gain counts
only on seeds where it exceeds (seed counting: the arm's own registered rule).
"""
import csv
import json
import pathlib

import numpy as np

FDIR = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors")


def _auc(s, y):
    from scipy.stats import rankdata
    p, n = int(y.sum()), int(len(y) - y.sum())
    r = rankdata(s)
    return float((r[y == 1].sum() - p * (p + 1) / 2) / (p * n))


def exceeds(contrast, scores, n_boot=2000, seed=20261115):
    rep = json.loads((FDIR / f"{contrast}.json").read_text())
    model = rep["floor"]["model"]
    R = list(csv.DictReader(open(FDIR / f"{contrast}_heldout.csv")))
    ids = [r["id"] for r in R]
    missing = [i for i in ids if i not in scores]
    assert not missing, f"{len(missing)} rows of {contrast} not scored"
    y = np.array([int(r["label"]) for r in R])
    g = np.array([int(r["component"]) for r in R])
    f = np.array([float(r[model]) for r in R])
    a = np.array([float(scores[i]) for i in ids])
    rng = np.random.default_rng(seed)
    ug = np.unique(g)
    idx = {k: np.where(g == k)[0] for k in ug}
    d = []
    for _ in range(n_boot):
        ii = np.concatenate([idx[k] for k in rng.choice(ug, len(ug), replace=True)])
        if 0 < y[ii].sum() < len(ii):
            d.append(_auc(a[ii], y[ii]) - _auc(f[ii], y[ii]))
    A, F = _auc(a, y), _auc(f, y)
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return dict(contrast=contrast, floor_model=model, arm_auc=A, floor_auc=F, diff=A - F, diff_lo=lo, diff_hi=hi,
                exceeds=bool(lo > 0))

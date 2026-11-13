"""Standing adversary (ADV): the registered "exceeds the ADV floor" rule for one network on one contrast
(experiments/ADV_shortcut-floors/prereg.md section 6 and amendment 2). For arm owners' readers; reads only committed,
pinned floor files. numpy only (no scipy needed on the cluster).

  from check import exceeds, diff_within_floor_quintiles
  r = exceeds("lcomb", {row_id: logit, ...})                  # the all-cue ADV floor
  r = exceeds("lcomb", {...}, floor="nuisance")               # the nuisance floor (border, resolution, storage, render)
  q = diff_within_floor_quintiles("lcomb", scores_a, scores_b) # arm difference within floor-score quintiles (printed)

Rule: the floor model's held-out scores and the network's scores on the same rows; 2,000 draws of person components
with replacement (numpy default_rng(20261115)); the network exceeds the floor if the 2.5% bound of (network AUC -
floor AUC), re-taken in the same draw, is above 0. The ADV floor is printed beside an arm's own registered floor and
never replaces it. Wording (internal record): within the all-cue floor but beyond the nuisance floor = "not beyond
hand-made morph statistics; not explained by nuisance cues".
"""
import csv
import hashlib
import json
import pathlib
import subprocess

import numpy as np

FDIR = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors")


def _rank(x):
    o = np.argsort(x, kind="mergesort")
    xs = x[o]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def _auc(s, y):
    p, n = int(y.sum()), int(len(y) - y.sum())
    r = _rank(np.asarray(s, float))
    return float((r[y == 1].sum() - p * (p + 1) / 2) / (p * n))


def _pinned(name):
    """sha256 of the file must appear in a committed floors/pins_stage*.sha256."""
    h = hashlib.sha256((FDIR / name).read_bytes()).hexdigest()
    for pf in sorted(FDIR.glob("pins_stage*.sha256")):
        tracked = subprocess.run(["git", "-C", str(FDIR), "ls-files", "--error-unmatch", pf.name],
                                 capture_output=True).returncode == 0
        clean = subprocess.run(["git", "-C", str(FDIR), "diff", "--quiet", "HEAD", "--", pf.name]).returncode == 0
        if tracked and clean and f"{h}  {name}" in pf.read_text().splitlines():
            return pf.name
    raise AssertionError(f"{name}: not in a committed pins file (sha256 {h[:16]})")


def _load(contrast, floor):
    pins = {p: _pinned(p) for p in (f"{contrast}.json", f"{contrast}_heldout.csv")}
    rep = json.loads((FDIR / f"{contrast}.json").read_text())
    assert rep.get("kind", "floor") == "floor", f"{contrast} is a separability ceiling: no exceeds rule"
    key = {"all": "floor", "nuisance": "nuisance_floor"}[floor]
    model = rep[key]["model"]
    col = model if floor == "all" else "nu_" + model
    R = list(csv.DictReader(open(FDIR / f"{contrast}_heldout.csv")))
    y = np.array([int(r["label"]) for r in R])
    g = np.array([int(r["component"]) for r in R])
    f = np.array([float(r[col]) for r in R])
    assert abs(_auc(f, y) - rep[key]["auc"]) < 1e-9, "held-out file does not reproduce the committed floor"
    return rep, key, model, [r["id"] for r in R], y, g, f, pins


def _scores(ids, scores, contrast):
    missing = [i for i in ids if i not in scores]
    assert not missing, f"{len(missing)} rows of {contrast} not scored"
    a = np.array([float(scores[i]) for i in ids])
    assert np.isfinite(a).all(), "non-finite network scores"
    return a


def exceeds(contrast, scores, floor="all", n_boot=2000, seed=20261115):
    rep, key, model, ids, y, g, f, pins = _load(contrast, floor)
    a = _scores(ids, scores, contrast)
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
    return dict(contrast=contrast, floor=floor, floor_model=model, arm_auc=A, floor_auc=F, diff=A - F, diff_lo=lo,
                diff_hi=hi, exceeds=bool(lo > 0), pinned_in=pins)


def diff_within_floor_quintiles(contrast, scores_a, scores_b, floor="all"):
    """Printed only (amendment 2 F7): AUC(a) - AUC(b) within quintiles of the floor's held-out score."""
    rep, key, model, ids, y, g, f, pins = _load(contrast, floor)
    a, b = _scores(ids, scores_a, contrast), _scores(ids, scores_b, contrast)
    q = np.searchsorted(np.quantile(f, [0.2, 0.4, 0.6, 0.8]), f, side="right")
    out = []
    for k in range(5):
        w = q == k
        if 0 < y[w].sum() < w.sum():
            out.append(dict(quintile=k, n=int(w.sum()), n_pos=int(y[w].sum()), diff=_auc(a[w], y[w]) - _auc(b[w], y[w])))
        else:
            out.append(dict(quintile=k, n=int(w.sum()), n_pos=int(y[w].sum()), diff=None))
    return dict(contrast=contrast, floor=floor, strata=out, pinned_in=pins)

"""Standing adversary (ADV): the registered "exceeds the ADV floor" rule for one network on one contrast
(experiments/ADV_shortcut-floors/prereg.md section 6 and amendment 2). For arm owners' readers; reads only committed,
pinned floor files. numpy only (no scipy needed on the cluster).

  from check import exceeds, diff_on_matched
  r = exceeds("lcomb", {row_id: logit, ...})                  # the all-cue ADV floor
  r = exceeds("lcomb", {...}, floor="nuisance")               # the nuisance floor (border, resolution, storage, render)
  q = diff_on_matched("lcomb", scores_a, scores_b)            # arm difference on floor-matched rows (printed)

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


def matched_rows(contrast, floor="all", caliper=0.1, seed=20261117):
    """Amendment 3 (replaces the quintile print, which was degenerate on lcomb): 1:1 greedy nearest-neighbour matching
    of positives to negatives on the logit of the floor's held-out score, without replacement, caliper 0.1 SD,
    positives in numpy default_rng(20261117) order. Returns the matched row ids (the floor is ~0.5 on them by
    construction)."""
    rep, key, model, ids, y, g, f, pins = _load(contrast, floor)
    z = np.log(np.clip(f, 1e-6, 1 - 1e-6) / (1 - np.clip(f, 1e-6, 1 - 1e-6))) if f.min() >= 0 and f.max() <= 1 else f
    sd = z.std() + 1e-12
    pos, neg = np.where(y == 1)[0], set(np.where(y == 0)[0].tolist())
    rng = np.random.default_rng(seed)
    keep = []
    for i in rng.permutation(pos):
        if not neg:
            break
        cand = np.array(sorted(neg))
        d = np.abs(z[cand] - z[i]) / sd
        j = int(np.argmin(d))
        if d[j] <= caliper:
            keep += [int(i), int(cand[j])]
            neg.discard(int(cand[j]))
    return [ids[k] for k in sorted(keep)], pins


def diff_on_matched(contrast, scores_a, scores_b, floor="all", n_boot=2000, seed=20261118):
    """Printed only: AUC(a) - AUC(b) on the floor-matched rows, person-component bootstrap interval."""
    rep, key, model, ids, y, g, f, pins = _load(contrast, floor)
    keep, _ = matched_rows(contrast, floor)
    ix = np.array([ids.index(i) for i in keep])
    a, b = _scores(keep, scores_a, contrast), _scores(keep, scores_b, contrast)
    yy, gg = y[ix], g[ix]
    rng = np.random.default_rng(seed)
    ug = np.unique(gg)
    idx = {k: np.where(gg == k)[0] for k in ug}
    d = []
    for _ in range(n_boot):
        ii = np.concatenate([idx[k] for k in rng.choice(ug, len(ug), replace=True)])
        if 0 < yy[ii].sum() < len(ii):
            d.append(_auc(a[ii], yy[ii]) - _auc(b[ii], yy[ii]))
    return dict(contrast=contrast, floor=floor, n_matched=len(keep), n_pos=int(yy.sum()),
                diff=_auc(a, yy) - _auc(b, yy), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                pinned_in=pins)

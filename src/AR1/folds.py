"""Strict person folds for every learned AR1 probe / baseline (reviewers, PLANNING_RECORD section 15 item 7: folds must
hold out BOTH persons of a morph). Persons are grouped into units that never split: in the primary and FRLL pools the
cycles of the host -> B assignment (a morph (H_p, S_q) and the twin (H_q, S_q) share the photo S_q, so p and q must sit
in the same fold; a permutation's cycles close this chain). Units are dealt to 5 folds greedily by person count
(largest first, seeded tie order). For pair sets whose persons do not follow the assignment (the FRLL bridge pairs),
an image is tested in fold k only if all its persons are in fold k and trained on only if none is; images that
straddle folds get no out-of-fold score (NaN) and are counted.
"""
import csv
import random

import numpy as np

import ar1_common as K

_CACHE = {}


def person_fold_map(nfold=5, seed=20261113):
    if nfold in _CACHE:
        return _CACHE[nfold]
    fmap = {}
    for pcsv in (K.OUT / "pool.csv", K.OUT / "pool_frll.csv"):      # each pool dealt to its own 5 folds
        units = []
        rows = list(csv.DictReader(open(pcsv)))
        nxt = {r["pid"]: r["B_pid"] for r in rows}
        seen = set()
        for p in sorted(nxt):
            if p in seen:
                continue
            cyc, q = [], p
            while q not in seen:
                seen.add(q)
                cyc.append(q)
                q = nxt[q]
            units.append(cyc)
        rng = random.Random(seed)
        rng.shuffle(units)
        units.sort(key=len, reverse=True)
        load = [0] * nfold
        for u in units:
            k = int(np.argmin(load))
            for p in u:
                fmap[p] = k
            load[k] += len(u)
    _CACHE[nfold] = fmap
    return fmap


def oof_strict(X, y, persons, make_model, nfold=5):
    """persons: list of tuples of person ids per image. -> (scores with NaN where untested, n_untested)."""
    fmap = person_fold_map(nfold)
    F = [set(fmap[p] for p in pp) for pp in persons]
    s = np.full(len(y), np.nan)
    for k in range(nfold):
        te = np.array([f == {k} for f in F])
        tr = np.array([k not in f for f in F])
        if te.sum() == 0 or len(set(y[tr])) < 2:
            continue
        m = make_model()
        m.fit(X[tr], y[tr])
        s[te] = m.decision_function(X[te])
    return s, int(np.isnan(s).sum())

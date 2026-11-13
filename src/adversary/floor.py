"""Standing adversary (ADV): the strongest shortcut-only model on the rows of one contrast, cross-fitted by person.

Given rows (id, label 1 = the side the arm should score higher, person keys) and their shortcut features
(src/adversary/feats.py), fits three shortcut-only models and reports cross-fitted AUC / EER with a person-cluster
bootstrap interval:
  single  best single statistic: on each training fold the statistic and sign with the highest training AUC; its
          held-out values are mapped through the training fold's empirical CDF so folds pool on one scale;
  logreg  StandardScaler + LogisticRegression(C = 1, class_weight balanced, max_iter 3000) on all features;
  gbt     HistGradientBoostingClassifier(max_iter 200, learning_rate 0.05, max_leaf_nodes 15, min_samples_leaf 20,
          l2_regularization 1.0, class_weight balanced, early_stopping off, random_state 0) on all features.
Folds: StratifiedGroupKFold(5, shuffle, random_state 20261113) over connected person components (a two-person
morph links its two persons, so no identity is on both sides of a split). Bootstrap: 2,000 draws of person
components with replacement, numpy default_rng(20261114). Missing / infinite feature values: training-fold median.
Also printed: the in-sample best single statistic (the convention of src/PN1/fs_read.py fmax: max over statistics of
max(AUC, 1 - AUC) on all rows; optimistic), per-family models (which family carries the floor) and
leave-one-family-out drops. floor = the highest of the three cross-fitted AUCs (its model named).
No network score is read here.
"""
import numpy as np

SPLIT_SEED = 20261113
BOOT_SEED = 20261114
N_BOOT = 2000


def auc(s, y):
    from scipy.stats import rankdata
    s = np.asarray(s, float)
    y = np.asarray(y, int)
    p, n = int(y.sum()), int(len(y) - y.sum())
    if p == 0 or n == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y == 1].sum() - p * (p + 1) / 2) / (p * n))


def eer(s, y):
    s = np.asarray(s, float)
    y = np.asarray(y, int)
    t = np.unique(s)
    if len(t) > 400:
        t = np.quantile(s, np.linspace(0, 1, 401))
    best = (2.0, 0.0)
    P, Nn = s[y == 1], s[y == 0]
    for th in t:
        fr = np.mean(P < th)          # attacks missed
        fa = np.mean(Nn >= th)        # negatives flagged
        if abs(fr - fa) < best[0]:
            best = (abs(fr - fa), (fr + fa) / 2)
    return float(best[1])


def components(persons):
    """persons: list of tuples of person keys -> component id per row (union-find)."""
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for ps in persons:
        ps = list(ps)
        for q in ps[1:]:
            ra, rb = find(ps[0]), find(q)
            if ra != rb:
                parent[rb] = ra
        find(ps[0])
    roots = {}
    return np.array([roots.setdefault(find(list(ps)[0]), len(roots)) for ps in persons])


def _clean(Xtr, Xte):
    Xtr = np.array(Xtr, float)
    Xte = np.array(Xte, float)
    Xtr[~np.isfinite(Xtr)] = np.nan
    Xte[~np.isfinite(Xte)] = np.nan
    med = np.nanmedian(Xtr, 0)
    med[~np.isfinite(med)] = 0.0
    for X in (Xtr, Xte):
        i = np.where(np.isnan(X))
        X[i] = med[i[1]]
    sd = Xtr.std(0)
    keep = sd > 0
    return Xtr[:, keep], Xte[:, keep], keep


def _single(Xtr, ytr, Xte):
    best = (-1.0, 0, 1)
    for j in range(Xtr.shape[1]):
        a = auc(Xtr[:, j], ytr)
        if not np.isfinite(a):
            continue
        for sgn, v in ((1, a), (-1, 1 - a)):
            if v > best[0]:
                best = (v, j, sgn)
    _, j, sgn = best
    tr = np.sort(sgn * Xtr[:, j])
    return np.searchsorted(tr, sgn * Xte[:, j], side="right") / len(tr), j, sgn


def _model(kind):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    if kind == "logreg":
        return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced"))
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
                                          l2_regularization=1.0, class_weight="balanced", early_stopping=False,
                                          random_state=0)


def folds(y, groups, k=5):
    from sklearn.model_selection import StratifiedGroupKFold
    ng = len(np.unique(groups))
    k = min(k, ng, int(y.sum()), int(len(y) - y.sum()))
    sgk = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=SPLIT_SEED)
    return list(sgk.split(np.zeros(len(y)), y, groups))


def crossfit(X, y, groups, kind, fl=None, names=None):
    """-> held-out score per row, and (for single) the chosen statistic per fold."""
    fl = fl or folds(y, groups)
    s = np.full(len(y), np.nan)
    chosen = []
    for tr, te in fl:
        Xtr, Xte, keep = _clean(X[tr], X[te])
        if Xtr.shape[1] == 0 or len(np.unique(y[tr])) < 2:        # pre-run check F9: nothing to fit on
            s[te] = 0.5
            chosen.append("none")
            continue
        if kind == "single":
            s[te], j, sgn = _single(Xtr, y[tr], Xte)
            nm = np.array(names)[keep][j] if names is not None else int(j)
            chosen.append(("-" if sgn < 0 else "+") + str(nm))
        else:
            m = _model(kind).fit(Xtr, y[tr])
            s[te] = m.predict_proba(Xte)[:, 1]
    return s, chosen


def boot(s, y, groups, n=N_BOOT, seed=BOOT_SEED):
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    idx = {g: np.where(groups == g)[0] for g in ug}
    out = []
    for _ in range(n):
        pick = rng.choice(ug, len(ug), replace=True)
        ii = np.concatenate([idx[g] for g in pick])
        a = auc(s[ii], y[ii])
        if np.isfinite(a):
            out.append(a)
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def insample_single(X, y, names):
    v = []
    for j in range(X.shape[1]):
        x = X[:, j]
        ok = np.isfinite(x)
        a = auc(x[ok], y[ok]) if ok.sum() > 2 else float("nan")
        v.append(max(a, 1 - a) if np.isfinite(a) else -1)
    j = int(np.argmax(v))
    return float(v[j]), names[j]


def fit_contrast(X, y, persons, names, families=("F27", "BORDER", "RES", "STORE", "RENDER", "BLEND"), detail=True):
    """Full adversary report for one contrast. X rows align with y and persons."""
    y = np.asarray(y, int)
    groups = components(persons)
    fl = folds(y, groups)
    names = list(names)
    rep = dict(n_pos=int(y.sum()), n_neg=int(len(y) - y.sum()), n_components=int(len(np.unique(groups))),
               n_folds=len(fl))
    rep["insample_best_single"], rep["insample_best_single_stat"] = insample_single(X, y, names)
    f27 = [i for i, n in enumerate(names) if n.startswith("F27:")]
    if f27:
        rep["insample_best_single_f27"], rep["insample_best_single_f27_stat"] = insample_single(X[:, f27], y,
                                                                                                [names[i] for i in f27])
    scores = {}
    for kind in ("single", "logreg", "gbt"):
        s, ch = crossfit(X, y, groups, kind, fl, names)
        scores[kind] = s
        rep[kind] = dict(auc=auc(s, y), eer=eer(s, y), ci=boot(s, y, groups))
        if ch:
            rep[kind]["chosen_per_fold"] = ch
    # the 27 statistics alone (continuity with the reviewed floors)
    if f27:
        s, _ = crossfit(X[:, f27], y, groups, "logreg", fl)
        rep["logreg_f27"] = dict(auc=auc(s, y), ci=boot(s, y, groups))
    best = max(("single", "logreg", "gbt"), key=lambda k: rep[k]["auc"])
    rep["floor"] = dict(model=best, auc=rep[best]["auc"], eer=rep[best]["eer"], ci=rep[best]["ci"])
    if detail:
        fam = {}
        for f in families:
            cols = [i for i, n in enumerate(names) if n.startswith(f + ":")]
            s1, _ = crossfit(X[:, cols], y, groups, "gbt", fl)
            s2, _ = crossfit(X[:, cols], y, groups, "logreg", fl)
            fam[f] = dict(gbt=auc(s1, y), logreg=auc(s2, y))
        rep["family_alone"] = fam
        rep["carrying_family"] = max(fam, key=lambda f: max(fam[f].values()))
        loo = {}
        for f in families:
            cols = [i for i, n in enumerate(names) if not n.startswith(f + ":")]
            s1, _ = crossfit(X[:, cols], y, groups, best if best != "single" else "gbt", fl,
                             [names[i] for i in cols])
            loo[f] = auc(s1, y)
        rep["leave_family_out"] = loo
    return rep, scores, groups

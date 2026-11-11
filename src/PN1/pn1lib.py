"""PN1 shared code: the catalogue of every image PN1 reads (class, role, persons, rung, tool, strength), feature lookup,
heads and statistics. Classes follow prereg.md section 0: genuine (camera photo and its stored copies), attack
(two-person morph and its stored copies), single (single-subject: warp-only, halves, same-person, mirror, their copies).
"""
import csv
import hashlib
import json
import pathlib

import numpy as np

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests")
AF0 = pathlib.Path("/mnt/t7/smad_next/AF0")
PD1D = pathlib.Path("/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512")
SPLIT = RES / "split"
BACKBONES = ("clip224", "dinov3_512")
FORBID = ("fst", "valx", "a12sp", "a12-sp")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def read(p):
    return list(csv.DictReader(open(p)))


def split_tables():
    lad = {r["pid"]: r for r in read(SPLIT / "ladder_split.csv")}
    af = {r["pid"]: r for r in read(SPLIT / "af0_split.csv")}
    return lad, af


def _strength(rung):
    if rung.endswith("fm61"):
        return "61"
    if rung.endswith("amsl112"):
        return "112"
    return ""


def _base(rung):
    return rung.split("_soft_")[0]


AF0_CLASS = {"photo": "genuine", "u50": "attack", "zero": "single", "halfA": "single", "halfB": "single"}
LAD_CLASS = {"R0": "genuine", "R4": "attack", "R2w": "single", "R2w4": "single", "R3": "single", "R3m": "single",
             "R2": None, "NC": None, "R2wm": "single"}


def catalog(include_missing_lists=True):
    """-> list of row dicts with: id, path, src, fam (af0 | ladder | bench | h1), klass, rung (base rung), strength
    ('' | '61' | '112'), tool, host (bootstrap unit), persons (tuple), role (train | dev | test | bench | h1 | excluded),
    cell (benchmark cell or ''), neutral (FRLL genuine: True for _03 files)."""
    lad, af = split_tables()
    man = {r["id"]: r for r in read(AF0 / "manifest.csv")}
    out = []

    def af_role(cell, persons):
        uses = {af.get(p, {}).get("pn1_use", "none") for p in persons}
        if cell == "train" and uses == {"train"}:
            return "train"
        if cell == "val" and uses == {"dev"}:
            return "dev"
        return "excluded"

    def lad_role(host, persons):
        r = lad[host]
        if any(lad[p]["is_val"] == "1" for p in persons if p in lad):
            return "excluded"
        if r["role"] == "test":
            return "test" if r["test_read"] == "1" else "excluded"
        return r["role"]                       # dev | train | excluded

    def add_af0(r, src):
        base = _base(r["rung"])
        if base not in AF0_CLASS:
            return
        mid = r["id"].split("_half")[0] if base.startswith("half") else r["id"].split("_fm61")[0].split("_amsl112")[0]
        m = man.get(mid)
        persons = (m["pid_A"], m["pid_B"]) if m and m["kind"] == "morph" else (r["p1"],)
        if base == "photo":
            persons = (r["p1"],)
        out.append(dict(id=r["id"], path=r["path"], src=src, fam="af0", klass=AF0_CLASS[base], rung=base,
                        strength=_strength(r["rung"]), tool="af0engine" if base != "photo" else "none",
                        pool="af0_" + r["tool"], host=persons[0], persons=tuple(sorted(set(persons))),
                        role=af_role(r["cell"], persons), cell="", neutral=None, pair=mid,
                        field=(m["field"] if m and m["kind"] == "morph" else base)))

    for n in ("af0_w1", "af0_w2", "af0_h"):
        for r in read(AF0 / "lists" / f"{n}.csv"):
            add_af0(r, n)
    for n, d in (("soft", AF0 / "lists" / "soft.csv"), ("devsoft", PN1 / "lists" / "devsoft.csv")):
        if d.exists():
            for r in read(d):
                if r["set"] in ("af0", "devsoft") and r["id"].startswith(("train_", "val_")):
                    add_af0(r, n)

    def add_lad(r, src):
        if r["cell"] != "frgcferet":
            return
        base = _base(r["rung"])
        k = LAD_CLASS.get(base)
        if k is None:
            return
        host = r["p1"]
        persons = (host, lad[host]["partner_B"]) if base == "R4" else (host,)
        out.append(dict(id=r["id"], path=r["path"], src=src, fam="ladder", klass=k, rung=base,
                        strength=_strength(r["rung"]), tool=r["tool"], pool="ladder_" + host.split(":")[0],
                        host=host, persons=tuple(sorted(set(persons))), role=lad_role(host, persons), cell="",
                        neutral=None, pair=host, field=""))

    for n, d in (("ar1", AF0 / "lists" / "ar1.csv"), ("ar1soft", AF0 / "lists" / "ar1soft.csv"),
                 ("r2w4", PN1 / "lists" / "r2w4.csv"), ("ladsoft", PN1 / "lists" / "ladsoft.csv"),
                 ("devsoft", PN1 / "lists" / "devsoft.csv")):
        if d.exists():
            for r in read(d):
                if r["id"].startswith("ar1_"):
                    add_lad(r, n)

    for n, d in (("bench_s", AF0 / "lists" / "bench_s.csv"), ("frll_e5", PN1 / "lists" / "frll_e5.csv")):
        for r in read(d):
            cell, rung = r["cell"], r["rung"]
            if rung == "morph":
                k = "attack"
            else:
                k = "genuine"
            neutral = None
            if k == "genuine" and cell.startswith("frllm"):
                neutral = pathlib.Path(r["path"]).name.split("_")[1] == "03"
            out.append(dict(id=r["id"], path=r["path"], src=n, fam="bench", klass=k, rung=rung, strength="",
                            tool=r["tool"], pool=cell.split("_")[0], host=r["p1"],
                            persons=tuple(sorted({r["p1"], r["p2"]})), role="bench", cell=cell, neutral=neutral,
                            pair=r["p1"], field=""))
    for r in read(AF0 / "lists" / "h1.csv"):
        out.append(dict(id=r["id"], path=r["path"], src="h1", fam="h1", klass="attack" if r["rung"] == "morph"
                        else "genuine", rung=r["rung"], strength="", tool="poisson", pool="casia", host=r["p1"],
                        persons=tuple(sorted({r["p1"], r["p2"]})), role="h1", cell="h1poisson", neutral=None,
                        pair=r["p1"], field=""))
    ids = [r["id"] for r in out]
    assert len(ids) == len(set(ids)), "duplicate ids in the catalogue"
    for r in out:
        assert not any(f in r["path"].lower() for f in FORBID), r["path"]
    return out


# ------------------------------------------------------------------ features
def feature_files(bb):
    """[(path_ids, path_mean)] in priority order (first hit wins; later duplicates are compared, not used)."""
    fs = []
    d = PN1 / "feat" / bb
    if d.exists():
        for f in sorted(d.glob("*.mean.npy")):
            if "_limit" in f.name:
                continue
            fs.append((f.with_name(f.name.replace(".mean.npy", ".ids.npy")), f))
    if bb == "dinov3_512":
        for f in sorted(PD1D.glob("af0_*_mean.npz")):
            fs.append((f, f))
    return fs


def load_features(bb, want=None, check_dupes=True):
    """-> (dict id -> row index, matrix, report of duplicate checks)."""
    idx, mats, rep = {}, [], {}
    off = 0
    for fi, fm in feature_files(bb):
        if fm.suffix == ".npz":
            z = np.load(fm)
            ids, M = z["ids"], z["mean"]
        else:
            ids, M = np.load(fi), np.load(fm)
        assert len(ids) == len(M)
        keep_rows, dup = [], []
        for i, x in enumerate(ids):
            x = str(x)
            if want is not None and x not in want:
                continue
            if x in idx:
                dup.append((x, i))
                continue
            keep_rows.append(i)
            idx[x] = off + len(keep_rows) - 1
        if keep_rows:
            mats.append(np.asarray(M[keep_rows], np.float32))
            off += len(keep_rows)
        if dup and check_dupes:
            allm = np.concatenate(mats)
            d = [float(np.abs(allm[idx[x]] - M[i]).max()) for x, i in dup[:2000]]
            rep[str(fm)] = dict(n_dup=len(dup), max_abs_diff=max(d), median_abs_diff=float(np.median(d)))
    return idx, (np.concatenate(mats) if mats else np.zeros((0, 1024), np.float32)), rep


# ------------------------------------------------------------------ heads
def fit_head(X, y, groups, seed, Cs=(0.001, 0.01, 0.1, 1.0, 10.0), folds=5):
    """StandardScaler + LogisticRegression (L2, lbfgs, balanced classes); C by grouped inner CV (AUC), refit on all."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    g = np.asarray(groups)
    ug = np.unique(g)
    rng = np.random.default_rng(seed)
    fold_of = dict(zip(rng.permutation(ug), np.arange(len(ug)) % folds))
    f = np.array([fold_of[x] for x in g])
    best, cv = None, {}
    for C in Cs:
        aucs = []
        for k in range(folds):
            tr, te = f != k, f == k
            if len(np.unique(y[te])) < 2:
                continue
            sc = StandardScaler().fit(X[tr])
            m = LogisticRegression(C=C, max_iter=5000, class_weight="balanced").fit(sc.transform(X[tr]), y[tr])
            aucs.append(auc(m.decision_function(sc.transform(X[te]))[y[te] == 1],
                            m.decision_function(sc.transform(X[te]))[y[te] == 0]))
        cv[C] = float(np.mean(aucs))
        if best is None or cv[C] > cv[best]:
            best = C
    sc = StandardScaler().fit(X)
    m = LogisticRegression(C=best, max_iter=5000, class_weight="balanced").fit(sc.transform(X), y)
    return dict(scaler=sc, model=m, C=best, cv=cv)


def head_score(h, X):
    return h["model"].decision_function(h["scaler"].transform(X))


# ------------------------------------------------------------------ statistics
def auc(pos, neg):
    """signed AUC, pos above neg, ties one half."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    s = np.concatenate([pos, neg])
    from scipy.stats import rankdata
    r = rankdata(s)
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cmp_matrix(pos, neg):
    pos, neg = np.asarray(pos, float)[:, None], np.asarray(neg, float)[None, :]
    return (pos > neg).astype(np.float32) + 0.5 * (pos == neg)


def boot_weights(units, B, seed):
    """host bootstrap: (B, n_units) counts, and the unit list."""
    u = sorted(set(units))
    rng = np.random.default_rng(seed)
    return rng.multinomial(len(u), np.full(len(u), 1 / len(u)), size=B).astype(np.float32), u


def wauc_draws(M, wp, wn):
    """weighted AUCs for B draws: M (np, nn) comparison matrix, wp (B, np), wn (B, nn)."""
    num = np.einsum("bi,ij,bj->b", wp, M, wn)
    den = wp.sum(1) * wn.sum(1)
    return num / np.maximum(den, 1e-12)


def paired_auc_ci(pos, neg, pos_units, neg_units, B=2000, seed=20261111, extra=None):
    """AUC with a host bootstrap (draws over the union of units, applied to both sides). extra: dict name ->
    (pos_stat, neg_stat) arrays whose folded AUCs are maxed per draw for the excess. Returns dict."""
    w, u = boot_weights(list(pos_units) + list(neg_units), B, seed)
    ui = {x: i for i, x in enumerate(u)}
    ip = np.array([ui[x] for x in pos_units])
    ineg = np.array([ui[x] for x in neg_units])
    wp, wn = w[:, ip], w[:, ineg]
    M = cmp_matrix(pos, neg)
    a = auc(pos, neg)
    d = wauc_draws(M, wp, wn)
    res = dict(auc=a, lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)), n_pos=len(pos),
               n_neg=len(neg), n_units=len(u))
    if extra:
        best_pt, best_name, best_draws = -1, None, None
        stat_draws = []
        for name, (sp, sn) in extra.items():
            ok_p, ok_n = np.isfinite(sp), np.isfinite(sn)
            Ms = cmp_matrix(np.where(ok_p, sp, 0), np.where(ok_n, sn, 0))
            ds = wauc_draws(Ms, wp, wn)
            ds = np.maximum(ds, 1 - ds)
            pt = auc(sp, sn)
            pt = max(pt, 1 - pt)
            stat_draws.append(ds)
            if pt > best_pt:
                best_pt, best_name = pt, name
        S = np.max(np.stack(stat_draws), 0)
        ex = d - S
        res.update(best_stat=best_name, best_stat_auc=best_pt, excess=a - best_pt,
                   excess_lo=float(np.percentile(ex, 2.5)), excess_hi=float(np.percentile(ex, 97.5)))
    return res


def unpaired_auc_ci(pos, neg, B=1000, seed=20261111):
    rng = np.random.default_rng(seed)
    pos, neg = np.asarray(pos), np.asarray(neg)
    d = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return dict(auc=auc(pos, neg), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)),
                n_pos=len(pos), n_neg=len(neg))


def eer(pos, neg):
    """equal error rate (%): attacks pos (higher = attack). Threshold sweep over all scores; at each candidate
    threshold t: FA = share(neg > t)... computed as the point where FA and miss cross, linearly interpolated."""
    pos, neg = np.sort(np.asarray(pos, float)), np.sort(np.asarray(neg, float))
    ts = np.unique(np.concatenate([pos, neg, [-np.inf]]))
    fa = 1 - np.searchsorted(neg, ts, side="right") / len(neg)      # share of genuine above t
    mi = np.searchsorted(pos, ts, side="right") / len(pos)          # share of attacks at or below t
    d = fa - mi
    k = int(np.argmax(d <= 0)) if (d <= 0).any() else len(ts) - 1
    if k == 0:
        return float(100 * (fa[0] + mi[0]) / 2)
    d0, d1 = d[k - 1], d[k]
    lam = d0 / (d0 - d1) if d0 != d1 else 0.5
    return float(100 * ((fa[k - 1] + lam * (fa[k] - fa[k - 1])) + (mi[k - 1] + lam * (mi[k] - mi[k - 1]))) / 2)


def eer_ci(pos, neg, B=1000, seed=20261111):
    rng = np.random.default_rng(seed)
    pos, neg = np.asarray(pos), np.asarray(neg)
    d = [eer(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(B)]
    return dict(eer=eer(pos, neg), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)))


def thr_at(scores, alpha=0.05):
    """the smallest score t of the pool with share(score > t) <= alpha (EV1's rule); flag = score > t."""
    s = np.sort(np.asarray(scores, float))
    n = len(s)
    for t in np.unique(s):
        if (n - np.searchsorted(s, t, side="right")) / n <= alpha:
            return float(t)
    return float(s[-1])


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def rate(mask):
    k, n = int(np.sum(mask)), int(len(mask))
    lo, hi = cp(k, n) if n else (float("nan"), float("nan"))
    return dict(rate=k / n if n else float("nan"), k=k, n=n, lo=lo, hi=hi)


def dump(obj, path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    json.dump(obj, open(path, "w"), indent=1, default=conv)

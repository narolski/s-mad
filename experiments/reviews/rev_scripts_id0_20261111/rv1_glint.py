"""Reviewer check (post hoc, unregistered, descriptive), glintr100 arm. (1) ISS and the registered virtual head on
virtual normalised midpoints of the AR1 pool's own source embeddings, next to the real built images. (2) Is the
in-domain 'ceiling' a ceiling: learning curve over fit persons, regulariser, and a small non-linear head.
Point estimates, plain Mann-Whitney AUC."""
import collections
import itertools
import sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/ID0")
import analyse as A  # noqa
from iss import ISS, auc_fast  # noqa
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

keys, X, found, meta, fk, fp = A.image_features("glint")
idx = {k: i for i, k in enumerate(keys)}
Xfit = X[[idx[k] for k in fk]]
M = ISS(Xfit, fp, kmax=64)
meta = {k: v for k, v in meta.items() if k in idx and found[idx[k]]}


def grp(g):
    return [k for k, m in meta.items() if m["group"] == g and not (A.valbad(m["p1"]) or A.valbad(m["p2"]))]


def vec(k):
    return X[idx[k]]


def nrm(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


# ---- registered virtual head, rebuilt exactly as analyse.geo0 does
g = collections.defaultdict(list)
for i, p in enumerate(fp):
    g[p].append(i)
pers = sorted(g)
rng = np.random.default_rng(20261111)
rng.shuffle(pers)
fold = {p: i % 5 for i, p in enumerate(pers)}
fpa = np.array(fp)
db = np.array([p.split(":")[0] for p in fp])
items = []
for f in range(5):
    ix = np.where([fold[p] == f for p in fp])[0]
    for i in ix:
        items.append((f, Xfit[i], 0, "single", np.nan))
    for p in [p for p in pers if fold[p] == f]:
        for a, b in itertools.combinations(g[p], 2):
            v = Xfit[a] + Xfit[b]
            items.append((f, v / np.linalg.norm(v), 0, "twin", float(Xfit[a] @ Xfit[b])))
    n = 0
    while n < 4000:
        a, b = rng.choice(ix, 2)
        if fpa[a] == fpa[b] or db[a] != db[b]:
            continue
        v = Xfit[a] + Xfit[b]
        items.append((f, v / np.linalg.norm(v), 1, "morph", float(Xfit[a] @ Xfit[b])))
        n += 1
F = np.array([t[0] for t in items]); V = np.array([t[1] for t in items]); Y = np.array([t[2] for t in items])
K = np.array([t[3] for t in items])
scal = StandardScaler().fit(V)
head = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(scal.transform(V), Y)
hs = lambda Z: head.decision_function(scal.transform(np.asarray(Z)))  # noqa
iss = lambda Z: M.scores(np.asarray(Z))["iss"]  # noqa
u = Xfit.mean(0); u = u / np.linalg.norm(u)

R4 = grp("ar1_frgcferet_opencv_R4"); R4f = grp("ar1_frgcferet_facemorpher_R4")
H = grp("ar1src_frgcferet_H"); R2w = grp("ar1_frgcferet_opencv_R2w"); R3 = grp("ar1_frgcferet_opencv_R3")
print("n", len(R4), len(H), len(R2w), len(R3))
real4 = np.array([vec(k) for k in R4]); real4f = np.array([vec(k) for k in R4f])
virt4 = nrm(np.array([vec(meta[k]["src1"]) + vec(meta[k]["src2"]) for k in R4]))
virt3 = nrm(np.array([vec(meta[k]["src1"]) + vec(meta[k]["src2"]) for k in R3]))
eH = np.array([vec(k) for k in H]); e2w = np.array([vec(k) for k in R2w]); e3 = np.array([vec(k) for k in R3])
for nm, fn in (("ISS", iss), ("virtual head", hs), ("mean-direction projection", lambda Z: np.asarray(Z) @ u)):
    print(f"[{nm}]")
    for lab, neg in (("host photo", eH), ("R2w", e2w), ("R3 real", e3), ("virtual twin H+S", virt3)):
        print(f"   {lab:18s} vs real OpenCV R4 {auc_fast(fn(real4), fn(neg)):.3f} | vs real FaceMorpher R4 {auc_fast(fn(real4f), fn(neg)):.3f}"
              f" | vs VIRTUAL midpoint of the same pairs {auc_fast(fn(virt4), fn(neg)):.3f}")
print("fidelity check: median cos(real R4, virtual R4)", float(np.median((real4 * virt4).sum(1))))
# share of the virtual shift realised, paired on host, in head units
sh = hs(np.array([vec(meta[k]["src1"]) for k in R4]))
print("head: paired median shift vs host: real %.3f virtual %.3f ; SD host %.3f" % (np.median(hs(real4) - sh), np.median(hs(virt4) - sh), sh.std()))

# ---- (2) is 0.744 a ceiling? hold out fold 0, vary training persons / C / model
te = F == 0
Vte, Yte, Kte = V[te], Y[te], K[te]
trp = [p for p in pers if fold[p] != 0]
r2 = np.random.default_rng(7)


def build(ps, nm=16000):
    ps = set(ps)
    ix = np.array([i for i, p in enumerate(fp) if p in ps])
    its, lab = [Xfit[i] for i in ix], [0] * len(ix)
    for p in ps:
        for a, b in itertools.combinations(g[p], 2):
            its.append(nrm(Xfit[a] + Xfit[b])); lab.append(0)
    n = 0
    while n < nm:
        a, b = r2.choice(ix, 2)
        if fpa[a] == fpa[b] or db[a] != db[b]:
            continue
        its.append(nrm(Xfit[a] + Xfit[b])); lab.append(1); n += 1
    return np.array(its), np.array(lab)


def ev(model, sc_):
    s = model.decision_function(sc_.transform(Vte)) if hasattr(model, "decision_function") else model.predict_proba(sc_.transform(Vte))[:, 1]
    return auc_fast(s[Yte == 1], s[Kte == "single"]), auc_fast(s[Yte == 1], s[Yte == 0])


print("held-out fold 0: test persons", sum(1 for p in pers if fold[p] == 0), "items", collections.Counter(Kte.tolist()))
for N in (75, 150, 300, len(trp)):
    Xt, Yt = build(trp[:N])
    s_ = StandardScaler().fit(Xt)
    m = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(s_.transform(Xt), Yt)
    print(f"  linear head, {N:4d} training persons: morph vs single {ev(m, s_)[0]:.3f}, vs single+twin {ev(m, s_)[1]:.3f}")
Xt, Yt = build(trp)
s_ = StandardScaler().fit(Xt)
for Cc in (0.001, 0.01, 0.1, 10.0):
    m = LogisticRegression(C=Cc, class_weight="balanced", max_iter=3000).fit(s_.transform(Xt), Yt)
    print(f"  linear head, all persons, C={Cc}: morph vs single {ev(m, s_)[0]:.3f}")
# first-moment statistic alone (projection on the fit mean direction), no fit beyond the mean
print("  mean-direction projection alone on the held-out fold: %.3f" % auc_fast(Vte[Yte == 1] @ u, Vte[Kte == "single"] @ u))
from sklearn.neural_network import MLPClassifier
m = MLPClassifier(hidden_layer_sizes=(256,), alpha=1e-2, max_iter=60, early_stopping=True, random_state=0).fit(s_.transform(Xt), Yt)
print(f"  MLP(256) head, all persons: morph vs single {ev(m, s_)[0]:.3f}, vs single+twin {ev(m, s_)[1]:.3f}")

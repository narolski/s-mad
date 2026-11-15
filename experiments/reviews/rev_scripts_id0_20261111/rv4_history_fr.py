"""Reviewer check (post hoc, unregistered, descriptive): paired storage-history shift of FR-embedding read-outs
(registered virtual head rebuilt as in analyse.geo0; projection on the fit mean direction) on FRLL photos,
native vs each E7 family. Existing embeddings only."""
import collections, itertools, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/ID0")
import analyse as A  # noqa
from iss import auc_fast  # noqa
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
keys, X, found, meta, fk, fp = A.image_features("glint")
idx = {k: i for i, k in enumerate(keys)}
Xfit = X[[idx[k] for k in fk]]
g = collections.defaultdict(list)
for i, p in enumerate(fp):
    g[p].append(i)
pers = sorted(g); rng = np.random.default_rng(20261111); rng.shuffle(pers)
fold = {p: i % 5 for i, p in enumerate(pers)}; fpa = np.array(fp); db = np.array([p.split(":")[0] for p in fp])
V, Y = [], []
for f in range(5):
    ix = np.where([fold[p] == f for p in fp])[0]
    for i in ix:
        V.append(Xfit[i]); Y.append(0)
    for p in [p for p in pers if fold[p] == f]:
        for a, b in itertools.combinations(g[p], 2):
            v = Xfit[a] + Xfit[b]; V.append(v / np.linalg.norm(v)); Y.append(0)
    n = 0
    while n < 4000:
        a, b = rng.choice(ix, 2)
        if fpa[a] == fpa[b] or db[a] != db[b]:
            continue
        v = Xfit[a] + Xfit[b]; V.append(v / np.linalg.norm(v)); Y.append(1); n += 1
V, Y = np.array(V), np.array(Y)
sc = StandardScaler().fit(V); h = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000).fit(sc.transform(V), Y)
u = Xfit.mean(0); u /= np.linalg.norm(u)
nat = {k.split("|", 2)[2]: k for k, m in meta.items() if m["group"] == "e7_native" and k in idx and found[idx[k]]}
fams = sorted({m["group"] for m in meta.values() if m["group"].startswith("e7_") and m["group"] != "e7_native"})
for fam in fams:
    pr = [(nat[k.split("|", 2)[2]], k) for k, m in meta.items() if m["group"] == fam and k in idx and found[idx[k]] and k.split("|", 2)[2] in nat]
    a = np.array([X[idx[x]] for x, _ in pr]); b = np.array([X[idx[y]] for _, y in pr])
    ha, hb = h.decision_function(sc.transform(a)), h.decision_function(sc.transform(b))
    pa, pb = a @ u, b @ u
    print(f"{fam:18s} n={len(pr):3d} cos(native,copy) med {np.median((a*b).sum(1)):.3f} | head: AUC {auc_fast(hb, ha):.3f}, share lower {np.mean(hb < ha):.2f}, "
          f"median shift {np.median(hb-ha)/ha.std():+.2f} SD | mean-direction projection: AUC {auc_fast(pb, pa):.3f}, share lower {np.mean(pb < pa):.2f}, median shift {np.median(pb-pa)/pa.std():+.2f} SD")

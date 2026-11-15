"""Reviewer check (post hoc, unregistered, descriptive): virtual feature midpoints of the EVALUATION pools' own
sources, scored with the registered genuine-only ISS, next to the real built images. Splits the closed-form
shortfall into (a) pool/statistic and (b) image formation. Point estimates, plain Mann-Whitney AUC, no intervals."""
import sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/ID0")
import analyse as A  # noqa
from iss import ISS, auc_fast  # noqa

arm = sys.argv[1]
keys, X, found, meta, fk, fp = A.image_features(arm)
idx = {k: i for i, k in enumerate(keys)}
ok = np.isfinite(X).all(1)
Xfit = X[[idx[k] for k in fk]]
M = ISS(Xfit, fp, kmax=64)
meta = {k: v for k, v in meta.items() if k in idx and found[idx[k]] and ok[idx[k]]}
unit = arm == "glint"


def grp(g):
    return [k for k, m in meta.items() if m["group"] == g and not (A.valbad(m["p1"]) or A.valbad(m["p2"]))]


def sc(V):
    return M.scores(np.asarray(V))["iss"]


def vec(k):
    return X[idx[k]]


def virt(ks):
    out, kk = [], []
    for k in ks:
        m = meta[k]
        if m["src1"] in idx and m["src2"] in idx and m["src1"] in meta and m["src2"] in meta:
            w = float(m["w2"])
            v = (1 - w) * vec(m["src1"]) + w * vec(m["src2"])
            if unit:
                v = v / np.linalg.norm(v)
            out.append(v)
            kk.append(k)
    return np.array(out), kk


print("arm", arm, "fit", M.summary()["k"], "d", M.d)
for lab, pos, negs in (("AR1 OpenCV R4", "ar1_frgcferet_opencv_R4", ("ar1src_frgcferet_H", "ar1_frgcferet_opencv_R2w", "ar1_frgcferet_opencv_R3")),
                       ("AR1 OpenCV R3 (same person)", "ar1_frgcferet_opencv_R3", ("ar1src_frgcferet_H", "ar1_frgcferet_opencv_R2w")),
                       ("A43 stored B20", "a43_B20", ("a43_E", "a43_D20")),
                       ("DiffAE-native B20", "dae_B20", ("dae_a256", "dae_D20")),
                       ("DiffAE-native C20 (same person)", "dae_C20", ("dae_a256", "dae_D20")),
                       ("A43 stored C20 (same person)", "a43_C20", ("a43_E", "a43_D20"))):
    pk = grp(pos)
    if not pk:
        continue
    V, kk = virt(pk)
    if not len(V):
        continue
    sreal = sc([vec(k) for k in kk])
    svirt = sc(V)
    for ng in negs:
        nk = grp(ng)
        if not nk:
            continue
        sn = sc([vec(k) for k in nk])
        print(f"{lab:34s} vs {ng:28s} n={len(kk):4d}/{len(nk):4d}  real {auc_fast(sreal, sn):.3f}   virtual feature midpoint {auc_fast(svirt, sn):.3f}")
    # paired: how much of the virtual shift does the real image realise (median of score differences to the host photo)
    h = [meta[k]["src1"] for k in kk]
    sh = sc([vec(k) for k in h])
    print(f"   paired median shift vs src1: real {np.median(sreal - sh):+.3f}  virtual {np.median(svirt - sh):+.3f}  "
          f"share of hosts moved up: real {np.mean(sreal > sh):.3f} virtual {np.mean(svirt > sh):.3f}  SD(src1 score) {sh.std():.3f}")

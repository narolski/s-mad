"""Reviewer check (post hoc, unregistered, descriptive): does the DiffAE z_sem score on the landmark ladder follow the
exact-shape score host by host? Spearman over AR1 hosts of (a) R4 scores, (b) paired shifts R4 - R2w (image) against
R4 - R3 shape (exact). Also the glintr100 virtual head and CLIP for comparison."""
import sys
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, "/home/narolski/smad-next/src/ID0")
import analyse as A  # noqa
from iss import ISS  # noqa

kL, XL, mL, fkL, fpL = A.landmark_features()
iL = {k: i for i, k in enumerate(kL)}
ML = ISS(XL[[iL[k] for k in fkL]], fpL, kmax=64)
sL = ML.scores(XL)["iss"]
out = {}
for arm in ("diffae", "clip", "dino"):
    keys, X, found, meta, fk, fp = A.image_features(arm)
    idx = {k: i for i, k in enumerate(keys)}
    M = ISS(X[[idx[k] for k in fk]], fp, kmax=64)
    s = M.scores(X)["iss"]
    rows = []
    for k, m in meta.items():
        if m["group"] != "ar1_frgcferet_opencv_R4" or k not in idx or A.valbad(m["p1"]) or A.valbad(m["p2"]):
            continue
        h = m["p1"]
        k2w, kh = f"ar1|frgcferet|opencv|R2w|{h}", f"ar1src|frgcferet|{h}|H"
        l4, l3, l0 = f"L|frgcferet|R4|{h}", f"L|frgcferet|R3|{h}", f"L|frgcferet|src|{h}|H"
        if k2w in idx and kh in idx and l4 in iL:
            rows.append((s[idx[k]], s[idx[k2w]], s[idx[kh]], sL[iL[l4]], sL[iL[l3]], sL[iL[l0]]))
    r = np.array(rows)
    print(f"{arm}: n={len(r)}  rho(R4 image score, R4 exact-shape score) = {spearmanr(r[:,0], r[:,3]).statistic:+.3f}; "
          f"rho(image R4-R2w, shape R4-R3) = {spearmanr(r[:,0]-r[:,1], r[:,3]-r[:,4]).statistic:+.3f}; "
          f"rho(image R4-R0, shape R4-R0) = {spearmanr(r[:,0]-r[:,2], r[:,3]-r[:,5]).statistic:+.3f}; "
          f"rho(host photo image score, host exact-shape score) = {spearmanr(r[:,2], r[:,5]).statistic:+.3f}")

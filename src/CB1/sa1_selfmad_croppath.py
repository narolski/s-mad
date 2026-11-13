"""CB1 amendment 5, cell 10-SelfMAD: SelfMAD own crop; FRLL-Morphs five-family EER with the raw genuine photos (A41 x7,
logit) against our aligned genuine frames through the own crop (A32-RSX, probability -> logit, saturated values tie),
same raw-file morphs (A41 x7). Pools from RS1 analyse.selfmad_pools (read only).
  python3 -I sa1_selfmad_croppath.py OUT.json"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/RS1"); sys.path.insert(0, "/home/narolski/smad-next/src/CB1")
import analyse as A
from analyse_cnn import w_eer
P = A.selfmad_pools(A.manifest())
def lg(pool):
    s = pool.s.astype(float)
    if pool.key == "logit":
        return s
    p = np.clip(s, 1e-7, 1 - 1e-7); return np.log(p / (1 - p))
out = {}
for g in ("G_raw", "Galn_frll"):
    e = {}
    for f in ("amsl", "facemorpher", "opencv", "stylegan", "webmorph"):
        m = P.get(f"M_{f}")
        if m is None or g not in P:
            e[f] = None; continue
        s = np.r_[lg(P[g]), lg(m)]; y = np.r_[np.zeros(len(P[g].s)), np.ones(len(m.s))]
        e[f] = round(100 * w_eer(s, y), 2)
    vals = [v for v in e.values() if v is not None]
    out[g] = dict(per_family=e, mean5=round(float(np.mean(vals)), 2) if len(vals) == 5 else None, n_gen=int(len(P[g].s)) if g in P else 0,
                  ties_in_genuine=int(len(P[g].s) - len(np.unique(P[g].s))) if g in P else None)
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))

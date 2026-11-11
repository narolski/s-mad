"""Mirror-asymmetry test (AS0), amendment A1: midline geometry per item from its landmarks (no image is read).
Midline x at eye level (pupil midpoint and the midpoints of the mirror-paired eye and brow points), nose level (nose
midline points 72, 73, 74, 80, 86) and mouth level (mouth midline points 53, 60, 62, 71 and the midpoints of the
paired mouth points), as offsets from the frame's flip axis (W - 1)/2 in units of the frame's nominal IOD.
  python3 -I as0_geom.py -> OUT/geom.npz (ids, G [n, 5]: off_eye, off_nose, off_mouth, bend_nose, bend_mouth)"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402
import as0_measure as M  # noqa: E402

EYE = list(range(33, 52))          # left eye + left brow (paired with 87..105 by the permutation)
MOUTH_PAIRED = [52, 54, 55, 56, 63, 64, 65, 66]
NOSE_MID = [72, 73, 74, 80, 86]
MOUTH_MID = [53, 60, 62, 71]


def main():
    items = {it["id"]: it for it in K.read_csv(K.OUT / "items.csv")}
    L = M.LM(items)
    nom = json.load(open(K.OUT / "iod_nominal.json"))
    z = np.load(K.OUT / "meas_all.npz", allow_pickle=False)
    ids = z["ids"].tolist()
    W = z["C"][:, z["cov_names"].tolist().index("W")]
    G = np.full((len(ids), 5), np.nan)
    P = K.PERM106
    for n, i in enumerate(ids):
        it = items[i]
        lm = L.of(it)
        if lm is None or not np.isfinite(W[n]):
            continue
        ax = (W[n] - 1) / 2
        iod = nom[it["frame"]]["median"]
        eye = np.mean([(lm[j, 0] + lm[P[j], 0]) / 2 for j in EYE])
        nose = lm[NOSE_MID, 0].mean()
        mouth = np.mean([lm[j, 0] for j in MOUTH_MID] + [(lm[j, 0] + lm[P[j], 0]) / 2 for j in MOUTH_PAIRED])
        G[n] = [(eye - ax) / iod, (nose - ax) / iod, (mouth - ax) / iod, (nose - eye) / iod, (mouth - eye) / iod]
    np.savez(K.OUT / "geom.npz", ids=np.array(ids), G=G,
             names=np.array(["off_eye", "off_nose", "off_mouth", "bend_nose", "bend_mouth"]))
    print("geom", len(ids), int(np.isfinite(G[:, 0]).sum()))


if __name__ == "__main__":
    main()

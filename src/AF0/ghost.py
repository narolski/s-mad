"""AF0 wave 2 (lead, 11 Nov): ghost-energy and disagreement targets per patch, and the warped halves as negatives.

For every AF0 morph the unchanged engine is run again (af_morph.warped_pair: its own float32 warped images W_A, W_B);
a(x) is the stored map. Luma Y = 0.299 R + 0.587 G + 0.114 B. Per patch (area-weighted footprint in the 512 frame, the
same footprints as the alpha target; numpy only, nothing written as an image except the halves below):
  g = 4 * a_p * (1 - a_p) * sd_patch(Y_A - Y_B) / (sd_patch(Y_out) + C),  a_p = patch mean of a(x), C = 2 grey levels
  D = patch mean of a(x) * mean_channels |W_A - W_B|
  G = patch mean of a(x) * |grad Y_A - grad Y_B| (forward differences; wave 3's flat-excluding target)
  sdo = sd_patch(Y_out) (the patch's own contrast, for the wave-3 target sanity checks)
Both are 0 where a = 0 (zero-field images), on photos and on the halves.
Halves (negatives, all-zero maps): W_A and W_B as the engine's own clip + uint8 cast, lossless PNG in the same frame,
for the wave-1 pairs (W_A of a zero-field pair is that zero-field image itself and is not written again).
  python3 -I ghost.py --workers 6
"""
import argparse
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

C = 2.0
GRIDS = (32, 24, 16)
_W = {}


def Wm(g):
    if g not in _W:
        _W[g] = L.area_matrix(g)
    return _W[g]


def luma(x):                        # BGR float
    return 0.114 * x[..., 0] + 0.587 * x[..., 1] + 0.299 * x[..., 2]


def job(r):
    import cv2
    cv2.setNumThreads(1)
    import af_morph as AM
    A, B = cv2.imread(r["A"]), cv2.imread(r["B"])
    la, lb = AM.parse_tem(r["A"][:-4] + ".tem"), AM.parse_tem(r["B"][:-4] + ".tem")
    wA, wB, _, _ = AM.warped_pair(A, la, B, lb)
    a = np.load(r["map"]).astype(np.float64)
    out = cv2.imread(r["image"]).astype(np.float64)
    hA, hB = np.clip(wA, 0, 255), np.clip(wB, 0, 255)
    d = luma(hA) - luma(hB)
    yo = luma(out)
    ad = a * np.abs(hA - hB).mean(-1)
    yA, yB = luma(hA), luma(hB)
    gx = np.diff(yA, axis=1, append=yA[:, -1:]) - np.diff(yB, axis=1, append=yB[:, -1:])
    gy = np.diff(yA, axis=0, append=yA[-1:, :]) - np.diff(yB, axis=0, append=yB[-1:, :])
    ag = a * np.sqrt(gx * gx + gy * gy)          # wave 3: gradient disagreement (zero on flat regions of both)
    res = {}
    for g in GRIDS:
        W = Wm(g)
        pm = lambda M: W @ M @ W.T  # noqa
        sd_d = np.sqrt(np.maximum(pm(d * d) - pm(d) ** 2, 0))
        sd_o = np.sqrt(np.maximum(pm(yo * yo) - pm(yo) ** 2, 0))
        ap = pm(a)
        res[f"g{g}"] = (4 * ap * (1 - ap) * sd_d / (sd_o + C)).reshape(-1).astype(np.float32)
        res[f"D{g}"] = pm(ad).reshape(-1).astype(np.float32)
        res[f"G{g}"] = pm(ag).reshape(-1).astype(np.float32)
        res[f"sdo{g}"] = sd_o.reshape(-1).astype(np.float32)
    halves = []
    if True:            # halves for every selected pair
        for tag, h in (("halfA", hA), ("halfB", hB)):
            if tag == "halfA" and r["field"] == "zero":
                continue
            p = L.OUT / "img" / r["split"] / tag / f"{r['id']}_{tag}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                assert cv2.imwrite(str(p), h.astype(np.uint8))
            halves.append((tag, str(p)))
    return r["id"], res, halves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--wave", type=int, default=0, help="1 = wave-1 pairs only")
    ap.add_argument("--plus-u50", action="store_true", help="also every uniform-0.5 pair (wave-3 ablation arms)")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(L.OUT / "manifest.csv")) if r["kind"] == "morph"
            and (not a.wave or int(r["wave"]) <= a.wave or (a.plus_u50 and r["field"] == "u50"))][: a.limit or None]
    from multiprocessing import Pool
    T = {}
    H = []
    byid = {r["id"]: r for r in rows}
    with Pool(a.workers) as p:
        for k, (iid, res, halves) in enumerate(p.imap(job, rows, chunksize=4)):
            T[iid] = res
            for tag, path in halves:
                H.append((byid[iid], tag, path))
            if (k + 1) % 500 == 0:
                print(k + 1, flush=True)
    sfx = f"_limit{a.limit}" if a.limit else ""
    ids = np.array(list(T))
    np.savez(L.OUT / f"ghost_targets{sfx}.npz", ids=ids,
             **{f"{t}{g}": np.stack([T[i][f"{t}{g}"] for i in ids]) for t in ("g", "D", "G", "sdo") for g in GRIDS})
    with open(L.OUT / f"halves{sfx}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "path", "split", "db", "field", "pid_A", "pid_B", "lm"])
        for r, tag, path in H:
            w.writerow([f"{r['id']}_{tag}", path, r["split"], r["db"], tag, r["pid_A"] if tag == "halfA" else r["pid_B"],
                        r["pid_A"] if tag == "halfA" else r["pid_B"], r["map"][:-4] + "_lm.npy"])
    print("targets", len(ids), "halves", len(H))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

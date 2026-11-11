"""Wave 3, control 2: target sanity per target variant (alpha a, ghost energy g, disagreement D, gradient
disagreement G, and D restricted to patches above the median contrast 'Dm'), at the 32 x 32 patch grid.
  AF0 part (ghost_targets.npz, validation + training morphs with measured targets, u50 images so a is constant):
    per image, in-hull patches split by the patch's own contrast (sd of output luma, 'sdo') into quartiles;
    median target on the flattest and on the busiest quartile (medians over images), and the per-image Spearman
    between target and contrast (mean over images).
  AR1 part (OpenCV-style engine, a = 0.5, 100 frgcferet hosts, seed 401): the same targets computed for the
    same-person morph (H, S), the mirror self-morph (H, mirror H; AR1's mirror frame + .tem) and the two-person morph
    (H, B); ratio of the in-hull mean target, same-person / two-person and mirror / two-person (median over hosts).
Acceptance (lead): flat below busy and |contrast correlation| < 0.3.
  python3 -I sanity.py --workers 2
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import ghost as G  # noqa: E402


def targets_for_pair(args):
    import cv2
    import af_morph as AM
    pa, ta, pb, tb = args
    A, B = cv2.imread(pa), cv2.imread(pb)
    wA, wB, out, tris = AM.warped_pair(A, AM.parse_tem(ta), B, AM.parse_tem(tb))
    LM = AM.mean_shape(A, AM.parse_tem(ta), AM.parse_tem(tb))
    a = np.full(A.shape[:2], 0.5)
    hA, hB = np.clip(wA, 0, 255), np.clip(wB, 0, 255)
    d = G.luma(hA) - G.luma(hB)
    yo = G.luma(out.astype(np.float64))
    yA, yB = G.luma(hA), G.luma(hB)
    gx = np.diff(yA, axis=1, append=yA[:, -1:]) - np.diff(yB, axis=1, append=yB[:, -1:])
    gy = np.diff(yA, axis=0, append=yA[-1:, :]) - np.diff(yB, axis=0, append=yB[-1:, :])
    W = G.Wm(32)
    pm = lambda M: W @ M @ W.T  # noqa
    sd_d = np.sqrt(np.maximum(pm(d * d) - pm(d) ** 2, 0))
    sd_o = np.sqrt(np.maximum(pm(yo * yo) - pm(yo) ** 2, 0))
    face = pm(L.hull_mask(LM[:106])) >= L.FACE_MIN
    t = dict(alpha=pm(a), g=4 * 0.25 * sd_d / (sd_o + G.C), D=pm(a * np.abs(hA - hB).mean(-1)),
             G=pm(a * np.sqrt(gx * gx + gy * gy)))
    med = np.median(sd_o[face])
    t["Dm"] = t["D"] * (sd_o > med)
    return {k: float(v[face].mean()) for k, v in t.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--hosts", type=int, default=100)
    a = ap.parse_args()
    from scipy.stats import spearmanr
    z = np.load(L.OUT / "ghost_targets.npz")
    man = {r["id"]: r for r in csv.DictReader(open(L.OUT / "manifest.csv"))}
    face = {}
    for n in ("af0_w1", "af0_w2"):
        pr = L.prep(n, 32)
        face.update(dict(zip(pr["ids"], pr["face"] >= L.FACE_MIN)))
    res = {"af0": {}}
    keys = ("g", "D", "G", "Dm")
    acc = {k: dict(flat=[], busy=[], rho=[]) for k in keys}
    for i, iid in enumerate(z["ids"]):
        if man[iid]["field"] != "u50":
            continue
        m = face[iid]
        sdo = z["sdo32"][i][m]
        q1, q3 = np.quantile(sdo, [0.25, 0.75])
        for k in keys:
            t = (z["D32"][i] * (z["sdo32"][i] > np.median(z["sdo32"][i][m])))[m] if k == "Dm" else z[f"{k}32"][i][m]
            acc[k]["flat"].append(np.median(t[sdo <= q1]))
            acc[k]["busy"].append(np.median(t[sdo >= q3]))
            acc[k]["rho"].append(spearmanr(t, sdo)[0])
    for k, v in acc.items():
        f, b, r = np.median(v["flat"]), np.median(v["busy"]), float(np.nanmean(v["rho"]))
        res["af0"][k] = dict(median_flat=round(float(f), 4), median_busy=round(float(b), 4), contrast_rho=round(r, 4),
                             n_images=len(v["rho"]), accepted=bool(f < b and abs(r) < 0.3))
    res["af0"]["alpha"] = dict(note="a is constant (0.5) on uniform images: flat = busy, contrast correlation undefined",
                               accepted=False)
    pool = list(csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv")))
    rng = np.random.default_rng(401)
    pick = [pool[i] for i in sorted(rng.choice(len(pool), min(a.hosts, len(pool)), replace=False))]
    jobs = []
    for r in pick:
        mir = f"/mnt/t7/smad_next/AR1/mirror/frgcferet/{r['pid'].replace(':', '_')}.png"
        jobs += [(r["H"], r["H"][:-4] + ".tem", r["S"], r["S"][:-4] + ".tem"),
                 (r["H"], r["H"][:-4] + ".tem", mir, mir[:-4] + ".tem"),
                 (r["H"], r["H"][:-4] + ".tem", r["B"], r["B"][:-4] + ".tem")]
    from multiprocessing import Pool
    with Pool(a.workers) as p:
        out = p.map(targets_for_pair, jobs, chunksize=2)
    rat = {}
    for k in ("alpha", "g", "D", "G", "Dm"):
        same = [out[3 * j][k] / max(out[3 * j + 2][k], 1e-9) for j in range(len(pick))]
        mirr = [out[3 * j + 1][k] / max(out[3 * j + 2][k], 1e-9) for j in range(len(pick))]
        rat[k] = dict(same_over_two=round(float(np.median(same)), 4), mirror_over_two=round(float(np.median(mirr)), 4),
                      iqr_same=[round(float(x), 4) for x in np.quantile(same, [0.25, 0.75])],
                      iqr_mirror=[round(float(x), 4) for x in np.quantile(mirr, [0.25, 0.75])])
    res["ar1_ratios_opencv_engine_a05"] = dict(n_hosts=len(pick), **rat)
    json.dump(res, open(L.RES / "wave3_target_sanity.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

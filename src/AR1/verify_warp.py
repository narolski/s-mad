"""Amendment 4 check: the warp-only driver reproduces the unchanged tool's warp. For each host, the A-side image
(R2w4 = H warped to mean(H, B), H texture only) and the matching B-side image (B warped to the same mean shape with the
same driver, computed here in memory, never written) are averaged and compared with the tool's R4 = tool(H, B):
  OpenCV      : 0.5 * (A + B) vs R4 over the whole frame (tool truncates the float blend; expected |diff| <= 1)
  FaceMorpher : cv2.addWeighted(A, 0.5, B, 0.5) vs R4 inside the face mask (outside, R2w4 keeps H's own background)
Same check for R2w (partner S, tool R3).
  python3 -I verify_warp.py [--limit 8]   -> experiments/AR1/warp_check[_smoke].json
"""
import argparse
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import variants as V  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    import cv2
    hm = V._load(K.MC / "scripts/68_hires_morph.py", "hm68")
    warper, blender = V._load(V.FM / "warper.py", "warper"), V._load(V.FM / "blender.py", "blender")
    rows = list(csv.DictReader(open(K.OUT / "pool.csv")))[: a.limit or None]
    out = {}
    for rung, partner, tool_rung in (("R2w4", "B", "R4"), ("R2w", "S", "R3")):
        for tool in ("opencv", "facemorpher"):
            mx, mean, fr_in = [], [], []
            for r in rows:
                s = r["pid"].replace(":", "_") + ".png"
                A = cv2.imread(str(K.OUT / "img/frgcferet" / tool / rung / s)).astype(int)
                T = cv2.imread(str(K.OUT / "img/frgcferet" / tool / tool_rung / s)).astype(int)
                b = cv2.imread(r[partner])
                lh, lb = K.read_tem(r["H"][:-4] + ".tem"), K.read_tem(r[partner][:-4] + ".tem")
                if tool == "opencv":
                    Bw = V.warp_cv(b, lb, lh, hm).astype(int)
                    d = np.abs(((A + Bw) / 2.0) - T)
                    m = np.ones(A.shape[:2], bool)
                else:
                    size = b.shape[:2]
                    pts = np.rint((lh + lb) / 2.0).astype(int)
                    Bw = warper.warp_image(b, np.rint(lb).astype(int), pts, size).astype(np.uint8)
                    avg = cv2.addWeighted(A.astype(np.uint8), 0.5, Bw, 0.5, 0).astype(int)
                    m = blender.mask_from_points(size, pts) > 0
                    d = np.abs(avg - T)
                mx.append(float(d[m].max()))
                mean.append(float(d[m].mean()))
                fr_in.append(float(m.mean()))
            out[f"{rung}/{tool}"] = dict(n=len(rows), max_abs_diff_max=max(mx), max_abs_diff_median=float(np.median(mx)),
                                        mean_abs_diff_median=float(np.median(mean)),
                                        region="whole frame" if tool == "opencv" else "face mask",
                                        mask_fraction_median=float(np.median(fr_in)))
            print(rung, tool, out[f"{rung}/{tool}"], flush=True)
    json.dump(out, open(K.RES / ("warp_check.json" if not a.limit else "warp_check_smoke.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

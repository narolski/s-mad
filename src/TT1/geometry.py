"""Threshold transfer on unseen genuine sources (TT1): crop geometry of the unseen sources in the canonical 512 frame,
for the crop-geometry-matched reference (amendment M4). No score; reads the aligned U_p frames only.
Per U_p frame: the bounding box of the non-black pixels (max over channels > 0) of the 512x512 aligned frame, i.e. where
the warped source crop landed. Per geometry group (g224 = the four anti-spoofing sets, 224 px frames; g112 = the four
packs, 112 px crops): median x0, x1 (exclusive), y0, y1 (exclusive), rounded to integers, and the median source
inter-eye distance (ied_src) of the group.
  python3 -I geometry.py -> experiments/TT1_.../crop_geometry.json"""
import json
import sys
import pathlib

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402


def main():
    rows = [r for r in T.tt1_rows() if r["primary"]]
    out = {}
    for g, srcs in (("g224", T.ANTISPOOF), ("g112", T.SOURCES[4:])):
        rs = [r for r in rows if r["source"] in srcs]
        bb = []
        for r in rs:
            m = cv2.imread(r["aligned_path"]).max(2) > 0
            ys, xs = np.where(m.any(1))[0], np.where(m.any(0))[0]
            bb.append((xs[0], xs[-1] + 1, ys[0], ys[-1] + 1))
        bb = np.array(bb, float)
        med = np.median(bb, 0)
        box = [int(round(v)) for v in med]
        out[g] = dict(n=len(rs), box_x0_x1_y0_y1=box, box_w=box[1] - box[0], box_h=box[3] - box[2],
                      p10=[float(v) for v in np.percentile(bb, 10, 0)], p90=[float(v) for v in np.percentile(bb, 90, 0)],
                      median_ied_src=float(np.median([float(r["ied_src"]) for r in rs])),
                      box_in_ied_units_from_eye_mid=[(box[0] - 256) / 132, (box[1] - 256) / 132, (box[2] - 210) / 132,
                                                     (box[3] - 210) / 132])
    (T.RES / "crop_geometry.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

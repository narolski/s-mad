"""Platform check of the AR1 scoring adapter: rescore the A46 RGB crops of FRLL bona fide + published OpenCV /
FaceMorpher with score.py and compare with the registered A46 RGB-only score files (same ids, score_noTTA).
  python3 -I check_a46.py list     -> OUT/lists/a46check.csv
  python3 -I check_a46.py compare  -> experiments/AR1/a46_platform_check.json
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402

ROOT = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
REG = pathlib.Path("/mnt/t7/smad_heldout/a46_rgb_only_20261108/scores")


def main():
    if sys.argv[1] == "list":
        rows = [dict(id=r["id"], path=str(ROOT / r["path"])) for r in csv.DictReader(open(ROOT / "manifests/a46c_rgb_clip.csv"))
                if r["pool"] in ("frllm_frll_bona", "frllm_opencv", "frllm_facemorpher")]
        with open(K.OUT / "lists/a46check.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "path"])
            w.writeheader()
            w.writerows(rows)
        print(len(rows))
        return
    out = {}
    for d in ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd"):
        z = np.load(K.OUT / f"scores/a46check/scores_rel_{d}.npz")
        r = np.load(REG / d / "scores_a46_rgb_only.npz")
        reg = dict(zip(r["id"].tolist(), r["score_noTTA"]))
        ours = dict(zip(z["id"].tolist(), z["score_noTTA"]))
        ids = [i for i in ours if i in reg]
        a = np.array([ours[i] for i in ids])
        b = np.array([reg[i] for i in ids])
        out[d] = dict(n=len(ids), max_abs_diff=float(np.abs(a - b).max()), mean_abs_diff=float(np.abs(a - b).mean()))
    json.dump(out, open(K.RES / "a46_platform_check.json", "w"), indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()

"""Own-crop re-score of the audit rows (RS1): platform and crop checks (no efficacy number is printed).

  python3 -I platform_check.py
1. Rescored A46 crops vs the registered A46 RGB-only per-image files (same crop files, same ids): max and mean
   |score_noTTA difference| per release, over every id both files hold.
2. Crop check: boxes of 32 raw files re-detected with crop_rgb.py (batched) vs the A46 boxes (attempts_rgb_clip.jsonl).
Writes experiments/RS1_own-crop-rescore/rs1_platform_check.json.
"""
import csv
import json
import pathlib

import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

K.add_paths(K.MC, K.W46 / "smadcvpr")
import analyze as A  # noqa: E402

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
REG = pathlib.Path("/mnt/t7/smad_heldout/a46_rgb_only_20261108/scores")
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
DETS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitl14", "mixfacenet_mad_smdd", "madation_fe_vitb16")


def main():
    out = {"score_check": {}, "crop_check": {}}
    for d in DETS:
        f = OUT / f"scores/scores_rel_{d}__a46.npz"
        if not f.exists():
            out["score_check"][d] = "not scored"
            continue
        z = np.load(f)
        r = np.load(REG / d / "scores_a46_rgb_only.npz")
        reg = dict(zip(r["id"].tolist(), r["score_noTTA"].astype(float)))
        ours = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(float)))
        ids = [i for i in ours if i in reg]
        a = np.array([ours[i] for i in ids])
        b = np.array([reg[i] for i in ids])
        out["score_check"][d] = dict(n=len(ids), n_ours=len(ours), max_abs_diff=float(np.abs(a - b).max()),
                                     mean_abs_diff=float(np.abs(a - b).mean()),
                                     n_diff_over_1e3=int((np.abs(a - b) > 1e-3).sum()))
        # per pool: crops stored as JPEG (FRLL-Morphs) vs PNG; and the native EER of each cell from both score sets
        pool = {r["id"]: r for r in csv.DictReader(open(A46 / "manifests/a46c_rgb_clip.csv"))}
        regl = dict(zip(r["id"].tolist(), r["logit_noTTA"].astype(float)))
        ourl = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
        per = {}
        for p in sorted({pool[i]["pool"] for i in ids}):
            pi = [i for i in ids if pool[i]["pool"] == p]
            dd = np.abs(np.array([ours[i] for i in pi]) - np.array([reg[i] for i in pi]))
            per[p] = dict(n=len(pi), ext=pathlib.Path(pool[pi[0]]["path"]).suffix, max_abs_diff=float(dd.max()),
                          n_diff_over_1e3=int((dd > 1e-3).sum()))
        bona = [i for i in ids if pool[i]["pool"] == "frllm_frll_bona"]
        cells = {}
        for p in per:
            if p == "frllm_frll_bona":
                continue
            mi = [i for i in ids if pool[i]["pool"] == p]
            cells[p] = dict(eer_dgx=round(100 * A.eer(np.array([ourl[i] for i in bona]), np.array([ourl[i] for i in mi])), 3),
                            eer_a46_registered=round(100 * A.eer(np.array([regl[i] for i in bona]),
                                                                 np.array([regl[i] for i in mi])), 3))
        out["score_check"][d]["per_pool"] = per
        out["score_check"][d]["native_eer_by_platform"] = cells
    # crop check
    src2box = {}
    for ln in open(A46 / "attempts_rgb_clip.jsonl"):
        r = json.loads(ln)
        src2box[r["src_path"]] = r.get("box")
    chk = {r["id"]: r["path"] for r in csv.DictReader(open(OUT / "lists/cropcheck.csv"))}
    f = OUT / "crops/check/crops.csv"
    if f.exists():
        diffs, nof = [], 0
        for r in csv.DictReader(open(f)):
            if not r["box"]:
                nof += 1
                continue
            b1 = np.array(json.loads(r["box"]))
            b0 = np.array(src2box[chk[r["id"]]])
            diffs.append(float(np.abs(b1 - b0).max()))
        out["crop_check"] = dict(n=len(diffs), no_face=nof, max_box_diff_px=max(diffs),
                                 median_box_diff_px=float(np.median(diffs)))
    json.dump(out, open(RES / "rs1_platform_check.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

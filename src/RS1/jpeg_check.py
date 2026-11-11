"""Own-crop re-score of the audit rows (RS1): effect of the release crop step's JPEG re-save (measurement for the lead,
not an experiment result). 300 JPEG raw files (100 FRLL photos, 40 per FRLL-Morphs family): the A46 crop as stored
(JPEG, cv2.imwrite quality 95, as the SMDD script) vs the identical crop region stored losslessly as PNG (same A46 box,
same a46_corrective_crop.crop_box). Writes the PNG crops and a 600-row scoring manifest; after scoring, compares logits.
  python3 -I jpeg_check.py build | compare
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

O = pathlib.Path("/mnt/t7/smad_next/RS1/jpegcheck")
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
RELS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitl14", "madation_fe_vitb16", "madation_fs_vitb16",
        "madation_fs_vitl14", "mixfacenet_mad_smdd")


def build():
    import cv2
    CC = K.load_module(K.W46 / "smadcvpr/a46_corrective_crop.py", "a46_corrective_crop")
    att = {}
    for ln in open(A46 / "attempts_rgb_clip.jsonl"):
        q = json.loads(ln)
        att[q["output"]] = q
    rows = list(csv.DictReader(open(A46 / "manifests/a46c_rgb_clip.csv")))
    pick = [r for r in rows if r["pool"] == "frllm_frll_bona"][:100]
    for f in ("amsl", "facemorpher", "opencv", "webmorph", "stylegan"):
        pick += [r for r in rows if r["pool"] == f"frllm_{f}"][:40]
    out, stats = [], []
    for r in pick:
        q = att[r["path"]]
        img = cv2.imread(q["src_path"])
        crop, geo = CC.crop_box(img, q["box"])
        assert geo["clipped_slice"] == q["clipped_slice"], r["id"]
        p = O / "png" / f"{r['id']}.png"
        if not p.exists():
            CC.save_checked(p, crop)
        j = cv2.imread(str(A46 / r["path"]))
        assert j.shape == crop.shape
        mse = float(((j.astype(float) - crop.astype(float)) ** 2).mean())
        stats.append(10 * np.log10(255 ** 2 / max(mse, 1e-12)))
        out += [dict(id="j_" + r["id"], path=str(A46 / r["path"])), dict(id="p_" + r["id"], path=str(p))]
    with open(O / "jpegcheck.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path"])
        w.writeheader()
        w.writerows(out)
    print(len(pick), "pairs; PSNR JPEG crop vs PNG crop: median", round(float(np.median(stats)), 2), "min",
          round(float(np.min(stats)), 2))


def compare():
    pool = {r["id"]: r["pool"] for r in csv.DictReader(open(A46 / "manifests/a46c_rgb_clip.csv"))}
    res = {}
    for d in RELS:
        f = O / f"scores_rel_{d}__jpegcheck.npz"
        if not f.exists():
            continue
        z = np.load(f)
        lg = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
        ids = [i[2:] for i in lg if i.startswith("j_")]
        dd = np.array([lg["j_" + i] - lg["p_" + i] for i in ids])
        gen = np.array([pool[i] == "frllm_frll_bona" for i in ids])
        res[d] = dict(n=len(ids), max_abs=round(float(np.abs(dd).max()), 4),
                      median_abs=round(float(np.median(np.abs(dd))), 4),
                      mean_shift_photos=round(float(dd[gen].mean()), 4), mean_shift_morphs=round(float(dd[~gen].mean()), 4),
                      flips_at_rule=int(np.sum((np.array([lg["j_" + i] for i in ids]) > 0) != (np.array([lg["p_" + i] for i in ids]) > 0))))
    json.dump(res, open("/home/narolski/smad-next/experiments/RS1_own-crop-rescore/rs1_jpeg_storage_check.json", "w"),
              indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"build": build, "compare": compare}[sys.argv[1]]()

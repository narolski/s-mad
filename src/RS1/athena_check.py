"""Own-crop re-score of the audit rows (RS1): equivalence of an Athena run with the DGX and with the registered A46
scores (no efficacy number is computed).

  python3 -I athena_check.py RESULT_DIR [TAG]
RESULT_DIR = an unpacked Athena result tar (scores/, crops/). Compares, on every image both hold:
  (a) logit_noTTA of the Athena scores vs the DGX scores of the reused A46 crops (MADation ViT-B/16, ViT-L/14);
  (b) score_noTTA / logit_noTTA vs the registered A46 RGB-only scores (WCSS), all seven releases;
  (c) MTCNN boxes of the Athena crops vs the DGX crops of the same images (crop journals).
Each split by crop file type (JPEG / PNG). Writes experiments/RS1_own-crop-rescore/rs1_athena_equivalence[_TAG].json.
"""
import csv
import json
import pathlib
import sys

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
REG = pathlib.Path("/mnt/t7/smad_heldout/a46_rgb_only_20261108/scores")
RELS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitl14", "madation_fe_vitb16", "madation_fs_vitb16",
        "madation_fs_vitl14", "mixfacenet_mad_smdd")


def diffs(a, b, ids, ext):
    out = {}
    for e in sorted(set(ext[i] for i in ids)):
        ii = [i for i in ids if ext[i] == e]
        d = np.abs(np.array([a[i] for i in ii]) - np.array([b[i] for i in ii]))
        out[e] = dict(n=len(ii), max_abs=float(d.max()), median_abs=float(np.median(d)), n_over_1e3=int((d > 1e-3).sum()))
    return out


def main():
    R = pathlib.Path(sys.argv[1])
    tag = sys.argv[2] if len(sys.argv) > 2 else ""
    man = {r["id"]: r for r in csv.DictReader(open(OUT / "athena/athena_manifest.csv"))}
    ext = {i: pathlib.Path(r["relpath"]).suffix for i, r in man.items()}
    res = {"logit_vs_dgx": {}, "vs_a46_registered": {}, "boxes_vs_dgx": {}}
    for d in RELS:
        f = R / "scores" / f"scores_rel_{d}__athena.npz"
        if not f.exists():
            continue
        z = np.load(f)
        al = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
        asc = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(float)))
        g = OUT / "scores" / f"scores_rel_{d}__a46.npz"
        if g.exists():
            y = np.load(g)
            dl = dict(zip(y["id"].tolist(), y["logit_noTTA"].astype(float)))
            ids = [i for i in al if i in dl]
            if ids:
                res["logit_vs_dgx"][d] = diffs(al, dl, ids, ext)
        r = np.load(REG / d / "scores_a46_rgb_only.npz")
        rs = dict(zip(r["id"].tolist(), r["score_noTTA"].astype(float)))
        rl = dict(zip(r["id"].tolist(), r["logit_noTTA"].astype(float)))
        ids = [i for i in al if i in rs]
        if ids:
            res["vs_a46_registered"][d] = dict(score=diffs(asc, rs, ids, ext), logit=diffs(al, rl, ids, ext))
    dgx = {}
    for f in sorted((OUT / "crops/main").glob("boxes_*of2.jsonl")):
        for ln in open(f):
            try:
                q = json.loads(ln)
            except ValueError:
                continue
            dgx[q["id"]] = q["box"]
    ath = {}
    for f in sorted((R / "crops").glob("boxes_*of3.jsonl")):
        for ln in open(f):
            q = json.loads(ln)
            ath[q["id"]] = q["box"]
    ids = [i for i in ath if i in dgx and ath[i] and dgx[i]]
    if ids:
        dd = np.array([np.abs(np.array(ath[i]) - np.array(dgx[i])).max() for i in ids])
        res["boxes_vs_dgx"] = dict(n=len(ids), max_px=float(dd.max()), median_px=float(np.median(dd)),
                                   n_over_1px=int((dd > 1).sum()),
                                   no_face_mismatch=int(sum((ath[i] is None) != (dgx[i] is None) for i in ath if i in dgx)))
    json.dump(res, open(RES / f"rs1_athena_equivalence{('_' + tag) if tag else ''}.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

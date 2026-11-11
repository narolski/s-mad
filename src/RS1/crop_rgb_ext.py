"""RS1 copy of the landmark ladder's (AR1) crop_rgb.py with ONE change: the crop is stored in the source file's format
(a .jpg input gives a .jpg crop, written by cv2.imwrite at OpenCV's default JPEG quality 95), as the SMDD crop script
(image_preprocess.py line 43) and the A46 acquisition do; AR1's version always stores PNG. Everything else unchanged.

AR1 own-crop acquisition for the MADation and MixFaceNet-MAD releases: the A46 RGB-only path
(smadcvpr/a46_corrective_crop.py of the frozen A46 runtime, imported unchanged: facenet_pytorch 2.6.0
MTCNN(select_largest=True, post_process=False, min_face_size=64, device cuda:0) on RGB pixels (detector_pixels
'rgb_clip'), box[0], crop_box = the SMDD script's 5% margin with clamping, save_checked). Run in the pinned facenet venv.
Deviation (speed, the GPU is shared): images of the same size are passed to MTCNN.detect as one batch of up to 16;
on 32 test frames batched vs one-by-one boxes differ by at most 0.04 px (median 0.006 px). Crops are stored as PNG.
Boxes are journalled per image (boxes_<shard>.jsonl) so a restart resumes. --boxes-in FILE: reuse the boxes detected on
the ORIGINAL images for blanked copies (AR4; a face-blanked image has no face to detect), crop_box unchanged.

  python3 -I crop_rgb.py --manifest M.csv --out DIR [--shard i/n] | --boxes-in boxes.json --src-col bg_path
Manifest columns: id, <src-col> (absolute image path). Writes DIR/<id>.png, DIR/crops[_iofn].csv, DIR/boxes[_iofn].jsonl.
"""
import argparse
import collections
import csv
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

BATCH = 16


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--src-col", default="path")
    ap.add_argument("--boxes-in")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    si, sn = map(int, a.shard.split("/"))
    sfx = "" if sn == 1 else f"_{si}of{sn}"
    CC = K.load_module(K.W46 / "smadcvpr/a46_corrective_crop.py", "a46_corrective_crop")
    import cv2
    import numpy as np
    import torch
    rows = list(csv.DictReader(open(a.manifest)))[: a.limit or None][si::sn]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jpath = out / f"boxes{sfx}.jsonl"
    boxes = {}
    if a.boxes_in:
        boxes = json.load(open(a.boxes_in))
    elif jpath.exists():
        for ln in open(jpath):
            d = json.loads(ln)
            boxes[d["id"]] = d["box"]
    t0 = time.time()
    if not a.boxes_in:
        from facenet_pytorch import MTCNN
        torch.set_num_threads(4)
        det = MTCNN(select_largest=True, post_process=False, min_face_size=64, device="cuda:0")
        todo = [r for r in rows if r["id"] not in boxes]
        n = 0
        with open(jpath, "a") as jf:
            for c0 in range(0, len(todo), 256):                 # stream: at most 256 decoded images in memory
                imgs, groups = {}, collections.defaultdict(list)
                for r in todo[c0:c0 + 256]:
                    assert not K.forbidden(r[a.src_col])
                    im = cv2.imread(r[a.src_col])
                    if im is None:
                        boxes[r["id"]] = None
                        continue
                    groups[im.shape].append(r["id"])
                    imgs[r["id"]] = im
                for shp, ids in groups.items():
                    for k in range(0, len(ids), BATCH):
                        chunk = ids[k:k + BATCH]
                        bb, pp, lm = det.detect(np.stack([CC.detector_pixels(imgs[i], "rgb_clip") for i in chunk]),
                                                landmarks=True)
                        for i, bi, li in zip(chunk, bb, lm):
                            box = None if li is None else [float(v) for v in bi[0]]
                            boxes[i] = box
                            jf.write(json.dumps(dict(id=i, box=box)) + "\n")
                jf.flush()
                n += min(256, len(todo) - c0)
                print(n, len(todo), round(time.time() - t0, 1), flush=True)
    res = []
    for r in rows:
        tgt = out / f"{r['id']}{pathlib.Path(r[a.src_col]).suffix.lower() or '.png'}"   # RS1: the source's format, as the SMDD script
        rec = dict(id=r["id"], path=str(tgt), status="", box="")
        box = boxes.get(r["id"])
        if box is None:
            rec["status"] = "no_face"
        else:
            img = cv2.imread(r[a.src_col])
            try:
                crop, geo = CC.crop_box(img, box)
                if not tgt.exists():
                    CC.save_checked(tgt, crop)
                rec.update(status="retained" if not geo["quality_flags"] else "flag:" + "|".join(geo["quality_flags"]),
                           box=json.dumps([round(float(v), 2) for v in box]))
            except ValueError as e:
                rec["status"] = "invalid_geometry:" + str(e)
        res.append(rec)
    with open(out / f"crops{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)
    print(json.dumps(dict(collections.Counter(r["status"].split(":")[0] for r in res))),
          round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()

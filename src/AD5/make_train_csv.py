"""Retrains of released methods (AD5): the training list of the cropped SMDD training split, in the order of SMDD's
train.csv, keeping every image whose crop file was written by the SMDD repository's image_preprocess.py (unchanged).

  python3 -I make_train_csv.py SMDD_TRAIN_CSV CROP_ROOT PREFIX OUT_CSV OUT_JSON [--every K]
SMDD_TRAIN_CSV: SMDD_release_train/train.csv (image_path relative, label bonafide|attack). CROP_ROOT: directory holding
os25k_bf_t/ and m15k_t/ crops. PREFIX: absolute directory written in front of each relative path (the crop root as
the training job sees it). --every K keeps every K-th kept row (smoke subsets only).
Output CSV header and labels as MADation / SMDD expect: image_path,label.
"""
import argparse
import csv
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("train_csv")
ap.add_argument("crop_root")
ap.add_argument("prefix")
ap.add_argument("out_csv")
ap.add_argument("out_json")
ap.add_argument("--every", type=int, default=1)
a = ap.parse_args()
rows = list(csv.DictReader(open(a.train_csv)))
assert len(rows) == 40000 and set(r["label"] for r in rows) == {"bonafide", "attack"}
kept, lost = [], []
for r in rows:
    p = os.path.join(a.crop_root, r["image_path"])
    (kept if os.path.isfile(p) and os.path.getsize(p) > 0 else lost).append(r)
sub = kept[:: a.every]
with open(a.out_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["image_path", "label"])
    for r in sub:
        w.writerow([os.path.join(a.prefix, r["image_path"]), r["label"]])
rep = dict(train_csv_rows=len(rows), kept=len(kept), lost=len(lost),
           kept_bonafide=sum(r["label"] == "bonafide" for r in kept), kept_attack=sum(r["label"] == "attack" for r in kept),
           written=len(sub), every=a.every, lost_images=[r["image_path"] for r in lost],
           madation_release_log_trainset=39730)
json.dump(rep, open(a.out_json, "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "lost_images"}))

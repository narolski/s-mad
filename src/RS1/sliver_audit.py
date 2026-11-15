"""Own-crop re-score of the audit rows (RS1), amendment 7: sliver audit of variant 1 (SMDD image_preprocess.py
unchanged). CPU re-run of the script's arithmetic (MTCNN select_largest, post_process False, min_face_size 64, BGR
pixels, boxes[0], 5% margin, the line-40 slice); nothing is written except the audit table.
  python3 -I sliver_audit.py [--limit-check 50]
Runs in the facenet venv (torch CPU, 4 threads). Output: /home/narolski/smad-next/experiments/RS1_own-crop-rescore/
rs1_sliver_audit.csv (per image) and rs1_sliver_summary.csv (per set).
"""
import argparse
import collections
import csv
import glob
import json
import pathlib
import random

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
R = OUT / "results_rented"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-check", type=int, default=50)
    ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args()
    import cv2
    import torch
    torch.set_num_threads(4)
    from facenet_pytorch import MTCNN
    det = MTCNN(select_largest=True, post_process=False, min_face_size=64, device="cpu")
    man = {r["id"]: r for r in csv.DictReader(open(OUT / "athena/athena_manifest.csv")) if r["origin"] == "crop"}
    box2 = {}
    for f in glob.glob(str(R / "prod_v2_rented/v2meta/boxes_*.jsonl")):
        for ln in open(f):
            d = json.loads(ln)
            box2[d["id"]] = d["box"]
    dropped = set(json.load(open(R / "prod_v1_rented/crop_summary.json"))["v1_missing"])
    neg2 = collections.Counter()
    by = collections.defaultdict(list)
    for i, r in man.items():
        by[r["set"]].append(i)
        b = box2.get(i)
        if b:
            x1, y1, x2, y2 = b
            w, h = x2 - x1, y2 - y1
            if round(x1 - 0.05 * w) < 0 or round(y1 - 0.05 * h) < 0:
                neg2[r["set"]] += 1
    rng = random.Random(20261112)
    todo = []
    for s, ids in sorted(by.items()):
        ids = sorted(ids)
        todo += [(s, i, "full") for i in ids] if neg2[s] else [(s, i, "check") for i in rng.sample(ids, min(a.limit_check, len(ids)))]
    if a.smoke:
        todo = todo[: a.smoke]
    rows = []
    for k, (s, i, mode) in enumerate(todo):
        img = cv2.imread(man[i]["src_path"])
        rec = dict(id=i, set=s, mode=mode, dropped_by_script=int(i in dropped), face=0, x0=None, y0=None, crop_h=0,
                   crop_w=0, start_below_0=0, short_lt32=0, malformed=0)
        if img is not None:
            bx, pr, lm = det.detect(img, landmarks=True)
            if lm is not None:
                x1, y1, x2, y2 = bx[0]
                w, h = x2 - x1, y2 - y1
                x1, y1, x2, y2 = x1 - .05 * w, y1 - .05 * h, x2 + .05 * w, y2 + .05 * h
                c = img[round(y1):round(y2), round(x1):round(x2)]
                rec.update(face=1, x0=round(x1), y0=round(y1), crop_h=c.shape[0], crop_w=c.shape[1],
                           start_below_0=int(round(x1) < 0 or round(y1) < 0), short_lt32=int(min(c.shape[:2]) < 32))
        rec["malformed"] = int(rec["start_below_0"] or rec["short_lt32"] or not rec["face"] or rec["dropped_by_script"])
        rows.append(rec)
        if k % 500 == 0:
            print(k, len(todo), flush=True)
    sfx = "_smoke" if a.smoke else ""
    with open(RES / f"rs1_sliver_audit{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summ = []
    for s in sorted(by):
        rr = [r for r in rows if r["set"] == s]
        if not rr:
            continue
        n = len(rr)
        summ.append(dict(set=s, n_set=len(by[s]), audited=n, mode=rr[0]["mode"], v2_box_start_below_0=neg2[s],
                         malformed=sum(r["malformed"] for r in rr), start_below_0=sum(r["start_below_0"] for r in rr),
                         short_lt32=sum(r["short_lt32"] for r in rr), no_face_cpu=sum(1 - r["face"] for r in rr),
                         dropped_by_script=sum(r["dropped_by_script"] for r in rr),
                         share_malformed=round(sum(r["malformed"] for r in rr) / n, 4)))
    with open(RES / f"rs1_sliver_summary{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]))
        w.writeheader()
        w.writerows(summ)
    for x in summ:
        print(x)


if __name__ == "__main__":
    main()

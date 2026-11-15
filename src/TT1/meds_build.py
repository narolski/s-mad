"""TT1 MEDS extension: genuine pool from NIST SD32 MEDS-I/II (operational mugshots). No image leaves /mnt/t7 except
inside scoring packs (author's ruling; NIST terms: no image in any figure, repository or artifact).
Selection (fixed before any score): MEDS-II images with human_review_bin_label == "Frontal" (image_pose.csv); MEDS-I
images whose file content (sha256) is not in MEDS-II and whose POS == "F" (blank POS = unknown pose -> excluded).
Duplicates by sha256 are kept once (MEDS-II copy). Person = subject id (Snnn), encounter = nn of Snnn-nn-t10_mm.
Alignment: prep_eval.align unchanged via align.py's logic (same pin), on cv2.imread of the raw JPEG; measurements as
extract.py (Laplacian variance, greyscale) and align.py (ied_src, enlarge, border_frac, aligned flag).
Out: /mnt/t7/smad_next/TT1/meds/{aligned/<id>.png, meds_manifest.csv}; counts -> experiments/TT1_.../meds_counts.json
  python -I meds_build.py [--limit 8]"""
import argparse
import collections
import csv
import hashlib
import io
import json
import pathlib
import re
import statistics as st
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import align as AL  # noqa: E402  (load_pe with the prep_eval pin, retry)
import tt1common as T  # noqa: E402

SRC = pathlib.Path("/mnt/t7/smad_next/TT1/meds_src")
UNP = pathlib.Path("/mnt/t7/Datasety/downloads/NIST_SD32_MEDS/unpacked")
OUT = pathlib.Path("/mnt/t7/smad_next/TT1/meds")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    pose2 = {r["img_fname"]: r["human_review_bin_label"] for r in csv.DictReader(open(SRC / "II_meta" / "image_pose.csv"))}
    pos1 = {r["DAT"]: r["POS"] for r in csv.DictReader(open(UNP / "MEDS-I" / "NIST_SD32_MEDS-I_metadata.csv"))}
    files2 = sorted(SRC.glob("II/data/*/*.jpg"))
    files1 = sorted(SRC.glob("I/img/*.jpg"))
    h2 = {}
    for f in files2:
        h2.setdefault(sha(f.read_bytes()), f)
    rows, stats = [], collections.Counter()
    stats["II_files"], stats["I_files"] = len(files2), len(files1)
    seen = set()
    for f in files2:
        b = f.read_bytes(); h = sha(b)
        if h in seen:
            stats["II_dup_content"] += 1; continue
        seen.add(h)
        if pose2.get(f.name) != "Frontal":
            stats["II_not_frontal"] += 1; continue
        rows.append(("MEDS-II", f, h, b))
    for f in files1:
        b = f.read_bytes(); h = sha(b)
        if h in h2 or h in seen:
            stats["I_in_II_by_content"] += 1; continue
        if pos1.get(f.name) != "F":
            stats["I_not_F"] += 1; continue
        seen.add(h)
        rows.append(("MEDS-I", f, h, b))
    if a.limit:
        rows = rows[:a.limit]
    P = AL.load_pe()
    od = OUT / ("aligned_test" if a.limit else "aligned")
    od.mkdir(parents=True, exist_ok=True)
    out = []
    for k, (part, f, h, b) in enumerate(rows):
        m = re.match(r"S(\d+)-(\d+)-t10_(\d+)\.jpg", f.name)
        img = cv2.imread(str(f))
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bch = img.astype(np.int16)
        chroma = float(((np.abs(bch[..., 2] - bch[..., 1]) + np.abs(bch[..., 1] - bch[..., 0])) / 2).mean())
        pim = Image.open(io.BytesIO(b))
        al, ok, iod = AL.retry(P.align, img)
        iid = f"meds_{k:05d}"
        dst = od / f"{iid}.png"
        cv2.imwrite(str(dst), al)
        out.append(dict(id=iid, part=part, person=f"meds:S{m.group(1)}", encounter=int(m.group(2)), img_in_enc=int(m.group(3)),
                        src_file=str(f), sha256=h, width=img.shape[1], height=img.shape[0], format=pim.format, pil_mode=pim.mode,
                        lap_var=round(float(cv2.Laplacian(grey, cv2.CV_64F).var()), 4), chroma_mean=round(chroma, 4),
                        greyscale=int(pim.mode == "L" or chroma < 1.0), aligned=int(bool(ok)), ied_src=round(float(iod), 4),
                        enlarge=round(132.0 / float(iod), 5) if iod > 0 else "", border_frac=round(float((al.max(2) == 0).mean()), 6),
                        aligned_path=str(dst), aligned_sha256=T.sha(dst)))
    mf = OUT / ("meds_manifest_test.csv" if a.limit else "meds_manifest.csv")
    with open(mf, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    al = [r for r in out if r["aligned"] == 1]
    enc = collections.Counter()
    for r in al:
        enc[r["person"]] = enc.get(r["person"], set()) | {r["encounter"]} if False else enc[r["person"]]
    per = collections.defaultdict(set)
    for r in al:
        per[r["person"]].add(r["encounter"])
    c = dict(selection=dict(stats), images=len(out), persons=len({r["person"] for r in out}), aligned=len(al),
             aligned_persons=len(per), persons_2plus_encounters=sum(len(v) >= 2 for v in per.values()),
             by_part=dict(collections.Counter(r["part"] for r in out)),
             median_ied_src_aligned=st.median(r["ied_src"] for r in al) if al else None,
             p10_p90_ied=[float(np.percentile([r["ied_src"] for r in al], q)) for q in (10, 90)] if al else None,
             median_enlarge=st.median(r["enlarge"] for r in al) if al else None,
             median_lap_var=st.median(r["lap_var"] for r in out), median_border_frac_aligned=st.median(r["border_frac"] for r in al) if al else None,
             greyscale_share=sum(r["greyscale"] for r in out) / len(out), sizes=dict(collections.Counter(f"{r['width']}x{r['height']}" for r in out)),
             manifest=str(mf), manifest_sha256=T.sha(mf), prep_eval_sha256=AL.PE_SHA)
    if not a.limit:
        (T.RES / "meds_counts.json").write_text(json.dumps(c, indent=1))
    print(json.dumps(c, indent=1))


if __name__ == "__main__":
    main()

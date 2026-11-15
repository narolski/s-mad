"""Threshold transfer on unseen genuine sources (TT1), step 2b: align every raw genuine image to the canonical frame.

Alignment path: smadcvpr/prep_eval.py `align(img)` imported UNCHANGED (sha256 pinned below, file never edited), the same
function every other genuine pool of PN1 / AR1 / AF0 / FFHQ-Morphs went through: insightface buffalo_l detection at det
512 (with prep_eval.kps' one retry on a black-padded canvas) -> frontal filter (|nose x - eye-mid x| / IED <= 0.16, |eye
y difference| / IED <= 0.12) -> 2-point eye similarity to the canonical 512x512 frame, eyes at (190,210) and (322,210),
i.e. an inter-eye distance (IED) of 132 px -> lossless PNG (cv2.imwrite, as prep_eval.main). When no face is found or the
frontal filter fails, prep_eval returns a plain 512x512 INTER_AREA resize flagged aligned=0 (eval.csv convention); those
frames are written too (aligned=0) and are not part of the primary scoring pool (decided in the registration).
The input is cv2.imread(raw file), as prep_eval.main's get_native_info. No other image operation.
Recorded per image: detected (a face was found), aligned (prep_eval's flag), ied_src (the IED prep_eval measured in the
source image; 0 if no face), enlarge = 132 / ied_src, fail_reason (no_face / frontal_filter / ""), border_frac (share
of exactly-black pixels of the 512 frame, prep_ffhqm.border_frac), aligned PNG path and sha256.
  python -I align.py [--limit 8] [--manifest raw_manifest.csv]
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys
import time

import cv2
import numpy as np

MC = pathlib.Path("/home/narolski/mambamorph-code")
PE = MC / "smadcvpr" / "prep_eval.py"
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
OUT = pathlib.Path("/mnt/t7/smad_next/TT1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine")
CANON_IED = 322.0 - 190.0


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load_pe():
    assert sha(PE) == PE_SHA, "prep_eval.py is not at its registered pin"
    sys.path.insert(0, str(MC / "smadcvpr"))
    spec = importlib.util.spec_from_file_location("prep_eval", PE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert (m.RX - m.LX) == CANON_IED and m.LY == m.RY
    return m


def retry(fn, *a, tries=20):
    """GB10 is shared: back off and retry on CUDA out-of-memory (as prep_ffhqm.retry)."""
    import torch
    for t in range(tries):
        try:
            return fn(*a)
        except RuntimeError as e:
            if "out of memory" not in str(e).lower() or t == tries - 1:
                raise
            torch.cuda.empty_cache()
            time.sleep(15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--manifest", default=str(OUT / "raw_manifest.csv"))
    a = ap.parse_args()
    P = load_pe()
    rows = list(csv.DictReader(open(a.manifest)))
    if a.limit:
        bys = {}
        for r in rows:
            bys.setdefault(r["source"], [])
            if len(bys[r["source"]]) < a.limit:
                bys[r["source"]].append(r)
        rows = [r for v in bys.values() for r in v]
    adir = OUT / ("aligned_test" if a.limit else "aligned")
    out = []
    t0 = time.time()
    for i, r in enumerate(rows):
        img = cv2.imread(r["raw_path"])
        assert img is not None, r["raw_path"]
        al, ok, iod = retry(P.align, img)
        iod = float(iod)
        dst = adir / r["source"] / f"{r['id']}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dst), al)
        out.append(dict(id=r["id"], source=r["source"], family=r["family"], person=r["person"],
                        detected=int(iod > 0), aligned=int(bool(ok)), ied_src=round(iod, 4),
                        enlarge=round(CANON_IED / iod, 5) if iod > 0 else "",
                        fail_reason="" if ok else ("no_face" if iod <= 0 else "frontal_filter"),
                        border_frac=round(float((al.max(2) == 0).mean()), 6),
                        aligned_path=str(dst), aligned_sha256=sha(dst)))
        if (i + 1) % 1000 == 0:
            print(f"{i + 1}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
    mf = OUT / ("aligned_manifest_test.csv" if a.limit else "aligned_manifest.csv")
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    info = dict(prep_eval=str(PE), prep_eval_sha256=PE_SHA, align_sha256=sha(__file__), rows=len(out),
                input_manifest=a.manifest, input_manifest_sha256=sha(a.manifest),
                aligned_manifest=str(mf), aligned_manifest_sha256=sha(mf), seconds=round(time.time() - t0, 1))
    if not a.limit:
        (RES / "aligned_manifest.csv").write_bytes(mf.read_bytes())
        (RES / "align_run.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()

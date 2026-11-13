"""D5 measurement: source eye distance (ied_src) of the frames in DATA/D5/frames_measured.csv (lead's go, 13 Nov 2026).

Detection only, no image written. The detector is the one the frames' aligner used: scripts/73_delin_align.py is
imported unchanged and its own app() (insightface FaceAnalysis, detection + landmark_2d_106, det_size 512) is called
on the source image the aligner read. As in its align(): largest face, kps[0] and kps[1], iod = |kps1 - kps0|; the
frontal filter is applied as there (frontal = 1 if it passes). onnxruntime here is CPU-only (providers: CPU).
Source image per frame:
  ms1_ffhq : FFHQ-1024 Part<k//10000+1>/<key>.png (ms1common.raw_ffhq)
  celebahq : zip member <index>.png of CelebA-HQ-1024.zip (read into memory, as celebahq_prep.py)
  colorFERET frames (a*.png from train/bona_feret): dmad/data/maps/feret_map.csv -> baselines/webmorph/src_imgs/feret/
  FRGC frames: r6 names <Season>_<still>.png -> nd1/<Season>/<still>.jpg; a*.png from train/bona_frgc ->
             r6_train_sources.csv (verified copy in volatile_backup_20261113) -> nd1/<raw>
Check: from the detected eyes the aligner's similarity M is rebuilt (cv2.estimateAffinePartial2D, the same call) and
the share of the 512 frame that maps outside the source image is computed on the coordinate grid (no image is
warped). It should agree with the measured black-pixel border_frac; the agreement is printed per source.

Load control (lead, 13 Nov 19:38): every onnxruntime session of the loaded app is re-created from the same model file
with intra_op_num_threads = inter_op_num_threads = 1 (CPU provider; the module file is not edited); cv2.setNumThreads(1).
Resumable: rows are appended to frames_ied.partial.csv as they finish; a restart skips frames already in it.

  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 python -I d5_measure_ied.py --workers 2
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import json
import pathlib
import zipfile
from multiprocessing import Pool

import cv2
import numpy as np

MC = pathlib.Path("/home/narolski/mambamorph-code")
T7 = pathlib.Path("/mnt/t7/smad_next")
OUT = T7 / "DATA/D5"
FFHQ = pathlib.Path("/mnt/t7/Datasety/downloads/FFHQ-1024")
ZIP = pathlib.Path("/mnt/t7/Datasety/downloads/CelebA-HQ/CelebA-HQ-1024.zip")
ND1 = pathlib.Path("/mnt/t7/Datasety/FRGC-2.0/FRGC-2.0-dist/nd1")
FER = MC / "baselines/webmorph/src_imgs/feret"
S73 = MC / "scripts/73_delin_align.py"
DA = None
ZF = None
YY, XX = np.mgrid[0:512, 0:512].astype(np.float64)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def da():
    global DA
    if DA is None:
        import onnxruntime as ort
        cv2.setNumThreads(1)
        spec = importlib.util.spec_from_file_location("delin_align", S73)
        DA = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(DA)
        app = DA.app()
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        for m in app.models.values():
            m.session = ort.InferenceSession(m.model_file, so, providers=["CPUExecutionProvider"])
    return DA


def source_of(r, fmap, tsrc, znames):
    p = pathlib.Path(r["path"])
    if r["source"] == "ms1_ffhq":
        k = int(p.stem)
        return "file", str(FFHQ / f"Part{k // 10000 + 1}" / f"{k:05d}.png")
    if r["source"] == "celebahq":
        n = znames.get(p.stem)
        return ("zip", n) if n else (None, "not_in_zip")
    db = r["person"].split(":")[0]
    if db == "feret":
        m = fmap.get(p.name)
        return ("file", str(FER / m["src"])) if m else (None, "no_feret_map")
    if p.name.startswith("a"):
        raw = tsrc.get(f"train/bona_frgc/{p.name}")
        return ("file", str(ND1 / raw)) if raw else (None, "no_frgc_train_source")
    season, still = p.stem.split("_", 1)
    return "file", str(ND1 / season / f"{still}.jpg")


def measure(job):
    global ZF
    r, kind, src = job
    out = dict(r, src_kind=kind or "", src=src if kind != "zip" else f"zip:{src}", ied_src="", frontal="",
               n_faces="", src_h="", src_w="", border_geom="", note="")
    if kind is None:
        out["note"] = src
        return out
    if kind == "zip":
        if ZF is None:
            ZF = zipfile.ZipFile(ZIP)
        img = cv2.imdecode(np.frombuffer(ZF.read(src), np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(src)
    if img is None:
        out["note"] = "source_unreadable"
        return out
    fc = da().app().get(img)
    out.update(n_faces=len(fc), src_h=img.shape[0], src_w=img.shape[1])
    if not fc:
        out["note"] = "no_face"
        return out
    f = max(fc, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    le, re, nose = f.kps[0], f.kps[1], f.kps[2]
    iod = float(np.linalg.norm(re - le))
    emid = (le + re) / 2
    out["ied_src"] = round(iod, 4)
    out["frontal"] = int(not (iod < 1 or abs(nose[0] - emid[0]) / iod > 0.16 or abs(le[1] - re[1]) / iod > 0.12))
    M = cv2.estimateAffinePartial2D(np.float32([le, re]), np.float32([[da().LX, da().LY], [da().RX, da().RY]]))[0]
    if M is not None:
        Mi = cv2.invertAffineTransform(M)
        sx = Mi[0, 0] * XX + Mi[0, 1] * YY + Mi[0, 2]
        sy = Mi[1, 0] * XX + Mi[1, 1] * YY + Mi[1, 2]
        h, w = img.shape[:2]
        outside = (sx < 0) | (sy < 0) | (sx > w - 1) | (sy > h - 1)
        out["border_geom"] = round(float(outside.mean()), 6)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(OUT / "frames_measured.csv")))
    if a.limit:
        by = collections.defaultdict(list)
        for r in rows:
            if len(by[r["source"]]) < a.limit // 4 + 1:
                by[r["source"]].append(r)
        rows = [r for v in by.values() for r in v][: a.limit + 4]
    fmap = {r["aligned"]: r for r in csv.DictReader(open(MC / "dmad/data/maps/feret_map.csv"))}
    tsrc = {r["train_path"]: r["raw"] for r in csv.DictReader(open(T7 / "volatile_backup_20261113/r6_train_sources.csv"))
            if r["db"] == "frgc" and r["subject"] == r["train_subject"]}
    znames = {pathlib.Path(n).stem: n for n in zipfile.ZipFile(ZIP).namelist() if n.endswith(".png")}
    part = OUT / ("frames_ied.partial.csv" if not a.limit else "frames_ied_test.partial.csv")
    done = {}
    if part.exists():
        for x in csv.DictReader(open(part)):
            done[x["path"]] = x
    jobs = [(r,) + source_of(r, fmap, tsrc, znames) for r in rows if r["path"] not in done]
    print(f"resume: {len(done)} done, {len(jobs)} to do", flush=True)
    cols = list(rows[0].keys()) + ["src_kind", "src", "ied_src", "frontal", "n_faces", "src_h", "src_w", "border_geom", "note"]
    cols = list(dict.fromkeys(cols))
    new = not part.exists()
    with open(part, "a", newline="") as f, Pool(a.workers) as pool:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        for i, x in enumerate(pool.imap_unordered(measure, jobs, chunksize=8)):
            w.writerow(x)
            done[x["path"]] = x
            if (i + 1) % 500 == 0:
                f.flush()
                print(f"{i + 1}/{len(jobs)}", flush=True)
    order = {r["path"]: k for k, r in enumerate(rows)}
    res = sorted((d for d in done.values() if d["path"] in order), key=lambda d: order[d["path"]])
    assert len(res) == len(rows)
    p = OUT / ("frames_ied.csv" if not a.limit else "frames_ied_test.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(res)
    summ = {}
    for s in sorted({x["source"] for x in res}):
        v = [x for x in res if x["source"] == s]
        ok = [x for x in v if str(x["ied_src"]) != ""]
        agree = [x for x in ok if str(x["border_geom"]) != "" and abs(float(x["border_geom"]) - float(x["border_frac"])) <= 0.02]
        ied = sorted(float(x["ied_src"]) for x in ok)
        summ[s] = dict(frames=len(v), measured=len(ok), notes=dict(collections.Counter(x["note"] for x in v)),
                       frontal_pass=sum(str(x["frontal"]) == "1" for x in ok),
                       border_agree_within_0p02=len(agree),
                       ied_median=ied[len(ied) // 2] if ied else None,
                       ied_p10=ied[len(ied) // 10] if ied else None, ied_p90=ied[9 * len(ied) // 10] if ied else None)
    summ["_file"] = dict(path=str(p), sha256=sha(p), s73_sha256=sha(S73))
    json.dump(summ, open(OUT / ("ied_summary.json" if not a.limit else "ied_summary_test.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()

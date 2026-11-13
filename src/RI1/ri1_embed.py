"""Regional identity disagreement (RI1): glintr100 embeddings of the unoccluded and 8 constant-colour-occluded
112 x 112 crops of each image (lead's ruling 13 Nov: blanking regions of the aligned FR crop with a constant colour in
memory is the allowed constant-colour blanking; no blanked image is stored). Route: prep_eval.kps (unchanged; its
detector object is set to a CPU insightface FaceAnalysis, buffalo_l detection, det_size 512, the same model and size)
-> insightface norm_crop -> glintr100.onnx through insightface ArcFaceONNX.get_feat on onnxruntime CPU (a2f_common's
CUDA session swap is not used: the DGX GPU is busy; every RI1 embedding is made on this one CPU platform).
Parts: rows (FS1 ladder/splice rungs of the 291 dev+test hosts), sources (pool H, S, B, R photos), ffhq (first 1,000
ffhq_bona_orig of the FS1 list by id). Out: /mnt/t7/smad_next/RI1/emb_<part>_<shard>.npz (ids, emb [n, 9, 512], found).
  python3 -I ri1_embed.py PART --shard K/N [--limit 8]"""
import argparse
import csv
import hashlib
import importlib.util
import os
import pathlib
import sys

import numpy as np

PE_PATH = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr/prep_eval.py")
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
GLINT = pathlib.Path("/home/narolski/.insightface/models/antelopev2/glintr100.onnx")
MAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
EVAL = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data")
POOL = pathlib.Path("/mnt/t7/smad_next/AR1/pool.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/RI1")
GREY = 128
# occlusion boxes in the 112 x 112 ArcFace crop (template eyes (38.3, 51.7), (73.5, 51.5); nose (56.0, 71.7); mouth
# corners (41.5, 92.4), (70.7, 92.2)); integer slices (y0, y1, x0, x1)
BOXES = (("left_eye", (40, 64, 24, 54)), ("right_eye", (40, 64, 58, 88)), ("nose", (58, 84, 44, 68)),
         ("mouth", (82, 104, 34, 78)), ("upper", (0, 56, 0, 112)), ("lower", (56, 112, 0, 112)),
         ("left", (0, 112, 0, 56)), ("right", (0, 112, 56, 112)))
LAD = ("R0", "R2w4", "R3", "R4")
SPL = ("S0", "S3", "S4")


def rows(part):
    if part == "rows":
        R = []
        for r in csv.DictReader(open(MAN)):
            if r["role"] not in ("dev", "test"):
                continue
            if r["fam"] == "ladder" and r["rung"] in LAD and (r["strength"] == "" or (r["rung"] == "R0" and r["strength"] == "61")) \
                    and r["tool"] in ("opencv", "none", "facemorpher"):
                R.append((r["id"], str(EVAL / r["path"])))
            elif r["fam"] == "splice" and r["rung"] in SPL:
                R.append((r["id"], str(EVAL / r["path"])))
        return sorted(R)
    if part == "sources":
        S = set()
        hosts = {r["host"] for r in csv.DictReader(open(MAN)) if r["fam"] == "splice" and r["role"] in ("dev", "test")}
        for r in csv.DictReader(open(POOL)):
            if r["pid"] in hosts:
                for k in ("H", "S", "B", "R"):
                    if r[k]:
                        S.add(r[k])
        return sorted((p, p) for p in S)
    if part == "ffhq":
        F = sorted([(r["id"], str(EVAL / r["path"])) for r in csv.DictReader(open(MAN)) if r["rung"] == "ffhq_bona_orig"])
        return F[:1000]
    raise SystemExit(part)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    assert hashlib.sha256(PE_PATH.read_bytes()).hexdigest() == PE_SHA
    import cv2
    import onnxruntime as ort
    from insightface.app import FaceAnalysis
    from insightface.model_zoo import get_model
    from insightface.utils.face_align import norm_crop
    cv2.setNumThreads(1)
    sys.path.insert(0, str(PE_PATH.parent.parent))
    spec = importlib.util.spec_from_file_location("prep_eval", PE_PATH)
    PE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PE)
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
    app.prepare(ctx_id=-1, det_size=(512, 512))
    PE._APP = app                                    # CPU detector object; prep_eval.kps itself unchanged
    so = ort.SessionOptions()
    so.intra_op_num_threads = int(os.environ.get("OMP_NUM_THREADS", "2"))
    so.inter_op_num_threads = 1
    m = get_model(str(GLINT), providers=["CPUExecutionProvider"])
    m.session = ort.InferenceSession(str(GLINT), sess_options=so, providers=["CPUExecutionProvider"])
    k, n = map(int, a.shard.split("/"))
    R = rows(a.part)[k::n][: a.limit or None]
    ids, E, F = [], [], []
    for j, (i, p) in enumerate(R):
        img = cv2.imread(p)
        kp = PE.kps(img) if img is not None else None
        if kp is None:
            ids.append(i)
            E.append(np.zeros((9, 512), np.float32))
            F.append(False)
            continue
        c0 = norm_crop(img, kp)
        crops = [c0]
        for _, (y0, y1, x0, x1) in BOXES:
            c = c0.copy()
            c[y0:y1, x0:x1] = GREY
            crops.append(c)
        e = m.get_feat(crops).astype(np.float32)
        e /= np.linalg.norm(e, axis=1, keepdims=True)
        ids.append(i)
        E.append(e)
        F.append(True)
        if (j + 1) % 100 == 0:
            print(a.part, k, j + 1, len(R), flush=True)
    tag = f"emb_{a.part}_{k}of{n}" + (f"_limit{a.limit}" if a.limit else "")
    f = OUT / f"{tag}.npz"
    if f.exists():
        sys.exit(f"{f} exists; refusing to overwrite")
    np.savez(f, ids=np.array(ids), emb=np.stack(E), found=np.array(F), boxes=np.array([b for b, _ in BOXES]))
    print("DONE", tag, len(ids), int(np.sum(F)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

"""Mirror-asymmetry test (AS0), step 2: 106-point landmarks for the images that have no .tem file (measurement only).

Model: insightface buffalo_l (det_10g + 2d106det), the model pack 73_delin_align.py and prep_eval.py use, on the CPU
(onnxruntime CPUExecutionProvider; intra-op threads limited to --threads). Largest face kept (as 73_delin_align).
det_size 512 x 512 as in both record scripts. No image is written.

  python3 -I as0_landmarks.py [--limit 8] [--sets G,Fm,D,M,Ds,Fe,X] [--threads 2] [--chunk 128]
Writes /mnt/t7/smad_next/AS0/lm/part_<set>_<k>.npz (resumable) and, with --merge, lm/landmarks.npz.
"""
import argparse
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402

ORDER = ("G", "Fm", "D", "M", "Ds", "Fe", "X")


def make_app(threads):
    import onnxruntime as ort
    base = ort.InferenceSession

    class Limited(base):
        def __init__(self, path, sess_options=None, *a, **kw):
            so = sess_options or ort.SessionOptions()
            so.intra_op_num_threads = threads
            so.inter_op_num_threads = 1
            kw["providers"] = ["CPUExecutionProvider"]
            super().__init__(path, so, *a, **kw)
    ort.InferenceSession = Limited
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "landmark_2d_106"],
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(512, 512))
    return app


def detect(app, path):
    import cv2
    img = cv2.imread(str(K.guard(path)), cv2.IMREAD_COLOR)
    if img is None:
        return None
    fc, pad = app.get(img), 0
    if not fc:      # tight crops (A43 stored frames): retry on an in-memory copy padded with black (detector input only)
        pad = max(img.shape[:2]) // 2
        fc = app.get(cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0)))
    if not fc:
        return dict(n=0, h=img.shape[0], w=img.shape[1], pad=pad)
    f = max(fc, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    return dict(n=len(fc), lm=f.landmark_2d_106.astype(np.float32) - pad, kps=f.kps.astype(np.float32) - pad,
                score=float(f.det_score), bbox=f.bbox.astype(np.float32) - pad, h=img.shape[0], w=img.shape[1],
                pad=pad)


def save_part(path, ids, res):
    N = len(ids)
    lm = np.full((N, 106, 2), np.nan, np.float32)
    kps = np.full((N, 5, 2), np.nan, np.float32)
    sc, nf, hw = np.zeros(N, np.float32), np.zeros(N, np.int16), np.zeros((N, 2), np.int32)
    pad = np.zeros(N, np.int32)
    for i, r in enumerate(res):
        if r is None:
            nf[i] = -1
            continue
        nf[i], hw[i], pad[i] = r["n"], (r["h"], r["w"]), r["pad"]
        if r["n"] > 0:
            lm[i], kps[i], sc[i] = r["lm"], r["kps"], r["score"]
    np.savez(path, ids=np.array(ids), lm=lm, kps=kps, score=sc, n_faces=nf, hw=hw, pad=pad)


def merge():
    parts = sorted((K.OUT / "lm").glob("part_*.npz"))
    acc = {k: [] for k in ("ids", "lm", "kps", "score", "n_faces", "hw", "pad")}
    for p in parts:
        with np.load(p, allow_pickle=False) as z:
            for k in acc:
                acc[k].append(z[k])
    out = {k: np.concatenate(v) for k, v in acc.items()}
    assert len(set(out["ids"].tolist())) == len(out["ids"])
    np.savez(K.OUT / "lm/landmarks.npz", **out)
    print("merged", len(out["ids"]), "no face", int((out["n_faces"] == 0).sum()), "unreadable",
          int((out["n_faces"] < 0).sum()), "multi", int((out["n_faces"] > 1).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sets", default=",".join(ORDER))
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--chunk", type=int, default=128)
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    (K.OUT / "lm").mkdir(parents=True, exist_ok=True)
    if a.merge:
        return merge()
    items = [r for r in K.read_csv(K.OUT / "items.csv") if r["lm"] == "det"]
    app = make_app(a.threads)
    for s in a.sets.split(","):
        rows = [r for r in items if r["set"] == s]
        if a.limit:
            rows = rows[: a.limit]
        for k in range(0, len(rows), a.chunk):
            part = K.OUT / "lm" / (f"smoke_{s}_{k:05d}.npz" if a.limit else f"part_{s}_{k:05d}.npz")
            if part.exists():
                continue
            ch = rows[k: k + a.chunk]
            t0 = time.time()
            res = [detect(app, r["path"]) for r in ch]
            save_part(part, [r["id"] for r in ch], res)
            print(f"{s} {k + len(ch)}/{len(rows)} {time.time() - t0:.1f}s "
                  f"noface {sum(1 for r in res if r and r['n'] == 0)}", flush=True)


if __name__ == "__main__":
    main()

"""SM1 landmarks (+ ArcFace embeddings where needed) for SMDD morph-source renders (os25k_m_t), which have none.

Existing detector, unchanged: insightface buffalo_l models, CPU, det_size 512, largest face, landmark_2d_106 points
normalised by the image size -- the smadcvpr/build_arms._if106_one call (FaceAnalysis.get's own steps: det_model.detect,
then each model's get on the face); the recognition model (normed_embedding) runs only for rows that need it.
No pixel is changed or written. One ONNX thread per worker process (6 workers).
Stages (each its own file, so later stages can start early):
  pool    3,000 seeded non-contributors (Part 2 keys, unused and placebo partners) + the 5 trained partners, with
          embeddings; + 20 os25k_bf_t renders (reproduction check against smdd_bona_landmarks_if106.npz, tol 0.05 px)
  contrib the 3,858 contributors of the training release (landmarks only; the 5 partners again, with embeddings)
  extra   6,000 more seeded non-contributors, disjoint from pool (amendment A1.3, arm b'; landmarks only)

  python3 -I landmarks.py --stage pool|contrib|extra [--limit 8] [--workers 6]
-> OUT/lm/srcm_if106_<stage>.npz (names, split, lms (n,106,2) normalised, det_score, emb (n,512), NaN if not run)
   and RES/lm_check_<stage>.json
"""
import argparse
import json
import pathlib
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

_IF = {}


def _init():
    import onnxruntime as ort
    orig = ort.InferenceSession.__init__

    def init1(self, path, sess_options=None, **kw):
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        orig(self, path, sess_options=so, **kw)
    ort.InferenceSession.__init__ = init1
    import cv2
    cv2.setNumThreads(1)
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "landmark_2d_106", "recognition"],
                       providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(512, 512))
    _IF["app"] = app


def _one(job):
    import cv2
    from insightface.app.common import Face
    path, want_emb = job
    app = _IF["app"]
    img = cv2.imread(str(path))
    nan = (np.full((106, 2), np.nan, np.float32), 0.0, np.full(512, np.nan, np.float32))
    if img is None:
        return nan
    bb, kp = app.det_model.detect(img, max_num=0, metric="default")
    if bb.shape[0] == 0:
        return nan
    i = int(np.argmax((bb[:, 2] - bb[:, 0]) * (bb[:, 3] - bb[:, 1])))      # largest face (as _if106_one)
    f = Face(bbox=bb[i, 0:4], kps=None if kp is None else kp[i], det_score=bb[i, 4])
    app.models["landmark_2d_106"].get(img, f)
    emb = nan[2]
    if want_emb:
        app.models["recognition"].get(img, f)
        emb = f.normed_embedding.astype(np.float32)
    lm = (f.landmark_2d_106 / np.array([img.shape[1], img.shape[0]], np.float32)).astype(np.float32)
    return lm, float(f.det_score), emb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("pool", "contrib", "extra", "evalp"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    if a.stage == "extra":
        print("stage extra dropped by amendment A2 (prereg.md)")
        return
    if a.stage == "evalp":                        # A3: the 5 evaluation-split partners (os25k_m_e), with embeddings
        rows = [("evalp", n, K.SRC_E / f"{n}.png", True) for n in K.EVAL_PARTNERS]
        return run(a, rows)
    pairs = K.release_pairs()
    contrib = sorted({x for p in pairs for x in p})
    src_all = sorted(x.name[:-4] for x in K.SRC_T.iterdir() if x.suffix == ".png")
    rest = sorted(set(src_all) - set(contrib))
    pool = sorted(np.random.default_rng(K.SEED).choice(rest, size=3000, replace=False).tolist())
    if a.stage == "pool":
        bf_check = sorted(K.load_if106())[:: 25000 // 20][:20]
        rows = [("pool", n, K.SRC_T / f"{n}.png", True) for n in pool] + \
               [("partner", n, K.SRC_T / f"{n}.png", True) for n in K.PARTNERS] + \
               [("bfcheck", n, K.BF_T / f"{n}.png", False) for n in bf_check]
    elif a.stage == "contrib":
        rows = [("contrib", n, K.SRC_T / f"{n}.png", n in K.PARTNERS) for n in contrib]
    else:
        rest2 = sorted(set(rest) - set(pool))
        extra = sorted(np.random.default_rng(K.SEED + 7).choice(rest2, size=6000, replace=False).tolist())
        rows = [("extra", n, K.SRC_T / f"{n}.png", False) for n in extra]
    if a.limit:
        rows = rows[: a.limit] + [r for r in rows if r[0] == "bfcheck"][:4]
    run(a, rows)


def run(a, rows):
    t0 = time.time()
    res = []
    with Pool(a.workers, initializer=_init) as p:
        for i, r in enumerate(p.imap(_one, [(r[2], r[3]) for r in rows], chunksize=4)):
            res.append(r)
            if (i + 1) % 250 == 0:
                print(f"PROGRESS {i + 1}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
    dt = time.time() - t0
    lms = np.stack([r[0] for r in res])
    det = np.array([r[1] for r in res], np.float32)
    emb = np.stack([r[2] for r in res])
    (K.OUT / "lm").mkdir(parents=True, exist_ok=True)
    tag = a.stage + ("" if not a.limit else f"_limit{a.limit}")
    np.savez(K.OUT / f"lm/srcm_if106_{tag}.npz", names=np.array([r[1] for r in rows]),
             split=np.array([r[0] for r in rows]), lms=lms, det_score=det, emb=emb)
    ok = np.isfinite(lms).all(axis=(1, 2))
    log = dict(stage=a.stage, n=len(rows), seconds=round(dt, 1), images_per_minute=round(60 * len(rows) / dt, 1),
               workers=a.workers, no_face=int((~ok).sum()), no_face_names=[rows[i][1] for i in np.where(~ok)[0]][:50],
               with_embedding=int(sum(r[3] for r in rows)))
    chk = [i for i, r in enumerate(rows) if r[0] == "bfcheck"]
    if chk:
        ref = K.load_if106()
        d = [float(np.nanmax(np.abs(lms[i] - ref[rows[i][1]])) * 256) for i in chk]
        log.update(bfcheck_max_abs_px_vs_if106=d, bfcheck_pass=bool(max(d) <= 0.05))
    json.dump(log, open(K.RES / f"lm_check_{tag}.json", "w"), indent=1)
    print(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()

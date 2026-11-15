"""Lead request (11 Nov): two more one-person rungs, both pools, both tools, PNG in the same 512 frame.

R2w  warp-only: H warped by the tool's OWN warp routine to the mean shape of H and its same-person photo S
     (FRLL: neutral + smiling), texture from H only, no blending.
       OpenCV      : scripts/68_hires_morph.py (the module 78_tool_morph.py loads): morph()'s own geometry
                     (LA = H points + the 8 frame corners, LM = (LA + LS) / 2, cv2.Subdiv2D on LM) and its unchanged
                     _warp_tri for H only; the B-side warp and the 0.5 blend are dropped.
       FaceMorpher : baselines/face_morpher warper.warp_image(H, rint(pH), rint((pH + pS) / 2)) as 96_facemorpher_tool
                     calls it, blender.mask_from_points, blender.overlay_image over H itself (no averaged background).
R2wm warp-only toward H's own mirrored shape (lead request 2): as R2w with S replaced by Hm (mean of H's points and its
     mirrored, re-indexed points); uses the H file only (the clean FRLL one-person control, no smiling photo).
R2w4 warp-only toward the two-person mean shape (amendment 4): as R2w with S replaced by B, the R4 partner, so the
     geometry equals R4's; primary pool only.
R3m  mirror self-morph: the unchanged tool on (H, Hm), Hm = cv2.flip(H, 1) (lossless), Hm's .tem = the mirrored
     coordinates (x -> W-1-x) re-indexed by the measured 106-point left-right permutation (mirror_perm106.json).
     Built by build.py (role R3m) from pool_m.csv / pool_frll_m.csv written here.

  python3 -I variants.py mirror            -> OUT/mirror/<pool>/<stem>.png|.tem, OUT/pool_m.csv, OUT/pool_frll_m.csv
  python3 -I variants.py warp [--limit 8]  -> OUT/img/<pool>/<tool>/R2w/<stem>.png (+ timing log)
"""
import argparse
import csv
import json
import pathlib
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

POOLS = (("frgcferet", "pool.csv", "pool_m.csv"), ("frll", "pool_frll.csv", "pool_frll_m.csv"))
FM = K.MC / "baselines/face_morpher/facemorpher"


def write_tem(path, pts):
    with open(path, "w") as fo:                       # 73_delin_align.write_tem's format
        fo.write(f"{len(pts)}\n")
        for x, y in pts:
            fo.write(f"{float(x):.4f}\t{float(y):.4f}\n")
        fo.write("0\n")


def mirror():
    import cv2
    import numpy as np
    perm = np.array(json.load(open(K.OUT / "mirror_perm106.json"))["perm"])
    assert (perm[perm] == np.arange(106)).all()
    for pool, src, dst in POOLS:
        rows = list(csv.DictReader(open(K.OUT / src)))
        d = K.OUT / "mirror" / pool
        d.mkdir(parents=True, exist_ok=True)
        for r in rows:
            out = d / (r["pid"].replace(":", "_") + ".png")
            img = cv2.imread(r["H"])
            W = img.shape[1]
            fl = cv2.flip(img, 1)
            if not out.exists():
                cv2.imwrite(str(out), fl)
            assert (cv2.imread(str(out)) == fl).all()
            lm = K.read_tem(r["H"][:-4] + ".tem")
            m = lm[perm].copy()
            m[:, 0] = W - 1 - m[:, 0]
            write_tem(str(out)[:-4] + ".tem", m)
            r["M"] = str(out)
        with open(K.OUT / dst, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(pool, len(rows), "mirrors")


def _load(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def warp_cv(imgA, lmA, lmS, hm):
    """68_hires_morph.morph's geometry and _warp_tri, A side only (no B warp, no blend)."""
    import cv2
    import numpy as np
    H, W = imgA.shape[:2]
    corners = np.float32([[0, 0], [W // 2, 0], [W - 1, 0], [0, H // 2], [W - 1, H // 2], [0, H - 1], [W // 2, H - 1],
                          [W - 1, H - 1]])
    LA = np.vstack([lmA, corners]); LB = np.vstack([lmS, corners]); LM = (LA + LB) / 2
    sub = cv2.Subdiv2D((0, 0, W, H))
    for p in LM:
        sub.insert((float(np.clip(p[0], 0, W - 1)), float(np.clip(p[1], 0, H - 1))))
    tris = sub.getTriangleList()

    def idx(pt):
        d = np.sum((LM - pt) ** 2, 1); return int(np.argmin(d))
    wA = np.zeros_like(imgA, np.float32)
    for t in tris:
        pts = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]; ids = [idx(p) for p in pts]
        hm._warp_tri(imgA.astype(np.float32), wA, [LA[i] for i in ids], [LM[i] for i in ids])
    return np.clip(wA, 0, 255).astype(np.uint8)


def warp_fm(img1, pts1, pts2, warper, blender):
    """96_facemorpher_tool.fm_morph with the second image's texture dropped: H warped to the mean points, composited
    over H itself."""
    import numpy as np
    size = img1.shape[:2]
    pts = np.rint((pts1 + pts2) / 2.0).astype(int)
    f1 = warper.warp_image(img1, np.rint(pts1).astype(int), pts, size)
    mask = blender.mask_from_points(size, pts)
    return blender.overlay_image(f1, mask, img1.copy())


def one(job):
    import cv2
    tool, out, hp, sp = job
    if pathlib.Path(out).exists():
        return 1
    h = cv2.imread(hp)
    lh, ls = K.read_tem(hp[:-4] + ".tem"), K.read_tem(sp[:-4] + ".tem")
    if tool == "opencv":
        img = warp_cv(h, lh, ls, _load(K.MC / "scripts/68_hires_morph.py", "hm68"))
    else:
        img = warp_fm(h, lh, ls, _load(FM / "warper.py", "warper"), _load(FM / "blender.py", "blender"))
    cv2.imwrite(out, img)
    return 1


def warp(limit, workers, target="S", rung="R2w", pools=("frgcferet", "frll")):
    """target S: R2w (toward the same-person photo's shape); target M: R2wm (toward H's own mirrored shape, H file only)."""
    log = {}
    for tool in ("opencv", "facemorpher"):
        jobs = []
        for pool, src, msrc in POOLS:
            if pool not in pools:
                continue
            rows = list(csv.DictReader(open(K.OUT / (src if target == "S" else msrc))))[: limit or None]
            d = K.OUT / "img" / (pool if not limit else "smoke_" + pool) / tool / rung
            d.mkdir(parents=True, exist_ok=True)
            jobs += [(tool, str(d / (r["pid"].replace(":", "_") + ".png")), r["H"], r[target]) for r in rows]
        t0 = time.time()
        with Pool(workers) as p:
            n = sum(p.map(one, jobs, chunksize=8))
        dt = time.time() - t0
        log[tool] = dict(images=n, seconds=round(dt, 1), images_per_minute=round(60 * n / dt, 1))
        print(tool, log[tool], flush=True)
    log["s68_sha256"] = K.sha(K.MC / "scripts/68_hires_morph.py")
    log["warper_sha256"], log["blender_sha256"] = K.sha(FM / "warper.py"), K.sha(FM / "blender.py")
    json.dump(log, open(K.OUT / (f"{rung.lower()}_log.json" if not limit else f"{rung.lower()}_log_smoke.json"), "w"),
              indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("mirror", "warp", "warpmirror", "warp2"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    if a.stage == "mirror":
        mirror()
    elif a.stage == "warp":
        warp(a.limit, a.workers)
    elif a.stage == "warpmirror":
        warp(a.limit, a.workers, target="M", rung="R2wm")
    else:                                              # R2w4: toward the R4 mean shape (H and B), primary pool only
        warp(a.limit, a.workers, target="B", rung="R2w4", pools=("frgcferet",))


if __name__ == "__main__":
    main()

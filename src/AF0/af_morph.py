"""AF0 morph engine with a per-pixel mixing field a(x).

Reuses the UNCHANGED Delaunay engine `scripts/68_hires_morph.py`, loaded exactly as `scripts/78_tool_morph.py`
loads it (we load 78 itself and use its `hm` module object and its `parse_tem`). Nothing of the warp is
re-implemented: `hm.morph(a, la, b, lb)` runs unchanged; while it runs, its module-level `_warp_tri` is wrapped by a
recorder that only remembers the destination arrays (the engine's own float32 warped images wA, wB) and the
destination triangles, then calls the original `_warp_tri`. After the call the wrapper is removed.

New arithmetic (the only one on pixels): out = clip((1 - a) * wA + a * wB, 0, 255).astype(uint8), the same clip and
cast the engine uses for its 0.5 blend (so a = 0.5 everywhere reproduces it bit-for-bit).

The field a(x): values are defined on the vertices of the engine's own triangulation (the 106 landmarks of the mean
shape LM = (LA + LB) / 2, plus the 8 frame points the engine adds: 4 corners and 4 edge midpoints) and interpolated
linearly (barycentric) inside each triangle the engine warped, in the engine's own order; so a(x) is continuous, with
no seams. Outside the face hull the engine blends the whole frame at 0.5 through those 8 frame vertices; here the 8
frame vertices carry the mean of the field over the 106 landmark vertices, so triangles between the hull and the frame
interpolate between the hull values and that mean (for uniform fields: the constant itself; a = 0.5 is the engine).
Field types (on the 106 landmark vertices):
  zero  : 0                              u25 : 0.25                      u50 : 0.5
  grad  : 0.5 * (p - min p) / (max p - min p), p = projection of the vertex on a random unit direction
  bump  : min(0.5, sum_k 0.5 * exp(-|v - c_k|^2 / (2 s_k^2))), k = 1 or 2 bumps, c_k = random landmarks,
          s_k = U(0.15, 0.30) * face size (face size = diagonal of the landmark bounding box)

  python3 -I af_morph.py verify --n 8                 (a = 0.5 vs the unchanged engine, 8 pairs)
  python3 -I af_morph.py build --manifest M.csv --workers 6 [--wave 1] [--limit 8]
"""
import argparse
import csv
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np

MC = pathlib.Path("/home/narolski/mambamorph-code")
S78 = MC / "scripts" / "78_tool_morph.py"
S68 = MC / "scripts" / "68_hires_morph.py"
OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
FIELDS = ("zero", "u25", "u50", "grad", "bump")

_spec = importlib.util.spec_from_file_location("tool78", S78)
tool78 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool78)          # module top-level loads 68 as "hm68", exactly as 78 does
hm = tool78.hm
parse_tem = tool78.parse_tem


def warped_pair(imgA, lmA, imgB, lmB):
    """Run the unchanged engine once; return its warped float32 images, its 0.5 morph, and its triangles."""
    rec = dict(dst=[], tris=[])
    orig = hm._warp_tri

    def recorder(src, dst, tri_s, tri_d):
        if not any(dst is d for d in rec["dst"]):
            rec["dst"].append(dst)
        if dst is rec["dst"][0]:
            rec["tris"].append(np.float32(tri_d))
        return orig(src, dst, tri_s, tri_d)

    hm._warp_tri = recorder
    try:
        m05 = hm.morph(imgA, lmA, imgB, lmB)
    finally:
        hm._warp_tri = orig
    assert len(rec["dst"]) == 2, "engine structure changed"
    return rec["dst"][0], rec["dst"][1], m05, rec["tris"]


def mean_shape(imgA, lmA, lmB):
    """Vertex set of the engine (same expression as hm.morph): landmarks + 8 frame points, averaged."""
    H, W = imgA.shape[:2]
    corners = np.float32([[0, 0], [W // 2, 0], [W - 1, 0], [0, H // 2], [W - 1, H // 2], [0, H - 1], [W // 2, H - 1],
                          [W - 1, H - 1]])
    return (np.vstack([lmA, corners]) + np.vstack([lmB, corners])) / 2


def vertex_field(kind, LM, n_lm, rng):
    v = LM[:n_lm].astype(np.float64)
    info = {}
    if kind == "zero":
        f = np.zeros(n_lm)
    elif kind == "u25":
        f = np.full(n_lm, 0.25)
    elif kind == "u50":
        f = np.full(n_lm, 0.5)
    elif kind == "grad":
        th = rng.uniform(0, 2 * np.pi)
        p = v @ np.array([np.cos(th), np.sin(th)])
        f = 0.5 * (p - p.min()) / (p.max() - p.min())
        info = dict(theta=round(float(th), 6))
    elif kind == "bump":
        k = int(rng.integers(1, 3))
        size = float(np.hypot(*(v.max(0) - v.min(0))))
        cs = rng.choice(n_lm, size=k, replace=False)
        ss = rng.uniform(0.15, 0.30, size=k) * size
        f = np.zeros(n_lm)
        for c, s in zip(cs, ss):
            f += 0.5 * np.exp(-((v - v[c]) ** 2).sum(1) / (2 * s * s))
        f = np.minimum(f, 0.5)
        info = dict(k=k, centres=[int(c) for c in cs], sigma=[round(float(s), 3) for s in ss])
    else:
        raise ValueError(kind)
    full = np.concatenate([f, np.full(len(LM) - n_lm, f.mean())])
    return full, info


def pixel_field(shape, LM, fv, tris):
    """Barycentric interpolation of vertex values inside each engine triangle (engine order, later overwrites)."""
    H, W = shape[:2]
    import cv2
    tid = np.zeros((H, W), np.int32)
    idx = []
    for t, tri in enumerate(tris):
        ids = [int(np.argmin(((LM - p) ** 2).sum(1))) for p in tri]
        idx.append(ids)
        cv2.fillConvexPoly(tid, np.int32(tri), t + 1)
    out = np.full((H, W), np.nan, np.float64)
    yy, xx = np.mgrid[0:H, 0:W]
    for t, ids in enumerate(idx):
        m = tid == t + 1
        if not m.any():
            continue
        P = LM[ids].astype(np.float64)
        T = np.array([[P[0, 0] - P[2, 0], P[1, 0] - P[2, 0]], [P[0, 1] - P[2, 1], P[1, 1] - P[2, 1]]])
        if abs(np.linalg.det(T)) < 1e-9:
            out[m] = fv[ids].mean()
            continue
        Ti = np.linalg.inv(T)
        dx, dy = xx[m] - P[2, 0], yy[m] - P[2, 1]
        l1 = Ti[0, 0] * dx + Ti[0, 1] * dy
        l2 = Ti[1, 0] * dx + Ti[1, 1] * dy
        out[m] = l1 * fv[ids[0]] + l2 * fv[ids[1]] + (1 - l1 - l2) * fv[ids[2]]
    nan = np.isnan(out)
    out[nan] = fv[len(fv) - 8:].mean()     # pixels no engine triangle covers (none expected): the frame value
    return np.clip(out, fv.min(), fv.max()), int(nan.sum())


def af_morph(imgA, lmA, imgB, lmB, kind, rng):
    wA, wB, m05, tris = warped_pair(imgA, lmA, imgB, lmB)
    LM = mean_shape(imgA, lmA, lmB)
    fv, info = vertex_field(kind, LM, len(lmA), rng)
    a, n_unc = pixel_field(imgA.shape, LM, fv, tris)
    a32 = a.astype(np.float32)[..., None]
    out = np.clip((1 - a32) * wA + a32 * wB, 0, 255).astype(np.uint8)
    info["uncovered_px"] = n_unc
    return out, a.astype(np.float16), LM[: len(lmA)].astype(np.float32), m05, info


def _job(r):
    import cv2
    cv2.setNumThreads(1)
    img, amap = pathlib.Path(r["image"]), pathlib.Path(r["map"])
    if img.exists() and amap.exists():
        return r["id"], "exists", None
    a, b = cv2.imread(r["A"]), cv2.imread(r["B"])
    la, lb = parse_tem(r["A"][:-4] + ".tem"), parse_tem(r["B"][:-4] + ".tem")
    rng = np.random.default_rng(int(r["seed"]))
    out, am, lm, _, info = af_morph(a, la, b, lb, r["field"], rng)
    img.parent.mkdir(parents=True, exist_ok=True)
    amap.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(img), out)
    np.save(amap, am)
    np.save(str(amap)[:-4] + "_lm.npy", lm)
    return r["id"], "made", info


def build(a):
    rows = [r for r in csv.DictReader(open(a.manifest)) if r["kind"] == "morph"]
    if a.wave:
        rows = [r for r in rows if int(r["wave"]) <= a.wave]
    rows = rows[: a.limit or None]
    t0 = time.time()
    from multiprocessing import Pool
    made, infos = 0, {}
    with Pool(a.workers) as p:
        for i, (rid, st, info) in enumerate(p.imap_unordered(_job, rows, chunksize=4)):
            made += st == "made"
            if info is not None:
                infos[rid] = info
            if (i + 1) % 500 == 0:
                print(f"{i + 1}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
    dt = time.time() - t0
    log = dict(manifest=a.manifest, rows=len(rows), made=made, seconds=round(dt, 1), workers=a.workers,
               images_per_minute=round(60 * made / dt, 1) if made else None,
               s68_sha256=_sha(S68), s78_sha256=_sha(S78),
               uncovered_px_max=max((v["uncovered_px"] for v in infos.values()), default=0))
    tag = f"wave{a.wave}" if a.wave else "all"
    if a.limit:
        tag += f"_limit{a.limit}"
    json.dump(dict(log=log, info=infos), open(OUT / f"build_log_{tag}.json", "w"))
    print(json.dumps(log), flush=True)


def _sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def verify(a):
    """a = 0.5 everywhere vs the unchanged engine (fresh, unwrapped hm.morph call, as 78_tool_morph runs it)."""
    import cv2
    rows = [r for r in csv.DictReader(open(a.manifest)) if r["kind"] == "morph"][: a.n]
    res = []
    for r in rows:
        A, B = cv2.imread(r["A"]), cv2.imread(r["B"])
        la, lb = parse_tem(r["A"][:-4] + ".tem"), parse_tem(r["B"][:-4] + ".tem")
        ref = hm.morph(A, la, B, lb)                                   # unchanged engine, unwrapped
        out, am, _, m05, _ = af_morph(A, la, B, lb, "u50", np.random.default_rng(0))
        z, *_ = af_morph(A, la, B, lb, "zero", np.random.default_rng(0))
        wA, *_ = warped_pair(A, la, B, lb)
        res.append(dict(id=r["id"], A=r["A"], B=r["B"],
                        maxabs_u50_vs_engine=int(np.abs(out.astype(int) - ref.astype(int)).max()),
                        n_diff_px=int((out != ref).any(2).sum()),
                        maxabs_wrapped_vs_unwrapped=int(np.abs(m05.astype(int) - ref.astype(int)).max()),
                        alpha_minmax=[float(am.min()), float(am.max())],
                        zero_equals_engine_wA=bool((z == np.clip(wA, 0, 255).astype(np.uint8)).all())))
        print(json.dumps(res[-1]), flush=True)
    s = dict(n=len(res), max_abs_diff=max(x["maxabs_u50_vs_engine"] for x in res), pairs=res,
             s68_sha256=_sha(S68), s78_sha256=_sha(S78))
    json.dump(s, open(a.out, "w"), indent=1)
    print("max abs diff over", len(res), "pairs:", s["max_abs_diff"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("verify", "build"))
    ap.add_argument("--manifest", default=str(OUT / "manifest.csv"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--wave", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--out", default="/home/narolski/smad-next/experiments/AF0/verify_u50.json")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    build(a) if a.cmd == "build" else verify(a)

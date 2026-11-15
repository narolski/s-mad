"""AR2: graded two-person mixing with the UNCHANGED face_morpher library (baselines/face_morpher, the code behind
96_facemorpher_tool.py). The body of facemorpher.morpher.morph's frame loop with background='average', for one frame
at the tool's own `percent` (weight on the host image): points = locator.weighted_average_points(H, B, percent);
both faces warper.warp_image'd to them; blender.weighted_average(faces, percent); blender.mask_from_points;
blender.weighted_average(images, percent) background; blender.overlay_image. Mixing m = 1 - percent.
Levels m in {0, 0.1, 0.2, 0.3, 0.4, 0.5} on a seeded subset of hosts (same pairs H_p, B_p as R4).
No new pixel operation: every call is a library function, unchanged; PNG at tool size.

  python3 -I graded_fm.py --pool pool.csv --n 300 --workers 12 [--limit 8]
"""
import argparse
import csv
import importlib.util
import json
import pathlib
import random
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

FM = K.MC / "baselines/face_morpher/facemorpher"
LEVELS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)
SEED = 20261112


def _load(name):
    spec = importlib.util.spec_from_file_location(name, FM / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _locator_wap():
    """locator.weighted_average_points, its source text taken unchanged from locator.py (importing locator.py would
    load a dlib 68-point model file at import time, which is absent and unused here)."""
    import ast
    import numpy as np
    src = (FM / "locator.py").read_text()
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "weighted_average_points")
    ns = {"np": np}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(FM / "locator.py"), "exec"), ns)
    return ns["weighted_average_points"]


def one(job):
    import cv2
    import numpy as np
    out, hp, bp, m = job
    if pathlib.Path(out).exists():
        return 1
    warper, blender, wap = _load("warper"), _load("blender"), _locator_wap()
    h, b = cv2.imread(hp), cv2.imread(bp)
    ph = np.rint(K.read_tem(hp[:-4] + ".tem")).astype(int)
    pb = np.rint(K.read_tem(bp[:-4] + ".tem")).astype(int)
    size = h.shape[:2]
    percent = 1.0 - m
    points = wap(ph, pb, percent)
    f1 = warper.warp_image(h, ph, points, size)
    f2 = warper.warp_image(b, pb, points, size)
    face = blender.weighted_average(f1, f2, percent)
    mask = blender.mask_from_points(face.shape[:2], points)
    face = np.dstack((face, mask))
    bg = blender.weighted_average(h, b, percent)
    img = blender.overlay_image(face, mask, bg.copy())
    cv2.imwrite(out, img[..., :3])
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--name", default="frgcferet")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.pool)))
    random.Random(SEED).shuffle(rows)
    rows = sorted(rows[: a.limit or a.n], key=lambda r: r["pid"])
    root = K.OUT / "img" / a.name / "fm_graded"
    jobs = []
    for m in LEVELS:
        d = root / f"m{int(round(m * 100)):03d}"
        d.mkdir(parents=True, exist_ok=True)
        jobs += [(str(d / f"{r['pid'].replace(':', '_')}.png"), r["H"], r["B"], m) for r in rows]
    t0 = time.time()
    with Pool(a.workers) as p:
        done = sum(p.map(one, jobs, chunksize=8))
    dt = time.time() - t0
    log = dict(n_hosts=len(rows), levels=LEVELS, images=done, seconds=round(dt, 1),
               images_per_minute=round(60 * done / dt, 1), hosts=[r["pid"] for r in rows],
               lib_sha256={n: K.sha(FM / f"{n}.py") for n in ("warper", "blender", "locator")})
    json.dump(log, open(root / ("graded_log.json" if not a.limit else "graded_log_smoke.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in log.items() if k != "hosts"}), flush=True)


if __name__ == "__main__":
    main()

"""D12b: FaceMorpher warp-only images R2w4fm(H; B) for the D12a pairs (registration: REQUESTS.md D12b, 21a25a2).

Calls src/AR1/variants.py `one(("facemorpher", out, H, B))` UNCHANGED (the call that made the AR1 FaceMorpher R2w4
rung: warp_fm = face_morpher warper.warp_image of H to the rounded mean points of H and B, overlay inside the mask of
those points over H itself). Inputs: D12a pairs.csv and the MS1 FFHQ frames with their .tem files. Also writes, from
existing files only, the per-pair share of pixels where exactly one of H or B is black border, and |eye-distance gap|.
  OMP_NUM_THREADS=1 nice -n 19 python -I d12b_fm_warp_only.py --workers 2 [--limit 8]
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import pathlib
import time
from multiprocessing import Pool

import cv2
import numpy as np

T7 = pathlib.Path("/mnt/t7/smad_next")
OUT = T7 / "DATA/D12b"
SRC = pathlib.Path("/home/narolski/smad-next/src/AR1")
VAR_SHA = "76f4cd170ddb5e7b"
FMLIB = pathlib.Path("/home/narolski/mambamorph-code/baselines/face_morpher/facemorpher")
LIB = {"warper.py": "76c0d1acfb66813cc383a2a9df2fc3e069bf641a5f8938940b3cc255c2055d6c",
       "blender.py": "7b98a8d5bf70f5700f30872fc096daae8b1e206490aabee366d81db44cc43bee"}
V = None


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def var():
    global V
    if V is None:
        import sys
        cv2.setNumThreads(1)
        sys.path.insert(0, str(SRC))
        spec = importlib.util.spec_from_file_location("ar1_variants", SRC / "variants.py")
        V = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(V)
    return V


def job(args):
    out, h, b = args
    return var().one(("facemorpher", out, h, b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    assert sha(SRC / "variants.py").startswith(VAR_SHA), "variants.py changed"
    for k, v in LIB.items():
        assert sha(FMLIB / k) == v, k
    pairs = list(csv.DictReader(open(T7 / "DATA/D12a/pairs.csv")))
    d12a = {(r["host"], r["partner"]): r for r in csv.DictReader(open(T7 / "DATA/D12a/manifest.csv"))}
    d1d = {r["key"]: r for r in csv.DictReader(open(T7 / "DATA/D1d/manifest.csv"))}
    if a.limit:
        pairs = pairs[: a.limit]
    sfx = "_test8" if a.limit else ""
    od = OUT / ("test8" if a.limit else "facemorpher") / "R2w4"
    od.mkdir(parents=True, exist_ok=True)
    jobs = []
    for p in pairs:
        h, b = d1d[p["host"]]["frame"], d1d[p["partner"]]["frame"]
        jobs.append((str(od / f"{p['host']}__{p['partner']}.png"), h, b))
    t0 = time.time()
    with Pool(a.workers) as pool:
        pool.map(job, jobs, chunksize=8)
    dt = time.time() - t0
    man, fails, meas = [], [], []
    checks = dict(same_shape=0, same_dtype=0, png=0)
    for p, (o, h, b) in zip(pairs, jobs):
        m = d12a[(f"ffhq:{p['host']}", f"ffhq:{p['partner']}")]
        H, B = cv2.imread(h), cv2.imread(b)
        bh, bb = H.max(2) == 0, B.max(2) == 0
        meas.append(dict(host=p["host"], partner=p["partner"], exactly_one_black_share=round(float((bh ^ bb).mean()), 6),
                         host_black_share=round(float(bh.mean()), 6), partner_black_share=round(float(bb.mean()), 6),
                         abs_ied_gap=abs(float(p["ied_host"]) - float(p["ied_partner"]))))
        if not pathlib.Path(o).exists():
            fails.append(dict(host=p["host"], partner=p["partner"]))
            continue
        W, F = cv2.imread(o, cv2.IMREAD_UNCHANGED), cv2.imread(m["out"], cv2.IMREAD_UNCHANGED)
        checks["same_shape"] += W.shape == F.shape
        checks["same_dtype"] += W.dtype == F.dtype
        checks["png"] += open(o, "rb").read(8) == open(m["out"], "rb").read(8) == b"\x89PNG\r\n\x1a\n"
        man.append(dict(host=f"ffhq:{p['host']}", partner=f"ffhq:{p['partner']}", rung="R2w4", engine="facemorpher",
                        frame_host=h, frame_host_sha256=d1d[p["host"]]["frame_sha256"], frame_partner=b,
                        frame_partner_sha256=d1d[p["partner"]]["frame_sha256"], out=o, out_sha256=sha(o),
                        d12a_morph=m["out"], d12a_morph_sha256=m["out_sha256"], d1d_render=d1d[p["host"]]["out"]))
    mp = OUT / f"manifest{sfx}.csv"
    for path, rows, cols in ((mp, man, None), (OUT / f"failures{sfx}.csv", fails, ["host", "partner"]),
                             (OUT / f"pair_measures{sfx}.csv", meas, None)):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols or list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    (OUT / f"SHA256SUMS{sfx}").write_text("".join(f"{x['out_sha256']}  {pathlib.Path(x['out']).relative_to(OUT)}\n" for x in man))
    e1 = sorted(x["exactly_one_black_share"] for x in meas)
    g = sorted(x["abs_ied_gap"] for x in meas)
    q = lambda v, f: v[min(len(v) - 1, int(f * len(v)))]
    log = dict(pairs=len(pairs), present=len(man), failures=len(fails), seconds=round(dt, 1), workers=a.workers,
               host=os.uname().nodename, variants_sha256=sha(SRC / "variants.py"), library=LIB, checks_vs_d12a=checks,
               border_treatment="outside the mask: warp-only keeps H; FM(H,B) averages H and B (by construction)",
               exactly_one_black_share=dict(median=q(e1, 0.5), p90=q(e1, 0.9), max=e1[-1], pairs_above_0p01=sum(v > 0.01 for v in e1)),
               abs_ied_gap=dict(median=q(g, 0.5), p90=q(g, 0.9), max=g[-1]),
               manifest_sha256=sha(mp), measures_sha256=sha(OUT / f"pair_measures{sfx}.csv"))
    json.dump(log, open(OUT / f"build_log{sfx}.json", "w"), indent=1)
    print(json.dumps(log))


if __name__ == "__main__":
    main()

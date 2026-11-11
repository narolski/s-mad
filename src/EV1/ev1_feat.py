"""Fixed-threshold re-read (EV1), Part B features: per-image colour statistics, zero-border fraction and 32 x 32 grey
thumbnail of the aligned frames, and header attributes + colour statistics of the stored files, for the 17 cells of
the cue checks (C1 to C4). Colour, border and headers come from c_checks.stats_job (imported unchanged); the thumbnail is
a 16 x 16 block mean of the decoded frame in memory (the block-mean operation the C1 expression probe uses). Nothing
is written except the feature file. Run: python3 -I src/EV1/ev1_feat.py [--smoke]
"""
import os, sys, time, pathlib
from multiprocessing import Pool
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "C_cue_checks"))
import c_checks as CC  # noqa: E402
import ev1_common as K  # noqa: E402

SMOKE = "--smoke" in sys.argv
T0 = time.time()


def job(args):
    p, kind = args
    o = CC.stats_job((p, kind))
    if "error" in o:
        return o
    try:
        from PIL import Image
        with Image.open(p) as im:
            w, h = im.size
            if kind == "al":
                a = np.asarray(im.convert("RGB"), dtype=np.float64).mean(2)
                H, W_ = a.shape
                assert H % 32 == 0 and W_ % 32 == 0, (H, W_)
                o["thumb"] = a.reshape(32, H // 32, 32, W_ // 32).mean((1, 3)).astype(np.float32).ravel()
        o["w"], o["h"], o["bytes"] = w, h, os.path.getsize(p)
    except Exception as e:  # noqa: BLE001
        o["error"] = repr(e)
    return o


def main():
    C = CC.cells()
    jobs = sorted({(str(p), "raw") for c in C.values() for p in c["m_raw"] + c["b_raw"]} |
                  {(str(p), "al") for c in C.values() for p in c["m_al"] + c["b_al"]})
    assert not any(K.forbidden(p) for p, _ in jobs)
    print(len(jobs), "images", len(C), "cells", flush=True)
    with Pool(8) as pool:
        R = pool.map(job, jobs, chunksize=8)
    err = [o for o in R if "error" in o]
    print("errors", len(err), [e["error"] for e in err[:3]], f"{time.time() - T0:.0f}s", flush=True)
    al = [(j, o) for j, o in zip(jobs, R) if j[1] == "al" and "error" not in o]
    rw = [(j, o) for j, o in zip(jobs, R) if j[1] == "raw" and "error" not in o]
    hd = lambda o, k: str(o["hdr"][k])  # noqa: E731
    out = K.BIG / ("feat_smoke.npz" if SMOKE else "feat.npz")
    np.savez_compressed(
        out,
        al_path=np.array([j[0] for j, _ in al]),
        al_mean=np.array([o["mean"] for _, o in al]), al_std=np.array([o["std"] for _, o in al]),
        al_zero=np.array([o["zero_frac"] for _, o in al]), al_thumb=np.stack([o["thumb"] for _, o in al]),
        al_wh=np.array([[o["w"], o["h"]] for _, o in al]),
        raw_path=np.array([j[0] for j, _ in rw]),
        raw_mean=np.array([o["mean"] for _, o in rw]), raw_std=np.array([o["std"] for _, o in rw]),
        raw_w=np.array([o["w"] for _, o in rw]), raw_h=np.array([o["h"] for _, o in rw]),
        raw_bytes=np.array([o["bytes"] for _, o in rw]),
        raw_container=np.array([hd(o, "container") for _, o in rw]), raw_sub=np.array([hd(o, "sub") for _, o in rw]),
        errors=np.array([str(e.get("path")) + " " + e["error"] for e in err]),
        cells=np.array(list(C.keys())))
    print("written", out, f"{time.time() - T0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

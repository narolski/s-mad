"""PN1 certificate cues (prereg section 9 (i)): pixel cues measured on the image as the network sees it.
Loading: the training loader's own step, common.ImageItems.load of the AD4 pack (sha256 b5d42a99...; PIL RGB, whole
frame, bilinear resize to 224), imported unchanged. The same cues on the unresized 512 frame are stored for the
DINOv3 heads (descriptive). Measurements only; no image is written.
Cues (12): lap_k1, lap_k3, lap_k5 = variance of cv2.Laplacian(luma, CV_32F, ksize k); band0..band7 = log10 mean power
of the Hann-windowed luma spectrum (mean removed) in 8 equal-width radial bands from 1/N to 0.5 cycles per pixel
(rfft half plane, interior columns counted twice, as smadcvpr/cue_floor); zero_frac = share of pixels with every
channel <= 2 (cue_floor's border definition).
  python3 -I cert_cues.py <name>=<list.csv> ...   (list needs columns id, path)   [PN1_LIMIT=8 for a test]
Output /mnt/t7/smad_next/PN1/cues/cert_<name>.npz: ids, c224 (N, 12), c512 (N, 12), names.
"""
import csv
import hashlib
import os
import pathlib
import sys
import time

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402

PACK_CODE = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4/code/smadcvpr")
COMMON_SHA = "b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8"
OUT = pathlib.Path("/mnt/t7/smad_next/PN1/cues")
NAMES = ["lap_k1", "lap_k3", "lap_k5"] + [f"band{i}" for i in range(8)] + ["zero_frac"]
_cache = {}


def spec(N):
    if N not in _cache:
        fy = np.fft.fftfreq(N)[:, None]
        fx = np.fft.rfftfreq(N)[None, :]
        FR = np.hypot(fy, fx)
        W = np.ones_like(FR)
        W[:, 1:(N + 1) // 2] = 2.0
        edges = np.linspace(1.0 / N, 0.5, 9)
        masks = [(FR >= lo) & (FR < hi) for lo, hi in zip(edges[:-1], edges[1:])]
        HANN = np.outer(np.hanning(N), np.hanning(N)).astype(np.float32)
        _cache[N] = (W, masks, HANN)
    return _cache[N]


def cues(rgb):
    import cv2
    rgb = np.ascontiguousarray(rgb)
    N = rgb.shape[0]
    assert rgb.shape == (N, N, 3)
    f = rgb.astype(np.float32)
    Y = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    out = [float(cv2.Laplacian(Y, cv2.CV_32F, ksize=k).var()) for k in (1, 3, 5)]
    W, masks, HANN = spec(N)
    P = (np.abs(np.fft.rfft2((Y - Y.mean()) * HANN)) ** 2).astype(np.float64) * W
    out += [float(np.log10(P[m].sum() / W[m].sum() + 1e-12)) for m in masks]
    out.append(float((f.max(-1) <= 2).mean()))
    return out


def main():
    import cv2
    cv2.setNumThreads(1)
    assert hashlib.sha256((PACK_CODE / "common.py").read_bytes()).hexdigest() == COMMON_SHA
    sys.path.insert(0, str(PACK_CODE))
    import common as C                        # the AD4 pack's loader code, unchanged
    from PIL import Image
    loader = C.ImageItems([], 224, root="/")
    OUT.mkdir(parents=True, exist_ok=True)
    lim = int(os.environ.get("PN1_LIMIT", "0"))
    for job in sys.argv[1:]:
        name, lst = job.split("=", 1)
        tag = name + (f"_limit{lim}" if lim else "")
        out = OUT / f"cert_{tag}.npz"
        if out.exists():
            print("exists", out, flush=True)
            continue
        R = list(csv.DictReader(open(lst)))[: lim or None]
        a, b, t0 = [], [], time.time()
        for k, r in enumerate(R):
            img, _ = loader.load(r["path"])
            a.append(cues(np.asarray(img)))
            b.append(cues(np.asarray(Image.open(r["path"]).convert("RGB"))))
            if (k + 1) % 500 == 0:
                print(name, k + 1, len(R), f"{(k + 1) / (time.time() - t0):.1f}/s", flush=True)
        np.savez(out, ids=np.array([r["id"] for r in R]), c224=np.array(a), c512=np.array(b), names=np.array(NAMES))
        print("DONE", name, len(R), f"{time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

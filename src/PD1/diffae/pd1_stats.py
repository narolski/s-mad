"""PD1 DiffAE family: the seven simple image statistics of FZ1 P4 (the "simple-statistic floor").

Per image, on the 224 loader input the features see (smadcvpr/common.ImageItems(res=224)): high-frequency energy share
(luma FFT power above half Nyquist), Laplacian variance (cv2.Laplacian ksize 1, luma), mean |image - mirror image| (RGB),
per-channel std (R, G, B); plus the PNG file size in bytes. stats() is copied verbatim from src/FZ1/fz1_stats.py.
No image is written.

  pd1_stats.py --sets tr,f256,... [--limit 8] [--tag smoke]
Writes /mnt/t7/smad_next/PD1/diffae/stats/<set>[_<tag>].npz (id, stats n x 7, names)
Run: OMP_NUM_THREADS=1 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_stats.py ...
"""
import argparse, csv, os, pathlib, sys, time
import numpy as np
import cv2
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
from common import ImageItems  # noqa: E402

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/diffae")
NAMES = ("hf_energy", "laplacian_var", "mirror_mad", "std_R", "std_G", "std_B", "png_bytes")


def stats(img, png):
    I = img.astype(np.float64)
    Y = 0.299 * I[..., 0] + 0.587 * I[..., 1] + 0.114 * I[..., 2]
    Yc = Y - Y.mean()
    P = np.abs(np.fft.fft2(Yc)) ** 2
    fy, fx = np.meshgrid(np.fft.fftfreq(Y.shape[0]), np.fft.fftfreq(Y.shape[1]), indexing="ij")
    hf = float(P[np.sqrt(fx ** 2 + fy ** 2) > 0.25].sum() / max(P.sum(), 1e-12))
    lap = float(cv2.Laplacian(Y, cv2.CV_64F, ksize=1).var())
    mir = float(np.abs(I - I[:, ::-1]).mean())
    sd = I.reshape(-1, 3).std(0)
    return [hf, lap, mir, float(sd[0]), float(sd[1]), float(sd[2]), float(png)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    items = list(csv.DictReader(open(BIG / "lists/items.csv")))
    (BIG / "stats").mkdir(parents=True, exist_ok=True)
    for s in a.sets.split(","):
        out = BIG / "stats" / (f"{s}_{a.tag}.npz" if a.tag else f"{s}.npz")
        if out.exists() and not a.tag:
            print("exists, skipped:", out)
            continue
        rows = [r for r in items if r["set"] == s]
        if a.limit:
            rows = rows[:a.limit]
        ds = ImageItems([(r["path"], 0) for r in rows], res=224, root="/")
        t0 = time.time()
        S = np.zeros((len(rows), len(NAMES)), np.float64)
        for k, r in enumerate(rows):
            x = ds[k][0].permute(1, 2, 0).numpy() * 255.0
            S[k] = stats(x, os.path.getsize(r["path"]))
            if k % 1000 == 0:
                print(f"  {s} {k}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
        np.savez(out, id=np.array([r["id"] for r in rows]), stats=S, names=np.array(NAMES))
        print(f"wrote {out} {len(rows)} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

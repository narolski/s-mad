"""Signal isolation by paired differences (PD1), GAN family: simple image statistics (the floor).

FZ1's seven statistics (src/FZ1/fz1_stats.py, function copied verbatim) on the same 224 loader view the features see
(smadcvpr/common.ImageItems(res=224)): high-frequency energy share, Laplacian variance, mean |image - mirror image|,
std of R, G, B, file bytes of the stored file. Sets G, Hr, Ha (the sets with head contrasts).
Writes /mnt/t7/smad_next/PD1/gan/stats.npz (id, names, S).
Run: OMP_NUM_THREADS=1 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/gan/pd1_stats.py [--smoke]
"""
import csv, os, pathlib, sys
from multiprocessing import Pool
import numpy as np
import cv2
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
from common import ImageItems  # noqa: E402

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
NAMES = ("hf_energy", "laplacian_var", "mirror_mad", "std_R", "std_G", "std_B", "file_bytes")


def stats(img, png):  # verbatim from src/FZ1/fz1_stats.py
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


def one(path):
    cv2.setNumThreads(1)
    ds = ImageItems([(path, 0)], res=224, root="/")
    x = ds[0][0].permute(1, 2, 0).numpy() * 255.0
    return stats(x, os.path.getsize(path))


def main():
    smoke = "--smoke" in sys.argv
    rows = [r for r in csv.DictReader(open(BIG / "items.csv")) if r["set"] in ("G", "Hr", "Ha")]
    if smoke:
        rows = rows[:8]
    with Pool(3) as p:
        S = p.map(one, [r["path"] for r in rows], chunksize=16)
    out = BIG / ("stats_smoke.npz" if smoke else "stats.npz")
    np.savez(out, id=np.array([r["id"] for r in rows]), names=np.array(NAMES), S=np.array(S, dtype=np.float64))
    print("wrote", out, np.array(S).shape)
    if smoke:
        print(np.array(S))


if __name__ == "__main__":
    main()

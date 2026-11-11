"""V3: own simple statistics of the set G images (x0..x3) at native size (renders 1024 px, photos 512 px), computed
on whole image, a fixed face ellipse and the surround (FFHQ-aligned frame). Writes v3_stats.npz (small).
Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I v3_stats.py"""
import os, sys
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(__file__))
import vlib as V

cv2.setNumThreads(2)


def ellipse_mask(n):
    yy, xx = np.mgrid[0:n, 0:n] / n
    return ((xx - 0.5) / 0.27) ** 2 + ((yy - 0.56) / 0.36) ** 2 <= 1.0


def region_stats(Y, I, m):
    L = cv2.Laplacian(Y, cv2.CV_64F, ksize=3)
    gx, gy = cv2.Sobel(Y, cv2.CV_64F, 1, 0), cv2.Sobel(Y, cv2.CV_64F, 0, 1)
    G = np.hypot(gx, gy)
    hsv = cv2.cvtColor(I.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(float)
    return [np.log(L[m].var() + 1e-9), np.log(np.median(np.abs(L[m])) + 1e-9), np.log(G[m].mean() + 1e-9),
            Y[m].mean(), Y[m].std(), hsv[..., 1][m].mean(), I[..., 0][m].std(), I[..., 1][m].std(), I[..., 2][m].std()]


def band_energy(Y):
    P = np.abs(np.fft.fftshift(np.fft.fft2(Y - Y.mean()))) ** 2
    n = Y.shape[0]
    fy, fx = np.mgrid[-n // 2:n // 2, -n // 2:n // 2] / n
    r = np.hypot(fx, fy)
    edges = [0, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 3 / 16, 1 / 4, 3 / 8, 0.71]
    tot = P.sum()
    return [np.log(P[(r >= a) & (r < b)].sum() / tot + 1e-12) for a, b in zip(edges[:-1], edges[1:])]


def one(path):
    I = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    I = cv2.resize(I, (512, 512), interpolation=cv2.INTER_AREA).astype(np.float64)  # common 512 view for both frames
    Y = 0.299 * I[..., 0] + 0.587 * I[..., 1] + 0.114 * I[..., 2]
    m = ellipse_mask(512)
    s = [np.log(os.path.getsize(path))]
    s += region_stats(Y, I, np.ones_like(m)) + region_stats(Y, I, m) + region_stats(Y, I, ~m)
    s += band_energy(Y)
    s += [float(np.abs(I - I[:, ::-1]).mean())]
    return s


NAMES = ["log_file_bytes"] + [f"{reg}_{n}" for reg in ("all", "face", "sur") for n in
         ("loglapvar", "logmedlap", "loggrad", "meanY", "stdY", "sat", "stdR", "stdG", "stdB")] + \
        [f"band{i}" for i in range(8)] + ["mirror_mad"]

if __name__ == "__main__":
    rows = [r for r in V.rows("items.csv") if r["set"] == "G"]
    S = np.array([one(r["path"]) for r in rows])
    np.savez(V.OUT / "v3_stats.npz", id=np.array([r["id"] for r in rows]), names=np.array(NAMES), S=S)
    print(S.shape)

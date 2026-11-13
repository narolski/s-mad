"""Standing adversary (ADV): shortcut-only image features, computed on the stored 512 x 512 frame exactly as the
networks' packs hold it (cv2.imread, BGR -> RGB; no resampling, no image is written).

Families (the registration experiments/ADV_shortcut-floors/prereg.md section 3 fixes this list):
  F27     the 27 hand-made statistics of the reviewed floor: 26 smadcvpr/cue_floor statistics + PNG bytes, through
          src/AF0/cues_all.one imported unchanged (sha256 asserted, the same pin as src/PN1/cues27.py).
  BORDER  black-frame measures: edge-connected exactly-black fraction (src/TT1/build_border_ref.edge_mask, imported
          unchanged), black depth of each side, content bounding-box fraction, step contrast at the content boundary.
  RES     native-resolution / enlargement proxies: radial-spectrum cut-off frequencies (95 / 99 / 99.9% of the power)
          of the face box and of the whole frame, implied enlargement 0.5 / f99 of the face box, content scale.
  STORE   file size and storage history: PNG bytes per content pixel,
          8x8 blockiness maximised over the 64 grid offsets (JPEG grid that survived), DCT quantisation-comb score.
  RENDER  high-frequency and rendering cues: spectral peak excess at the GAN up-sampling frequencies, high-band tail
          flatness, chroma-noise residual std, cross-channel noise-residual correlation (demosaicing trace), residual
          kurtosis in the face.
  BLEND   blend / ghosting energy (image only): secondary peak of the face Laplacian autocorrelation (lags 2-16 px),
          eye-region Laplacian and gradient energy, face / border gradient-spread ratio, left-right mirror difference of the
          face box, second- to first-derivative energy ratio in the face.
Only image statistics; no network, no identity model. CPU only.
"""
import hashlib
import importlib.util
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import cv2  # noqa: E402
import numpy as np  # noqa: E402

cv2.setNumThreads(1)
SRC = pathlib.Path("/home/narolski/smad-next/src")
CUES_ALL = SRC / "AF0" / "cues_all.py"
CUES_ALL_SHA = "1ab50f3098e9eac6fcdfeb7a08cb6b02613d728f87aa24a4a396509f41cdcc9f"   # as src/PN1/cues27.py
BORDER_REF = SRC / "TT1" / "build_border_ref.py"
N = 512
FY0, FY1, FX0, FX1 = 150, 430, 124, 388            # cue_floor's canonical face box
EYES = ((190, 210), (322, 210))                     # (x, y) of the aligned frame (prep_eval.py docstring)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(pathlib.Path(path).parent))
    spec.loader.exec_module(m)
    return m


_M = {}


def mods():
    if not _M:
        assert hashlib.sha256(CUES_ALL.read_bytes()).hexdigest() == CUES_ALL_SHA, "cues_all.py changed"
        _M["cues"] = _load(CUES_ALL, "af0_cues_all")
        _M["bref"] = _load(BORDER_REF, "tt1_build_border_ref")
        import cue_floor as CF
        _M["CF"] = CF
    return _M


def names():
    m = mods()
    f27 = ["F27:" + n for n in list(m["CF"].NAMES) + ["png_bytes"]]
    border = ["BORDER:" + n for n in ("edge_black_frac", "black_top", "black_bottom", "black_left", "black_right",
                                      "content_bbox_frac", "boundary_step")]
    res = ["RES:" + n for n in ("face_f95", "face_f99", "face_f999", "frame_f95", "frame_f99", "frame_f999",
                                "face_enlarge", "content_scale")]
    store = ["STORE:" + n for n in ("png_bytes_per_px", "block8_max_offset", "block8_offset_ratio",
                                    "dct_comb_score", "dct_comb_q")]
    render = ["RENDER:" + n for n in ("peak_q4", "peak_q2", "tail_flat", "chroma_noise_cb", "chroma_noise_cr",
                                      "resid_corr_rg", "resid_corr_gb", "resid_kurt_face")]
    blend = ["BLEND:" + n for n in ("ghost_peak", "ghost_lag", "eye_lap_energy", "eye_grad_energy",
                                    "face_over_border_grad", "mirror_mad_face", "d2_over_d1_face")]
    return f27 + border + res + store + render + blend


FAMILIES = ("F27", "BORDER", "RES", "STORE", "RENDER", "BLEND")


def _radial_cutoffs(Y, fracs=(0.95, 0.99, 0.999)):
    h, w = Y.shape
    Z = (Y - Y.mean()) * np.outer(np.hanning(h), np.hanning(w))
    P = np.abs(np.fft.fft2(Z)) ** 2
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    R = np.hypot(fy, fx)
    m = R > 1.0 / min(h, w)
    r, p = R[m], P[m]
    o = np.argsort(r)
    c = np.cumsum(p[o]) / p.sum()
    return [float(r[o][min(np.searchsorted(c, f), len(c) - 1)]) for f in fracs]


def _srm(Y):
    k = np.array([[-1, 2, -1], [2, -4, 2], [-1, 2, -1]], np.float32) / 4.0
    return cv2.filter2D(Y, cv2.CV_32F, k, borderType=cv2.BORDER_REFLECT)


def extra(rgb, path):
    """All non-F27 families for one 512 RGB uint8 frame (order = names()[27:])."""
    m = mods()
    f = rgb.astype(np.float32)
    Y = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    out = []
    # BORDER
    em = m["bref"].edge_mask(rgb)
    dark = rgb.max(2) <= 2
    rows_dark = dark.mean(1) >= 0.98
    cols_dark = dark.mean(0) >= 0.98

    def run(v):
        k = 0
        while k < len(v) and v[k]:
            k += 1
        return k
    top, bot, lef, rig = run(rows_dark), run(rows_dark[::-1]), run(cols_dark), run(cols_dark[::-1])
    nz = np.argwhere(~dark)
    if len(nz):
        (y0, x0), (y1, x1) = nz.min(0), nz.max(0)
        bbox = (y1 - y0 + 1) * (x1 - x0 + 1) / (N * N)
    else:
        bbox = 0.0
    if em.any():
        dil = cv2.dilate(em.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~em
        step = float(Y[dil].mean()) if dil.any() else 0.0
    else:
        step = 0.0
    out += [float(em.mean()), top / N, bot / N, lef / N, rig / N, float(bbox), step]
    # RES
    face = Y[FY0:FY1, FX0:FX1]
    fc = _radial_cutoffs(face)
    fr = _radial_cutoffs(Y)
    out += fc + fr + [0.5 / max(fc[1], 1e-6), float(np.sqrt(max(bbox, 1e-6)))]
    # STORE
    content = max(int((~dark).sum()), 1)
    nbytes = os.path.getsize(path)
    dh = np.abs(np.diff(Y, axis=1))
    dv = np.abs(np.diff(Y, axis=0))
    ch, rv = dh.mean(0), dv.mean(1)                 # equal counts per column / row: mean of means is exact
    k8 = np.arange(N - 1) % 8
    hh = np.array([ch[k8 == o].mean() / (ch[k8 != o].mean() + 1e-6) for o in range(8)])
    vv = np.array([rv[k8 == o].mean() / (rv[k8 != o].mean() + 1e-6) for o in range(8)])
    bl = (vv[:, None] + hh[None, :]) / 2            # bl[oy, ox], the cue_floor blockiness8 at grid offset (oy, ox)
    blmax = float(bl.max())
    blratio = float(bl.max() / (np.median(bl) + 1e-6))
    by, bx = np.unravel_index(int(bl.argmax()), bl.shape)
    T = Y[by + 0: by + 8 * ((N - by) // 8), bx: bx + 8 * ((N - bx) // 8)] - 128.0
    hb, wb = T.shape[0] // 8, T.shape[1] // 8
    blocks = T[: hb * 8, : wb * 8].reshape(hb, 8, wb, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)
    keep = blocks.std((1, 2)) > 1.0
    best_s, best_q = 0.0, 0.0
    if keep.sum() > 50:
        D = np.stack([cv2.dct(b.astype(np.float32)) for b in blocks[keep][:2000]])
        c = np.concatenate([D[:, 0, 1], D[:, 1, 0], D[:, 1, 1]])
        c = c[np.abs(c) > 0.5]
        if len(c) > 100:
            for q in range(2, 21):
                s = float(np.mean(np.cos(2 * np.pi * c / q)))
                if s > best_s:
                    best_s, best_q = s, float(q)
    out += [nbytes / content, blmax, blratio, best_s, best_q]
    # RENDER
    Z = (Y - Y.mean()) * np.outer(np.hanning(N), np.hanning(N))
    P = np.log10(np.abs(np.fft.fft2(Z)) ** 2 + 1e-6)
    fy = np.fft.fftfreq(N)[:, None]
    fx = np.fft.fftfreq(N)[None, :]

    def peak(fq):
        pts = [(fq, 0), (0, fq), (fq, fq), (-fq, fq)]
        v = []
        for a, b in pts:
            iy, ix = int(round(a * N)) % N, int(round(b * N)) % N
            loc = P[iy, ix]
            ring = P[[(iy + d) % N for d in (-3, 3, 0, 0)], [(ix + d) % N for d in (0, 0, -3, 3)]].mean()
            v.append(loc - ring)
        return float(max(v))
    R = np.hypot(fy, fx)
    tail = P[(R > 0.35) & (R < 0.5)]
    sr = [_srm(f[..., k]) for k in range(3)]
    Cb = -0.168736 * f[..., 0] - 0.331264 * f[..., 1] + 0.5 * f[..., 2]
    Cr = 0.5 * f[..., 0] - 0.418688 * f[..., 1] - 0.081312 * f[..., 2]
    fb = (slice(FY0, FY1), slice(FX0, FX1))
    rf = [s[fb].ravel() for s in sr]
    ry = _srm(Y)[fb].ravel()

    def corr(a, b):
        sa, sb = a.std(), b.std()
        return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb)) if sa > 1e-6 and sb > 1e-6 else 0.0
    kurt = float(((ry - ry.mean()) ** 4).mean() / (ry.var() ** 2 + 1e-9))
    out += [peak(0.25), peak(0.5 - 1.0 / N), float(tail.std()), float(_srm(Cb)[fb].std()), float(_srm(Cr)[fb].std()),
            corr(rf[0], rf[1]), corr(rf[1], rf[2]), kurt]
    # BLEND
    L = cv2.Laplacian(Y, cv2.CV_32F, ksize=3)
    Lf = L[fb] - L[fb].mean()
    A = np.real(np.fft.ifft2(np.abs(np.fft.fft2(Lf, s=(2 * Lf.shape[0], 2 * Lf.shape[1]))) ** 2))
    A = A / (A[0, 0] + 1e-9)
    lag = np.hypot(*np.meshgrid(np.r_[0:A.shape[0] // 2, -(A.shape[0] // 2):0], np.r_[0:A.shape[1] // 2, -(A.shape[1] // 2):0],
                                indexing="ij"))
    ring = (lag >= 2) & (lag <= 16)
    gi = int(np.argmax(np.where(ring, A, -np.inf)))
    eye = np.zeros((N, N), bool)
    for x, y in EYES:
        eye[y - 24:y + 24, x - 32:x + 32] = True
    gx = cv2.Sobel(Y, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(Y, cv2.CV_32F, 0, 1)
    G = np.hypot(gx, gy)
    ring_b = np.zeros((N, N), bool)
    ring_b[:64, :] = ring_b[:, :64] = ring_b[:, N - 64:] = True
    fm = Y[fb]
    out += [float(A.ravel()[gi]), float(lag.ravel()[gi]), float((L[eye] ** 2).mean()), float((G[eye] ** 2).mean()),
            float(G[fb].std() / (G[ring_b].std() + 1e-6)), float(np.abs(fm - fm[:, ::-1]).mean()),
            float((L[fb] ** 2).mean() / ((G[fb] ** 2).mean() + 1e-6))]
    return out


def one(path):
    """Full feature vector of one stored frame (len(names()))."""
    m = mods()
    f27 = m["cues"].one(path)                       # 26 cue_floor stats + PNG bytes, the reviewed function
    rgb = cv2.imread(path)[:, :, ::-1]
    assert rgb.shape == (N, N, 3), (path, rgb.shape)
    return np.r_[f27, np.array(extra(np.ascontiguousarray(rgb), path), np.float64)]


def compute(paths, workers=2):
    from multiprocessing import Pool
    with Pool(workers) as p:
        return np.stack(p.map(one, list(paths), chunksize=8))

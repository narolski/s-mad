"""Mirror-asymmetry test (AS0), step 3: per-image band energies of the mirror-asymmetric and mirror-symmetric parts,
shape asymmetry and covariates (prereg.md, section "Statistic"). Measurement only: images are read, nothing is written
except the result arrays.

  python3 -I as0_measure.py --iod                      -> OUT/iod_nominal.json (nominal IOD per frame type)
  python3 -I as0_measure.py --sets L,Fm [--limit 8] [--chunk 256] [--shard i/n]
      -> OUT/meas/<set>_<k>.npz (resumable): ids; EA, ES [n, 4 channels (Y, R, G, B), 2 flips (F0, F1), 7 bands
         (B0..B6)]; covariates (see COV); shape asymmetry; pixel hash.
  python3 -I as0_measure.py --merge                    -> OUT/meas_all.npz
"""
import argparse
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402

NB = 7                       # B0 (low residual), B1..B5 (octave bands), B6 (high residual)
CH = ("Y", "R", "G", "B")
COV = ("mask0", "mask1", "c_mid", "mid_off", "iod_img", "yaw", "nose_off", "roll", "light", "lap_mask", "lap_full",
       "l1_mask", "box_l1", "shape_L", "W", "H", "lm_ok")
SMDD_LM = pathlib.Path("/mnt/t7/smad_next/AS0/inputs/smdd_bona_landmarks_if106.npz")   # byte copy of the /dev/shm file
_W = {}


def band_weights(h, w, iod):
    key = (h, w, round(iod, 3))
    if key in _W:
        return _W[key]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    with np.errstate(divide="ignore"):
        u = np.log2(f * iod)
    Hs = np.zeros((NB,) + f.shape, np.float32)
    u = np.where(np.isfinite(u), u, -50.0)          # f = 0 (the mean) -> deep in B0
    for k in range(1, 6):
        d = u - (k - 0.5)
        Hs[k] = np.where(np.abs(d) <= 1, np.cos(np.pi / 2 * d), 0)
    Hs[0] = np.where(u <= -0.5, 1.0, np.where(u < 0.5, np.cos(np.pi / 2 * (u + 0.5)), 0))
    Hs[6] = np.where(u >= 5.5, 1.0, np.where(u > 4.5, np.cos(np.pi / 2 * (u - 5.5)), 0))
    s2 = (Hs.astype(np.float64) ** 2).sum(0)
    assert np.allclose(s2, 1, atol=1e-5), (s2.min(), s2.max())
    _W[key] = Hs
    return Hs


class LM:
    """landmark resolver for the item list."""

    def __init__(self, items):
        self.items = items
        self.det = {}
        p = K.OUT / "lm/landmarks.npz"
        if p.exists():
            with np.load(p, allow_pickle=False) as z:
                for i, l, n in zip(z["ids"].tolist(), z["lm"], z["n_faces"]):
                    if n > 0:
                        self.det[i] = l.astype(np.float64)
        self.smdd = None

    def get(self, spec):
        kind, _, arg = spec.partition(":")
        if kind == "tem":
            return K.read_tem(arg)
        if kind == "mix":
            a, b, w = arg.split(";")
            w = float(w)
            return (1 - w) * K.read_tem(a) + w * K.read_tem(b)
        if kind == "same_as":
            return self.get(self.items[arg]["lm"])
        if kind == "det":
            return None  # resolved by id
        if kind == "det_of":
            return self.det.get(arg)
        if kind == "smdd":
            if self.smdd is None:
                with np.load(K.guard(SMDD_LM), allow_pickle=False) as z:
                    self.smdd = dict(zip(z["names"].tolist(), z["lms"].astype(np.float64)))
            name, sc = arg.split(";")
            l = self.smdd.get(name + ".png", self.smdd.get(name))
            return None if l is None else l * 256.0 * float(sc)    # the file stores coordinates / 256 (image size)
        raise ValueError(spec)

    def of(self, it):
        if it["lm"] == "det":
            return self.det.get(it["id"])
        return self.get(it["lm"])


def shape_asym(X, W):
    Xm = K.mirror_shape(X, W)
    mx = X.mean(0)
    Xc, Yc = X - mx, Xm - Xm.mean(0)
    U, s, Vt = np.linalg.svd(Yc.T @ Xc)
    D = np.diag([1.0, np.sign(np.linalg.det(U @ Vt))])
    R = U @ D @ Vt
    sc = float((s * np.diag(D)).sum() / (Yc ** 2).sum())
    Ys = sc * Yc @ R
    A = (Xc - Ys) / 2
    S = (Xc + Ys) / 2
    return float(np.log((A ** 2).sum() / (S ** 2).sum()))


def masks(lm, img, iod, c2):
    """symmetric face masks for F0 (axis (W-1)/2) and F1 (axis c2/2, c2 integer)."""
    import cv2
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.uint8)
    cv2.fillPoly(m, [np.round(K.face_polygon(lm) * 4).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=2)
    e = int(round(0.04 * iod))
    if e > 0:
        m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1)))
    z = (img.max(2) == 0).astype(np.uint8)
    n, lab = cv2.connectedComponents(z, connectivity=4)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    border = np.isin(lab, edge[edge > 0]) & (z > 0)
    if border.any():
        border = cv2.dilate(border.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    ok = (m > 0) & ~border
    M0 = ok & ok[:, ::-1]
    j = np.arange(w)
    idx = c2 - j
    valid = (idx >= 0) & (idx < w)
    idxc = np.where(valid, idx, j)
    M1 = ok & ok[:, idxc] & valid[None, :]
    return M0, M1, idxc


def bbox(M):
    r = np.where(M.any(1))[0]
    c = np.where(M.any(0))[0]
    return (r[0], r[-1] + 1, c[0], c[-1] + 1) if len(r) else None


def measure(img_bgr, lm, iod_nom, frame, blank=False):
    """returns EA, ES [4, 2, 7] and covariate dict. blank (amendment A4): everything outside M_sym (F0) is set to the
    mean colour of M_sym in memory before the FFT; only F0 is then reported."""
    import cv2
    import scipy.fft as sf
    h, w = img_bgr.shape[:2]
    rgb = img_bgr[..., ::-1].astype(np.float32)
    cov = dict(W=w, H=h, lm_ok=1)
    c = float(lm[:, 0].mean())
    c2 = int(round(2 * c))
    cov["c_mid"], cov["mid_off"] = c2 / 2, (c2 / 2 - (w - 1) / 2) / iod_nom
    M0, M1, idx1 = masks(lm, img_bgr, iod_nom, c2)
    if blank:
        M1 = np.zeros_like(M0)
        if M0.sum() > 0:
            rgb = rgb.copy()
            rgb[~M0] = rgb[M0].mean(0)
    cov["mask0"], cov["mask1"] = int(M0.sum()), int(M1.sum())
    iod_img = float(np.linalg.norm(lm[K.PUPIL_R] - lm[K.PUPIL_L]))
    cov["iod_img"] = iod_img
    xl, xr, xn = lm[12, 0], lm[28, 0], lm[K.NOSE_TIP, 0]
    cov["yaw"] = float(((xn - xl) - (xr - xn)) / max(xr - xl, 1e-6))
    cov["nose_off"] = float((xn - (lm[K.PUPIL_L, 0] + lm[K.PUPIL_R, 0]) / 2) / max(iod_img, 1e-6))
    d = lm[K.PUPIL_R] - lm[K.PUPIL_L]
    cov["roll"] = float(np.degrees(np.arctan2(d[1], d[0])))
    Y = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    if M0.sum() > 0:
        left = np.zeros_like(M0)
        left[:, : w // 2] = True
        mY = Y[M0].mean()
        cov["light"] = float((Y[M0 & left].mean() - Y[M0 & ~left].mean()) / max(mY, 1e-6))
        cov["l1_mask"] = float(np.abs(Y - Y[:, ::-1])[M0].mean())
    else:
        cov["light"] = cov["l1_mask"] = np.nan
    grey = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(grey, cv2.CV_64F)
    cov["lap_full"] = float(np.log(lap.var()))
    cov["lap_mask"] = float(np.log(lap[M0].var())) if M0.sum() > 10 else np.nan
    if frame == "diffae256" and (h, w) == (256, 256):
        x = img_bgr.astype(np.float64)
        cov["box_l1"] = float(np.abs(x - x[:, ::-1])[70:220, 64:192].mean())
    else:
        cov["box_l1"] = np.nan
    cov["shape_L"] = shape_asym(lm, w)
    EA = np.full((4, 2, NB), np.nan)
    ES = np.full((4, 2, NB), np.nan)
    Hs = band_weights(h, w, iod_nom)
    F = [sf.rfft2(rgb[..., i], workers=1) for i in range(3)]
    bb = [bbox(M0), bbox(M1)]
    for k in range(NB):
        bands = [sf.irfft2(F[i] * Hs[k], s=(h, w), workers=1) for i in range(3)]
        bY = 0.299 * bands[0] + 0.587 * bands[1] + 0.114 * bands[2]
        for ci, b in enumerate([bY] + bands):
            for fi, (M, box) in enumerate(((M0, bb[0]), (M1, bb[1]))):
                if box is None:
                    continue
                r0, r1, j0, j1 = box
                if fi == 0:
                    bc, mc = b[r0:r1, j0:j1], M[r0:r1, j0:j1]
                    mir = b[r0:r1, ::-1][:, j0:j1]          # mirror(b)[:, j] = b[:, w-1-j]
                else:
                    bc, mc = b[r0:r1, j0:j1], M[r0:r1, j0:j1]
                    mir = b[r0:r1][:, idx1[j0:j1]]
                P = float((bc * bc)[mc].sum())
                Q = float((bc * mir)[mc].sum())
                EA[ci, fi, k] = (P - Q) / 2
                ES[ci, fi, k] = (P + Q) / 2
    return EA, ES, cov


def nominal_iod(items, L):
    frames = {}
    genuine = {"R0", "S0", "x0", "photo", "native"}
    for it in items.values():
        if it["set"] in ("L", "G", "D", "Ds", "Fm", "Fe", "S") and it["role"] in genuine:   # not the O/N copies; X not measured in phase 1
            lm = L.of(it)
            if lm is not None:
                frames.setdefault(it["frame"], []).append(float(np.linalg.norm(lm[K.PUPIL_R] - lm[K.PUPIL_L])))
    out = {f: dict(median=float(np.median(v)), n=len(v), q10=float(np.percentile(v, 10)),
                   q90=float(np.percentile(v, 90))) for f, v in frames.items()}
    # frames without genuine images of their own
    out["ar1_512"]["note"] = "also used for canon512 (same eye coordinates)"
    if "smdd256" in out:
        out["smdd80"] = dict(median=out["smdd256"]["median"] * 0.3125, note="0.3125 x smdd256")
    for f in ("stylegan_raw1024",):
        if f not in out:
            v = [float(np.linalg.norm(L.of(it)[K.PUPIL_R] - L.of(it)[K.PUPIL_L])) for it in items.values()
                 if it["frame"] == f and L.of(it) is not None]
            if v:
                out[f] = dict(median=float(np.median(v)), n=len(v), note="all images (no genuine image in this frame)")
    json.dump(out, open(K.OUT / "iod_nominal.json", "w"), indent=1)
    json.dump(out, open(K.RES / "iod_nominal.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def iod_for(frame, nom):
    return nom[frame]["median"]          # amendment A8: canon512 uses its own genuine images


def run(items, L, sets, limit, chunk, shard, blank=False, roles=None, db="", subsample=0):
    import cv2
    nom = json.load(open(K.OUT / "iod_nominal.json"))
    md = "meas_blank" if blank else "meas"
    (K.OUT / md).mkdir(exist_ok=True)
    si, sn = map(int, shard.split("/"))
    for s in sets:
        rows = [it for it in items.values() if it["set"] == s and (not roles or it["role"] in roles)
                and (not db or it["db"] == db)
                and (not subsample or int(hashlib.sha1(it["host"].encode()).hexdigest(), 16) % subsample == 0)]
        tag = (f"_{db}" if db else "") + ("_" + "-".join(sorted(roles)) if roles else "") + \
              (f"_sub{subsample}" if subsample else "")
        if limit:
            rows = rows[:limit]
        chunks = list(range(0, len(rows), chunk))
        for ci, k in enumerate(chunks):
            if ci % sn != si:
                continue
            part = K.OUT / md / (f"smoke_{s}_{k:05d}.npz" if limit else f"{s}{tag}_{k:05d}.npz")
            if part.exists():
                continue
            ch = rows[k: k + chunk]
            t0 = time.time()
            n = len(ch)
            EA = np.full((n, 4, 2, NB), np.nan, np.float64)
            ES = np.full((n, 4, 2, NB), np.nan, np.float64)
            C = np.full((n, len(COV)), np.nan, np.float64)
            hs = []
            for i, it in enumerate(ch):
                img = cv2.imread(str(K.guard(it["path"])), cv2.IMREAD_COLOR)
                hs.append(hashlib.sha1(img.tobytes()).hexdigest() if img is not None else "")
                lm = L.of(it)
                if img is None or lm is None or not np.isfinite(lm).all():
                    C[i, COV.index("lm_ok")] = 0
                    continue
                ea, es, cov = measure(img, lm, iod_for(it["frame"], nom), it["frame"], blank=blank)
                EA[i], ES[i] = ea, es
                for j, name in enumerate(COV):
                    C[i, j] = cov.get(name, np.nan)
            np.savez(part, ids=np.array([it["id"] for it in ch]), EA=EA, ES=ES, C=C, cov_names=np.array(COV),
                     pixhash=np.array(hs))
            print(f"{s} {k + n}/{len(rows)} {time.time() - t0:.1f}s", flush=True)


def merge(blank=False):
    md = "meas_blank" if blank else "meas"
    acc = {k: [] for k in ("ids", "EA", "ES", "C", "pixhash")}
    for p in sorted((K.OUT / md).glob("*.npz")):
        if p.name.startswith("smoke_"):
            continue
        with np.load(p, allow_pickle=False) as z:
            for k in acc:
                acc[k].append(z[k])
    out = {k: np.concatenate(v) for k, v in acc.items()}
    _, first = np.unique(out["ids"], return_index=True)      # role-filtered reruns can repeat an id: keep the first
    keep = np.sort(first)
    print("duplicate ids dropped", len(out["ids"]) - len(keep))
    out = {k: v[keep] for k, v in out.items()}
    np.savez(K.OUT / ("meas_blank_all.npz" if blank else "meas_all.npz"), cov_names=np.array(COV), **out)
    print("merged", len(out["ids"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iod", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--sets", default="L,Fm,G,D,M,Lsoft,Ds,Fe,R8,S,X")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--blank", action="store_true", help="amendment A4 sensitivity run -> OUT/meas_blank")
    ap.add_argument("--roles", default="", help="comma list of roles to measure (default all)")
    ap.add_argument("--db", default="", help="only items of this database (e.g. feret)")
    ap.add_argument("--subsample", type=int, default=0, help="only hosts with sha1(host) %% k == 0")
    a = ap.parse_args()
    if a.merge:
        return merge(a.blank)
    items = {it["id"]: it for it in K.read_csv(K.OUT / "items.csv")}
    L = LM(items)
    if a.iod:
        return nominal_iod(items, L)
    run(items, L, a.sets.split(","), a.limit, a.chunk, a.shard, a.blank, set(a.roles.split(",")) - {""}, a.db, a.subsample)


if __name__ == "__main__":
    main()

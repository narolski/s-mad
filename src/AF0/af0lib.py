"""AF0 shared helpers: token caches, face-hull patch masks, patch targets, statistics (AR1's / the record's helpers)."""
import csv
import importlib.util
import pathlib
import sys

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
RES = pathlib.Path("/home/narolski/smad-next/experiments/AF0")
GRID = {"dinov3_512": 32, "clip336": 24, "clip224": 16, "thumb": 32}
FACE_MIN = 0.5            # a patch is "inside the face hull" if >= half of its footprint lies inside the hull


def rows(name):
    return list(csv.DictReader(open(OUT / "lists" / f"{name}.csv")))


def read_tem(p):
    lines = open(p).read().splitlines()
    n = int(lines[0].strip())
    return np.array([list(map(float, lines[i].split()[:2])) for i in range(1, n + 1)], np.float32)


def geometry(r):
    if r["geom"] == "lm":
        return np.load(r["g1"]).astype(np.float32)
    if r["geom"] == "tem":
        w = float(r["w1"])
        a = read_tem(r["g1"])
        return a if w == 1.0 else w * a + (1 - w) * read_tem(r["g2"])
    return None


def area_matrix(g, n=512):
    s = n / g
    W = np.zeros((g, n))
    for i in range(g):
        lo, hi = i * s, (i + 1) * s
        for x in range(int(np.floor(lo)), min(n, int(np.ceil(hi)))):
            W[i, x] = max(0.0, min(hi, x + 1) - max(lo, x)) / s
    return W


def hull_mask(pts, n=512):
    import cv2
    m = np.zeros((n, n), np.uint8)
    h = cv2.convexHull(np.round(pts).astype(np.int32))
    cv2.fillConvexPoly(m, h, 1)
    return m.astype(np.float64)


def patch_mean(M, W):
    return W @ M.astype(np.float64) @ W.T


def canonical_hull():
    p = OUT / "canonical_lm.npy"
    if p.exists():
        return np.load(p)
    pts = [geometry(r) for r in rows("af0_w1") if r["cell"] == "train"]   # fixed once: wave-1 training images
    m = np.mean(np.stack(pts), 0)
    np.save(p, m)
    return m


def load_tokens(backbone, name):
    d = OUT / "feat" / backbone
    tok = np.load(d / f"{name}.tokens.npy", mmap_mode="r")
    ids = np.load(d / f"{name}.ids.npy")
    done = int((d / f"{name}.done").read_text())
    return tok, ids, done


def load_mirror(backbone, name):
    d = OUT / "feat" / backbone
    return np.load(d / f"{name}.mirror.npy", mmap_mode="r")


def prep(listname, g):
    """per-image face fraction per patch (N, T) and, for AF0 images, the per-patch mean of a(x) (N, T); cached."""
    p = OUT / "prep" / f"g{g}_{listname}.npz"
    if p.exists():
        z = np.load(p, allow_pickle=False)
        return dict(ids=z["ids"], face=z["face"], target=z["target"])
    R = rows(listname)
    W = area_matrix(g)
    can = patch_mean(hull_mask(canonical_hull()), W).reshape(-1)
    face = np.zeros((len(R), g * g), np.float32)
    tgt = np.full((len(R), g * g), np.nan, np.float32)
    for i, r in enumerate(R):
        pts = geometry(r)
        face[i] = can if pts is None else patch_mean(hull_mask(pts), W).reshape(-1)
        if r["set"] == "af0":
            base, sid = r["rung"].split("_soft_")[0], (r["id"].rsplit("_", 1)[0] if "_soft_" in r["rung"] else r["id"])
            if base in ("photo", "halfA", "halfB", "zero"):
                tgt[i] = 0.0          # softened negatives (wave 4) keep the all-zero map
            else:                     # softened positives keep the map of their source morph
                mp = OUT / "maps" / r["cell"] / base / (sid + ".npy")
                tgt[i] = patch_mean(np.load(mp).astype(np.float64), W).reshape(-1)
    p.parent.mkdir(parents=True, exist_ok=True)
    ids = np.array([r["id"] for r in R])
    np.savez(p, ids=ids, face=face, target=tgt)
    return dict(ids=ids, face=face, target=tgt)


def prep_inner(listname, g):
    """per-patch fraction inside the inner-face hull (insightface 106 points 33-105: eyebrows, eyes, nose, mouth);
    contour points are 0-32 (checked on a plotted frame). Periphery = outside the full landmark hull (face < FACE_MIN)."""
    p = OUT / "prep" / f"g{g}_{listname}_inner.npz"
    if p.exists():
        return np.load(p)["inner"]
    R = rows(listname)
    W = area_matrix(g)
    can = patch_mean(hull_mask(canonical_hull()[33:]), W).reshape(-1)
    inner = np.zeros((len(R), g * g), np.float32)
    for i, r in enumerate(R):
        pts = geometry(r)
        inner[i] = can if pts is None else patch_mean(hull_mask(pts[33:]), W).reshape(-1)
    np.savez(p, ids=np.array([r["id"] for r in R]), inner=inner)
    return inner


# ---------------------------------------------------------------- statistics (record helpers, imported unchanged)
_ST = None


def stats():
    """src/AR1/stats.py: a41_read.Draw (pigeonhole two-way person bootstrap), a36_read.wauc, analyze.eer."""
    global _ST
    if _ST is None:
        sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
        spec = importlib.util.spec_from_file_location("ar1stats", "/home/narolski/smad-next/src/AR1/stats.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _ST = m
    return _ST


def auc_ci(pos, pos_p, neg, neg_p, B=2000, seed=(20261111, 1), D=None):
    S = stats()
    if D is None:
        pers = sorted({x for pp in list(pos_p) + list(neg_p) for x in pp})
        D = S.Draw(pers, B, list(seed))
    a, c = S.wauc_ci(D, pos, pos_p, neg, neg_p)
    return a, c


def eer(bona, morph):
    return 100 * stats().A.eer(np.asarray(bona, float), np.asarray(morph, float))


def eer_ci(bona, bona_p, morph, morph_p, B=2000, seed=(20261111, 1)):
    S = stats()
    pers = sorted({x for pp in list(bona_p) + list(morph_p) for x in pp})
    D = S.Draw(pers, B, list(seed))
    wb = D.wb([(p[0],) for p in bona_p])
    wm = D.wm([(p[0], p[1]) for p in morph_p])
    rep = 100 * S.A.eer_weighted(np.asarray(bona, float), np.asarray(morph, float), wb, wm)
    return eer(bona, morph), S.ci(rep)


def shift_ci(base, base_p, new, new_p, B=2000, seed=(20261111, 1)):
    """(mean(new) - mean(base)) / sd(base), person bootstrap (host counts as weights)."""
    base, new = np.asarray(base, float), np.asarray(new, float)
    pt = (new.mean() - base.mean()) / base.std(ddof=1)
    S = stats()
    pers = sorted({p[0] for p in list(base_p) + list(new_p)})
    D = S.Draw(pers, B, list(seed))
    wb, wn = D.wb([(p[0],) for p in base_p]), D.wb([(p[0],) for p in new_p])
    mb = (wb * base).sum(1) / wb.sum(1)
    mn = (wn * new).sum(1) / wn.sum(1)
    sb = np.sqrt((wb * (base - mb[:, None]) ** 2).sum(1) / wb.sum(1))
    return float(pt), S.ci((mn - mb) / sb)


def cluster_mean_ci(vals, groups, B=2000, seed=20261111):
    vals = np.asarray(vals, float)
    gs = sorted(set(groups))
    gi = np.array([gs.index(g) for g in groups])
    C = np.random.default_rng(seed).multinomial(len(gs), np.full(len(gs), 1 / len(gs)), size=B)
    w = C[:, gi].astype(float)
    rep = (w * vals).sum(1) / np.maximum(w.sum(1), 1e-12)
    return float(vals.mean()), [float(x) for x in np.percentile(rep, [2.5, 97.5])]

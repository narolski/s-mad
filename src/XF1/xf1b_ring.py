"""XF1 revision b: per-pair halo-ring share (second pre-run check, finding 3; the reviewer's measurement,
experiments/reviews/scripts_xf1/ring.py, restated as a pinned input). Ring = the face-only blanking hull (convex hull of
rint(0.5*tem(H) + 0.5*tem(B)), as src/AR1/blank.py hull_mask) minus the FaceMorpher tool's mask (the convex hull of
rint((tem(H)+tem(B))/2), eroded by a 10x10 kernel, as the tool's blender). ring_share = ring pixels / hull pixels.
Read-only on the images; CPU only. Also checks, per pair, that W equals raw H and FM(H,B) equals the unwarped
average of H and B inside the ring (the DATA caveat), and prints the counts.
  python3 -I xf1b_ring.py  -> /mnt/t7/smad_next/XF1/xf1b_ring.csv (host, ring_share, ring_share_t)"""
import csv, hashlib, json, pathlib, sys, time
import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
ROWS = pathlib.Path("/mnt/t7/smad_next/XF1/xf1b_rows.csv")
ROWS_SHA = "4adcf914fba651f3b1b1ccfc5ea4b3e03155357aa5c84804180513da5925b271"
SRC = pathlib.Path("/mnt/t7/smad_next/MS1/ffhq/src")
OUT = pathlib.Path("/mnt/t7/smad_next/XF1/xf1b_ring.csv")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    import cv2
    import ar1_common as K
    assert sha(ROWS) == ROWS_SHA
    rows = [r for r in csv.DictReader(open(ROWS)) if r["form"] == "whole"]
    by = {(r["klass"], r["host"]): r for r in rows}
    hosts = sorted({r["host"] for r in rows})
    res, okW, okF = {}, 0, 0
    for h in hosts:
        p = by[("FMHB", h)]["partner"]
        ph, pb = K.read_tem(SRC / f"{h.split(':')[1]}.tem"), K.read_tem(SRC / f"{p.split(':')[1]}.tem")
        H = cv2.imread(by[("H", h)]["src"]); B = cv2.imread(str(SRC / f"{p.split(':')[1]}.png"))
        F = cv2.imread(by[("FMHB", h)]["src"]); W = cv2.imread(by[("WARP", h)]["src"])
        me = np.zeros(H.shape[:2], np.uint8); cv2.fillConvexPoly(me, cv2.convexHull(np.rint((ph + pb) / 2).astype(np.int32)), 255)
        me = cv2.erode(me, np.ones((10, 10), np.uint8)) > 0
        hull = np.zeros(H.shape[:2], np.uint8); cv2.fillConvexPoly(hull, cv2.convexHull(np.rint(0.5 * ph + 0.5 * pb).astype(np.int32)), 1)
        hull = hull > 0
        ring = hull & ~me
        res[h] = float(ring.sum() / hull.sum())
        okW += bool((W[ring] == H[ring]).all()); okF += bool((F[ring] == cv2.addWeighted(H, 0.5, B, 0.5, 0)[ring]).all())
    q = np.quantile(list(res.values()), [1 / 3, 2 / 3])
    if OUT.exists():
        OUT.rename(OUT.with_name(OUT.name + f".bak-{time.strftime('%Y%m%d%H%M%S')}"))
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["host", "ring_share", "ring_share_t"])
        for h in hosts:
            w.writerow([h, f"{res[h]:.6f}", int(np.searchsorted(q, res[h], side="right"))])
    v = np.array(list(res.values()))
    print(json.dumps(dict(pairs=len(hosts), ring_equals_H_in_W=okW, ring_equals_avg_in_FM=okF, median=float(np.median(v)),
                          min=float(v.min()), max=float(v.max()), sha256=sha(OUT))))


if __name__ == "__main__":
    main()

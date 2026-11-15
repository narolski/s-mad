"""Threshold transfer on unseen genuine sources (TT1): border-matched references by constant-colour region blanking
(an allowed image operation; approved by the lead 12 Nov). No other image operation.
For each R_cam image (417, by id) and each family f (FAMILIES order): one U_p frame of family f (frames sorted by id) is
drawn with numpy.random.default_rng(20261121); mask = the largest exactly-zero region connected to the frame edge of that
aligned frame (8-connected component of pixels whose maximum over channels is 0, touching the frame edge, most pixels;
registration TT1-S 2.3, review M3);
the reference frame's pixels under the mask are set to (0,0,0) -> 2,919 PNGs. Then each R_ffhq image (2,000, by id) gets
one mask drawn, with the same generator, from all U_p frames sorted by id -> 2,000 PNGs. Lossless PNG (cv2.imwrite).
Both frames are canonical 512x512 (same eye positions), so the mask needs no warp.
Out: /mnt/t7/smad_next/TT1/border_ref/<new id>.png and border_ref.csv (id, kind, ref_id, family, mask_id, masked_frac,
sha256).
  python3 -I build_border_ref.py [--limit 8]"""
import argparse
import csv
import pathlib
import sys

import cv2
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402


def edge_mask(frame):
    z = (frame.max(2) == 0).astype(np.uint8)
    n, lab = cv2.connectedComponents(z, connectivity=8)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge = [k for k in edge if k != 0]
    if not edge:
        return np.zeros(z.shape, bool)
    sizes = [(int((lab == k).sum()), k) for k in edge]
    return lab == max(sizes)[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    rows = [r for r in T.tt1_rows() if r["primary"]]
    refs = T.ref_rows()
    byfam = {f: sorted((r for r in rows if r["family"] == f), key=lambda r: r["id"]) for f in T.FAMILIES}
    allp = sorted(rows, key=lambda r: r["id"])
    rng = np.random.default_rng(20261121)
    plan = []
    for f in T.FAMILIES:
        for r in refs["R_cam"]:
            m = byfam[f][int(rng.integers(len(byfam[f])))]
            plan.append(("R_cam_border", r, f, m))
    for r in refs["R_ffhq"]:
        m = allp[int(rng.integers(len(allp)))]
        plan.append(("R_ffhq_border", r, m["family"], m))
    if a.limit:
        plan = plan[:a.limit // 2] + plan[-(a.limit - a.limit // 2):]
    od = T.OUT / ("border_ref_test" if a.limit else "border_ref")
    od.mkdir(parents=True, exist_ok=True)
    out = []
    for kind, r, f, m in plan:
        ref = cv2.imread(str(T.PN1T / "data" / r["path"]))
        msk = cv2.imread(m["aligned_path"])
        assert ref is not None and msk is not None and ref.shape == msk.shape == (512, 512, 3), (r["path"], m["id"])
        black = edge_mask(msk)
        img = ref.copy()
        img[black] = 0
        nid = f"bref_{r['id']}__{f}" if kind == "R_cam_border" else f"bref_{r['id']}"
        p = od / f"{nid}.png"
        cv2.imwrite(str(p), img)
        out.append(dict(id=nid, kind=kind, ref_id=r["id"], ref_host=r["host"], family=f, mask_id=m["id"],
                        masked_frac=round(float(black.mean()), 6), path=str(p), sha256=T.sha(p)))
    mf = T.OUT / ("border_ref_test.csv" if a.limit else "border_ref.csv")
    with open(mf, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("rows", len(out), "manifest", mf, T.sha(mf))


if __name__ == "__main__":
    main()

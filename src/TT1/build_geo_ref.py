"""Threshold transfer on unseen genuine sources (TT1): crop-geometry-matched references (registration TT1-S section 2.4,
commit 01557ce; parameters fixed there before this script ran).
For each of the 417 R_cam canonical 512 frames and each geometry group:
  1. integer slice to the group's median crop box (crop_geometry.json): g224 rows 84:476 cols 60:451; g112 rows 21:423
     cols 53:455 (lossless, no resampling);
  2. e7_branch(P, crop, med_ied) of src/AF0/soften.py, imported unchanged (pin asserted): native IED from prep_eval.kps;
     prep_eval.degrade(img, "R", scale = med_ied / native IED) (INTER_AREA) when native IED > med_ied; prep_eval.align;
     med_ied: g224 76.94715, g112 37.6995;
  3. lossless PNG (cv2.imwrite) to /mnt/t7/smad_next/TT1/geo_ref/<group>/bgeo_<group>_<ref id>.png; manifest geo_ref.csv
     (id, group, ref_id, ref_host, aligned, native_ied, scale, crop shape, sha256).
  python -I build_geo_ref.py [--limit 8]   (DGX venv, thread caps, nice 10)"""
import argparse
import csv
import hashlib
import importlib.util
import pathlib
import sys

import cv2

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

SOFTEN = pathlib.Path("/home/narolski/smad-next/src/AF0/soften.py")
SOFTEN_SHA = "aa90f2719e13b934b5de0171925f1cec13b22722d48f4eea5ee8a9273ded4212"
GROUPS = {"g224": ((84, 476, 60, 451), 76.94715), "g112": ((21, 423, 53, 455), 37.6995)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    assert T.sha(SOFTEN) == SOFTEN_SHA, "soften.py not at its pin"
    spec = importlib.util.spec_from_file_location("soften", SOFTEN)
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)
    P = S.load_pe()                                   # asserts the prep_eval.py pin
    refs = T.ref_rows()["R_cam"]
    if a.limit:
        refs = refs[:a.limit // 2]
    od = T.OUT / ("geo_ref_test" if a.limit else "geo_ref")
    out = []
    for g, ((y0, y1, x0, x1), med) in GROUPS.items():
        (od / g).mkdir(parents=True, exist_ok=True)
        for r in refs:
            img = cv2.imread(str(T.PN1T / "data" / r["path"]))
            assert img is not None and img.shape == (512, 512, 3), r["path"]
            crop = img[y0:y1, x0:x1].copy()
            al, ok, nied, scale = S.e7_branch(P, crop, med)
            nid = f"bgeo_{g}_{r['id']}"
            p = od / g / f"{nid}.png"
            if al is None:                            # no face in the crop: e7_branch returns nothing; record, no image
                out.append(dict(id=nid, group=g, ref_id=r["id"], ref_host=r["host"], aligned=0, native_ied=nied,
                                scale="", crop_hw=f"{crop.shape[0]}x{crop.shape[1]}", path="", sha256=""))
                continue
            cv2.imwrite(str(p), al)
            out.append(dict(id=nid, group=g, ref_id=r["id"], ref_host=r["host"], aligned=int(bool(ok)),
                            native_ied=round(float(nied), 4), scale=round(float(scale), 6),
                            crop_hw=f"{crop.shape[0]}x{crop.shape[1]}", path=str(p), sha256=T.sha(p)))
    mf = T.OUT / ("geo_ref_test.csv" if a.limit else "geo_ref.csv")
    with open(mf, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("rows", len(out), "aligned", sum(int(x["aligned"]) for x in out), "manifest", mf, T.sha(mf))


if __name__ == "__main__":
    main()

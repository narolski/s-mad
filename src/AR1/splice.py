"""Amendment 7 (spliced inner-face morph) and amendment 8 (scoring lists for the AF0 softened copies).

splice : S4 = R2w4 with the R4 pixels copied inside the face hull (hull of the 106-point R4 geometry, mean of H and B
         .tem, drawn with cv2.fillConvexPoly as blank.py); S3 = R2w with the R3 pixels inside the R3 hull (mean of H and S).
         Pure pixel copy, no blur, no resampling. Blanked copies (grey 128) of S4 and R2w4 with the R4 hull, of S3 and
         R2w with the R3 hull, background- and face-blanked. Writes OUT/img/frgcferet/<tool>/{S4,S3}/,
         OUT/blank_splice/<variant>/<rung>_<tool>_<stem>.png and OUT/manifest_splice.csv (id, path, pool, tool, rung,
         p1, p2, variant, box_src, lm_src); box_src = manifest id whose RGB-MTCNN box is reused (blanked rows), '' = detect.
soft   : OUT/manifest_soft.csv from the AF0 lists (id, path, tool, rung, strength, p1, p2).
boxes  : OUT/crops/boxes_splice.json for the blanked splice rows (boxes of their unblanked source).
  python3 -I splice.py splice|soft|boxes [--limit 8]
"""
import argparse
import csv
import json
import pathlib
import sys
from multiprocessing import Pool

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

GREY = (128, 128, 128)


def hull(tem_a, tem_b, shape):
    import cv2
    import numpy as np
    pts = 0.5 * K.read_tem(tem_a) + 0.5 * K.read_tem(tem_b)
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillConvexPoly(m, cv2.convexHull(np.rint(pts).astype(np.int32)), 1)
    return m.astype(bool)


def job(a):
    import cv2
    tool, stem, H, X, base_rung, src_rung, out_rung = a
    d = K.OUT / "img/frgcferet" / tool
    base = cv2.imread(str(d / base_rung / f"{stem}.png"))
    src = cv2.imread(str(d / src_rung / f"{stem}.png"))
    m = hull(H[:-4] + ".tem", X[:-4] + ".tem", base.shape)
    sp = base.copy()
    sp[m] = src[m]
    o = d / out_rung / f"{stem}.png"
    o.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(o), sp)
    outs = {}
    for rung, img in ((out_rung, sp), (base_rung, base)):
        for v in ("bg", "face"):
            b = img.copy()
            if v == "bg":
                b[~m] = GREY
            else:
                b[m] = GREY
            p = K.OUT / "blank_splice" / v / f"{rung}_{tool}_{stem}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(p), b)
            outs[(rung, v)] = str(p)
    return tool, stem, out_rung, str(o), outs


def splice(limit):
    pool = list(csv.DictReader(open(K.OUT / "pool.csv")))[: limit or None]
    man = {(r["tool"], r["rung"], r["p1"]): r["id"] for r in csv.DictReader(open(K.OUT / "manifest.csv"))
           if r["pool"] == "frgcferet"}
    jobs = []
    for tool in ("opencv", "facemorpher"):
        for r in pool:
            s = r["pid"].replace(":", "_")
            jobs.append((tool, s, r["H"], r["B"], "R2w4", "R4", "S4"))
            jobs.append((tool, s, r["H"], r["S"], "R2w", "R3", "S3"))
    with Pool(6) as p:
        res = p.map(job, jobs, chunksize=8)
    rows = []
    byp = {r["pid"].replace(":", "_"): r for r in pool}
    for tool, stem, rung, path, outs in res:
        r = byp[stem]
        sid = f"sp_{rung}_{tool}_{stem}"
        rows.append(dict(id=sid, path=path, pool="frgcferet", tool=tool, rung=rung, p1=r["pid"],
                         p2=r["B_pid"] if rung == "S4" else r["pid"], variant="native", box_src="", lm_src=path))
        base = "R2w4" if rung == "S4" else "R2w"
        for (rg, v), p_ in outs.items():
            src_id = sid if rg == rung else man[(tool, base, r["pid"])]
            src_path = path if rg == rung else str(K.OUT / "img/frgcferet" / tool / base / f"{stem}.png")
            rows.append(dict(id=f"sp_{rg}_{tool}_{stem}__{v}_{rung}hull", path=p_, pool="frgcferet", tool=tool,
                             rung=rg, p1=r["pid"], p2=r["B_pid"] if rg in ("S4",) else r["pid"], variant=v + "_" + rung + "hull",
                             box_src=src_id, lm_src=src_path))
    out = K.OUT / ("manifest_splice.csv" if not limit else "manifest_splice_smoke.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(out, len(rows))


def soft():
    rows = []
    for r in csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/ar1soft.csv")):
        st = r["rung"].split("_soft_")[1]
        rows.append(dict(id="sf_" + r["id"], path=r["path"], tool=r["tool"], rung=r["rung"].split("_")[0] + "soft",
                         strength=st, p1=r["p1"], p2=r["p2"]))
    for r in csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/ar1soft_ladder.csv")):
        tool = r["source_path"].split("/")[-3]
        stem = pathlib.Path(r["output_path"]).stem
        rows.append(dict(id=f"sfl_{r['rung']}_{r['strength']}_{tool}_{stem}", path=r["output_path"], tool=tool,
                         rung=r["rung"] + "soft", strength=r["strength"], p1=r["host"], p2=r["person"] if r["rung"] == "R4" else r["host"]))
    for r in rows:
        assert pathlib.Path(r["path"]).exists() and not K.forbidden(r["path"])
    with open(K.OUT / "manifest_soft.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows))


def boxes():
    main = json.load(open(K.OUT / "crops/boxes_main.json"))
    sp = {}
    for f in sorted((K.OUT / "crops/splice").glob("boxes*.jsonl")):
        for ln in open(f):
            d = json.loads(ln)
            sp[d["id"]] = d["box"]
    out = {}
    for r in csv.DictReader(open(K.OUT / "manifest_splice.csv")):
        if r["box_src"]:
            out[r["id"]] = sp.get(r["box_src"], main.get(r["box_src"]))
    json.dump(out, open(K.OUT / "crops/boxes_splice.json", "w"))
    print(len(out), sum(v is None for v in out.values()), "without box")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("splice", "soft", "boxes"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"splice": lambda: splice(a.limit), "soft": soft, "boxes": boxes}[a.stage]()

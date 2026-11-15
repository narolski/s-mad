"""Signal isolation by paired differences (PD1), cross-family transfer: list of landmark images to extract in the common
feature space (diffusion / GAN space). Read-only sources; nothing is built, copied or written as an image.

Sets (all OpenCV-style engine, FRGC + colorFERET hosts of the landmark ladder (AR1), unless stated):
  Lad    : x0 R0, x1 R2w, xm R3m, x2 R3, x3 R4                        (landmark/lists/ar1.csv)
  Lbench : registered softened-genuine sets of the landmark family: FRLL native + FRLL E7 OpenCV, corrected MAD22
           native + corrected MAD22 E7 OpenCV                         (landmark/lists/bench.csv; FRLL persons, scored only)
  Lsoft  : existing shrink-and-enlarge copies of 200 hosts' photos at two strengths (landmark/lists/ar1soft.csv)
  Lblank : existing constant-grey blanked x1 and x3 (bg = face only, face = surround only) (landmark/verify/lists/blank.csv)
  Lx1g   : matched-geometry warp-only image R2w4                       (landmark/verify/lists/r2w4.csv)
Amendment 1 (diffusion CLIP cache made with TF32 off): the diffusion images are re-extracted with the common code
  Dtr    : diffusion training hosts, x0 / x1 / x2 / x3                 (diffae/lists/items.csv set tr)
  Dev    : registered flag set, FRLL native (mordiff_bona|orig) and E7 (mordiff|resmatch)   (set ev; scored only)
  Df256  : FRLL 20-step and 100-step reconstructions, 20-step two-person morphs (set f256 D20, rec100, B20; diagnostic)

  python3 -I tf_items.py            -> /mnt/t7/smad_next/PD1/transfer/lists/landmark_items.csv
"""
import collections
import csv
import pathlib
import sys

SRC = pathlib.Path("/mnt/t7/smad_next/PD1/landmark")
OUT = pathlib.Path("/mnt/t7/smad_next/PD1/transfer")
COLS = ["id", "path", "set", "rung", "p1", "p2", "var", "pool"]


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def rows(p):
    return list(csv.DictReader(open(p)))


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    out = []
    xn = {"R0": "x0", "R2w": "x1", "R3m": "xm", "R3": "x2", "R4": "x3"}
    for r in rows(SRC / "lists/ar1.csv"):
        if r["pool"] != "frgcferet":
            continue
        if (r["rung"] == "R0" and r["tool"] == "none") or (r["tool"] == "opencv" and r["rung"] in xn):
            out.append(dict(id=r["id"], path=r["path"], set="Lad", rung=xn[r["rung"]], p1=r["p1"], p2=r["p2"], var="",
                            pool=r["pool"]))
    keep = {("frllm_frll_bona", "native"), ("frllm_opencv", "e7"), ("mad22_BonaFide", "native"), ("mad22_OpenCV", "e7")}
    seen = set()
    for r in rows(SRC / "lists/bench.csv"):
        k = (r["pool"], r["rung"])
        if k in keep and (r["id"], r["pool"]) not in seen:
            seen.add((r["id"], r["pool"]))
            out.append(dict(id=f"{r['pool']}|{r['id']}", path=r["path"], set="Lbench", rung=r["rung"], p1=r["p1"],
                            p2=r["p2"], var="", pool=r["pool"]))
    for r in rows(SRC / "lists/ar1soft.csv"):
        if r["tool"] == "none":
            out.append(dict(id=r["id"], path=r["path"], set="Lsoft", rung=r["rung"], p1=r["p1"], p2=r["p2"], var="",
                            pool=r["pool"]))
    for r in rows(SRC / "verify/lists/blank.csv"):
        if r["tool"] == "opencv" and r["rung"] in ("R2w", "R4"):
            out.append(dict(id=r["id"], path=r["path"], set="Lblank", rung=xn[r["rung"]], p1=r["p1"], p2=r["p2"],
                            var=r["var"], pool="frgcferet"))
    for r in rows(SRC / "verify/lists/r2w4.csv"):
        if r["tool"] == "opencv":
            out.append(dict(id=r["id"], path=r["path"], set="Lx1g", rung="x1g", p1=r["p1"], p2=r["p2"], var="",
                            pool="frgcferet"))
    for r in rows("/mnt/t7/smad_next/PD1/diffae/lists/items.csv"):
        st = {"tr": "Dtr"}.get(r["set"])
        if r["set"] == "ev" and r["arm"] in ("mordiff_bona|orig", "mordiff|resmatch"):
            st = "Dev"
        if r["set"] == "f256" and r["arm"] in ("D20", "rec100", "B20"):
            st = "Df256"
        if st:
            out.append(dict(id=r["id"], path=r["path"], set=st, rung=r["rung"] if st != "Dev" else r["arm"],
                            p1=r["persons"], p2="", var=r["arm"], pool="diffusion"))
    ids = [r["id"] for r in out]
    assert len(ids) == len(set(ids)), "duplicate ids"
    for r in out:
        assert not forbidden(r["path"]), r["path"]
        assert pathlib.Path(r["path"]).is_file(), r["path"]
    (OUT / "lists").mkdir(parents=True, exist_ok=True)
    with open(OUT / "lists/landmark_items.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)
    c = collections.Counter((r["set"], r["rung"], r["var"], r["pool"]) for r in out)
    for k in sorted(c):
        print(k, c[k])
    print("total", len(out))


if __name__ == "__main__":
    main()

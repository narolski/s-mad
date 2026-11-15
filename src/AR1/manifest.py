"""AR1 master manifest of every image to score (after build.py, graded_fm.py, frll_prep.py).
Columns: id, path, pool, tool, rung, p1, p2, level, kind, tem1, tem2, w1
  kind: frame512 (our tool-size builds and the aligned source frames), raw (FRLL raw photos and published morph files),
        pe (prep_eval eval frames of FRLL: frll_bona orig, the E7 resmatch frames, published morph frames)
  p1 / p2: host / second contributor person ids (p2 = p1 for single-person images); tem1 / tem2 / w1: the geometry
  of the face (AR4 masks): hull of w1 * tem1 + (1 - w1) * tem2.
"""
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

PUB = pathlib.Path("/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london")
RAWF = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")


def tem(p):
    return str(p)[:-4] + ".tem" if p else ""


def main():
    rows = []

    def add(**r):
        r.setdefault("level", "")
        r.setdefault("tem1", "")
        r.setdefault("tem2", "")
        r.setdefault("w1", "")
        r["id"] = f"{len(rows):06d}"
        assert pathlib.Path(r["path"]).exists(), r["path"]
        rows.append(r)

    for pool, pcsv in (("frgcferet", K.OUT / "pool.csv"), ("frll", K.OUT / "pool_frll.csv")):
        P = list(csv.DictReader(open(pcsv)))
        for r in P:
            add(path=r["H"], pool=pool, tool="none", rung="R0", p1=r["pid"], p2=r["pid"], kind="frame512",
                tem1=tem(r["H"]), tem2=tem(r["H"]), w1=1.0)
        for tool in ("opencv", "facemorpher"):
            for r in P:
                s = r["pid"].replace(":", "_")
                geo = {"R2": (r["H"], r["H"], r["pid"]), "R3": (r["H"], r["S"], r["pid"]),
                       "R4": (r["H"], r["B"], r["B_pid"]), "NC": (r["S"], r["H"], r["pid"])}
                for g, (a, b, p2) in geo.items():
                    add(path=str(K.OUT / "img" / pool / tool / g / f"{s}.png"), pool=pool, tool=tool, rung=g,
                        p1=r["pid"], p2=p2, kind="frame512", tem1=tem(a), tem2=tem(b), w1=0.5)
        if pool == "frgcferet":
            gd = K.OUT / "img" / pool / "fm_graded"
            byp = {r["pid"]: r for r in P}
            for d in sorted(gd.glob("m0*")):
                m = int(d.name[1:]) / 100
                for f in sorted(d.glob("*.png")):
                    pid = f.stem.replace("_", ":", 1)
                    r = byp[pid]
                    add(path=str(f), pool=pool, tool="facemorpher_lib", rung="G", level=m, p1=pid,
                        p2=r["B_pid"] if m > 0 else pid, kind="frame512", tem1=tem(r["H"]), tem2=tem(r["B"]), w1=1 - m)
    # FRLL bridge: our same-pair morphs
    for tool in ("opencv", "facemorpher"):
        for r in csv.DictReader(open(K.OUT / f"bridge_frll_{tool}.csv")):
            a, b = r["pid"].split("|")
            add(path=str(K.OUT / "img/frll_bridge" / tool / "BR" / f"{r['out_stem']}.png"), pool="frll_bridge",
                tool=tool, rung="R4ours", p1=a, p2=b, kind="frame512", tem1=tem(r["a"]), tem2=tem(r["b"]), w1=0.5)
            add(path=r["published"], pool="frll_bench", tool=tool, rung="R4pub", p1=a, p2=b, kind="raw")
    for f in sorted(RAWF.glob("neutral_front/*_03.jpg")) + sorted(RAWF.glob("smiling_front/*_08.jpg")):
        add(path=str(f), pool="frll_bench", tool="none", rung="R0raw", p1=f"frll:{f.stem[:3]}", p2=f"frll:{f.stem[:3]}",
            kind="raw")
    # prep_eval frames (eval.csv set frllm rows only: frll_bona orig, resmatch opencv / facemorpher, published orig)
    for r in csv.DictReader(open(K.DATA / "manifests/eval.csv")):
        if r["set"] != "frllm":
            continue
        name = pathlib.Path(r["path"]).name
        if r["family"] == "frll_bona" and r["variant"] == "orig":
            add(path=str(K.DATA / r["path"]), pool="frll_bench", tool="none", rung="R0f", p1=f"frll:{name[:3]}",
                p2=f"frll:{name[:3]}", kind="pe")
        elif r["variant"] == "resmatch" and r["family"] in ("opencv", "facemorpher"):
            add(path=str(K.DATA / r["path"]), pool="frll_bench", tool=r["family"], rung="R1f", p1=f"frll:{name[:3]}",
                p2=f"frll:{name[:3]}", kind="pe")
        elif r["variant"] == "orig" and r["family"] in ("opencv", "facemorpher") and r["label"] == "1":
            a, b = name.split("_")[:2]
            add(path=str(K.DATA / r["path"]), pool="frll_bench", tool=r["family"], rung="R4f", p1=f"frll:{a}",
                p2=f"frll:{b[:3]}", kind="pe")
    # lead request (appended so earlier ids stay stable): R2w warp-only and R3m mirror self-morph, both pools and tools
    for pool, pcsv in (("frgcferet", K.OUT / "pool_m.csv"), ("frll", K.OUT / "pool_frll_m.csv")):
        if not pcsv.exists():
            continue
        P = list(csv.DictReader(open(pcsv)))
        for tool in ("opencv", "facemorpher"):
            for r in P:
                s = r["pid"].replace(":", "_")
                for g, b in (("R2w", r["S"]), ("R3m", r["M"])):
                    add(path=str(K.OUT / "img" / pool / tool / g / f"{s}.png"), pool=pool, tool=tool, rung=g,
                        p1=r["pid"], p2=r["pid"], kind="frame512", tem1=tem(r["H"]), tem2=tem(b), w1=0.5)
    # lead request 2 (appended): R2wm, warp-only toward H's own mirrored shape (H file only), both pools and tools
    for pool, pcsv in (("frgcferet", K.OUT / "pool_m.csv"), ("frll", K.OUT / "pool_frll_m.csv")):
        if not pcsv.exists() or not (K.OUT / "img" / pool / "opencv" / "R2wm").exists():
            continue
        for tool in ("opencv", "facemorpher"):
            for r in csv.DictReader(open(pcsv)):
                s = r["pid"].replace(":", "_")
                add(path=str(K.OUT / "img" / pool / tool / "R2wm" / f"{s}.png"), pool=pool, tool=tool, rung="R2wm",
                    p1=r["pid"], p2=r["pid"], kind="frame512", tem1=tem(r["H"]), tem2=tem(r["M"]), w1=0.5)
    # amendment 4 (appended): R2w4, warp-only toward the R4 mean shape (H and B), primary pool, both tools
    if (K.OUT / "img/frgcferet/opencv/R2w4").exists():
        for tool in ("opencv", "facemorpher"):
            for r in csv.DictReader(open(K.OUT / "pool.csv")):
                s = r["pid"].replace(":", "_")
                add(path=str(K.OUT / "img/frgcferet" / tool / "R2w4" / f"{s}.png"), pool="frgcferet", tool=tool,
                    rung="R2w4", p1=r["pid"], p2=r["pid"], kind="frame512", tem1=tem(r["H"]), tem2=tem(r["B"]), w1=0.5)
    for r in rows:
        assert not K.forbidden(r["path"])
    cols = ["id", "path", "pool", "tool", "rung", "p1", "p2", "level", "kind", "tem1", "tem2", "w1"]
    with open(K.OUT / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    import collections
    c = collections.Counter((r["pool"], r["tool"], r["rung"]) for r in rows)
    for k in sorted(c):
        print(k, c[k])
    print("total", len(rows))


if __name__ == "__main__":
    main()

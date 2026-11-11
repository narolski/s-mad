"""AF0 extraction lists (one CSV per set) under OUT/lists/.

Columns: id, path, set, cell, rung, tool, p1, p2, geom, g1, g2, w1
  geom = lm   : g1 = .npy of the 106 mean-shape landmarks written by af_morph (AF0 morphs)
         tem  : face geometry = w1 * tem(g1) + (1 - w1) * tem(g2) (AF0 photos; AR1 images, as AR1's AR4 masks)
         fixed: no landmarks stored for the frame (benchmark frames): the fixed canonical face hull (see heads.py)
Sets:
  af0   : every AF0 image (morphs, unprocessed photos)                                     [train / val only]
  ar1   : AR1 ladder, pools frgcferet and frll: R0, R2, R2w, R3, R3m, R4, NC per tool (files that exist)
  bench : FRLL-Morphs (eval.csv set frllm: frll_bona orig; amsl, facemorpher, opencv, webmorph orig; their E7
          'resmatch' genuine frames) and corrected MAD22 (canonical E7 inputs v3: native BonaFide, FaceMorpher,
          OpenCV, Webmorph; e7 FaceMorpher, OpenCV, Webmorph).  Evaluation only.
  python3 -I lists.py
"""
import collections
import csv
import pathlib

OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
MAD22 = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
COLS = ["id", "path", "set", "cell", "rung", "tool", "p1", "p2", "geom", "g1", "g2", "w1"]


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def write(name, rows):
    for r in rows:
        assert not forbidden(r["path"]), r["path"]
        assert pathlib.Path(r["path"]).exists(), r["path"]
    assert len({r["id"] for r in rows}) == len(rows)
    (OUT / "lists").mkdir(parents=True, exist_ok=True)
    with open(OUT / "lists" / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    c = collections.Counter((r["cell"], r["rung"], r["tool"]) for r in rows)
    print(name, len(rows))
    for k in sorted(c):
        print("  ", k, c[k])


def main():
    rows = []
    for r in csv.DictReader(open(OUT / "manifest.csv")):
        if r["kind"] == "morph":
            if not pathlib.Path(r["image"]).exists():
                continue
            rows.append(dict(id=r["id"], path=r["image"], set="af0", cell=r["split"], rung=r["field"], tool=r["db"],
                             p1=r["pid_A"], p2=r["pid_B"], geom="lm", g1=r["map"][:-4] + "_lm.npy", g2="", w1=""))
        else:
            rows.append(dict(id=r["id"], path=r["image"], set="af0", cell=r["split"], rung="photo", tool=r["db"],
                             p1=r["pid_A"], p2=r["pid_A"], geom="tem", g1=r["A"][:-4] + ".tem",
                             g2=r["A"][:-4] + ".tem", w1="1.0"))
    write("af0", rows)
    rows = []
    for r in csv.DictReader(open(AR1 / "manifest.csv")):
        if r["pool"] in ("frgcferet", "frll") and r["rung"] in ("R0", "R2", "R2w", "R3", "R3m", "R4", "NC"):
            if not pathlib.Path(r["path"]).exists():
                continue
            rows.append(dict(id="ar1_" + r["id"], path=r["path"], set="ar1", cell=r["pool"], rung=r["rung"],
                             tool=r["tool"], p1=r["p1"], p2=r["p2"], geom="tem", g1=r["tem1"], g2=r["tem2"],
                             w1=r["w1"]))
    write("ar1", rows)
    rows = []
    for r in csv.DictReader(open(DATA / "manifests/eval.csv")):
        if r["set"] != "frllm":
            continue
        fam, var, name = r["family"], r["variant"], pathlib.Path(r["path"]).name
        if fam == "frll_bona" and var == "orig":
            rung, p1, p2 = "native", f"frll:{name[:3]}", f"frll:{name[:3]}"
        elif fam in ("amsl", "facemorpher", "opencv", "webmorph") and var == "resmatch":
            rung, p1, p2 = "e7", f"frll:{name[:3]}", f"frll:{name[:3]}"
        elif fam in ("amsl", "facemorpher", "opencv", "webmorph") and var == "orig":
            a, b = name.split("_")[:2]
            rung, p1, p2 = "morph", f"frll:{a}", f"frll:{b[:3]}"
        else:
            continue
        rows.append(dict(id="frllm_" + r["id"], path=str(DATA / r["path"]), set="bench", cell="frllm_" + fam,
                         rung=rung, tool=fam, p1=p1, p2=p2, geom="fixed", g1="", g2="", w1=""))
    for fam in ("BonaFide", "FaceMorpher", "OpenCV", "Webmorph"):
        for p in sorted((MAD22 / "native" / fam).glob("*.png")):
            if fam == "BonaFide":
                rung, p1, p2 = "native", f"frll:{p.stem[:3]}", f"frll:{p.stem[:3]}"
            else:
                a, b = p.stem.split("-vs-")
                rung, p1, p2 = "morph", f"frll:{a[:3]}", f"frll:{b[:3]}"
            rows.append(dict(id=f"mad22_native_{fam}_{p.stem}", path=str(p), set="bench", cell="mad22_" + fam,
                             rung=rung, tool=fam, p1=p1, p2=p2, geom="fixed", g1="", g2="", w1=""))
    for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
        for p in sorted((MAD22 / "e7" / fam).glob("*.png")):
            rows.append(dict(id=f"mad22_e7_{fam}_{p.stem}", path=str(p), set="bench", cell="mad22_" + fam, rung="e7",
                             tool=fam, p1=f"frll:{p.stem[:3]}", p2=f"frll:{p.stem[:3]}", geom="fixed", g1="", g2="",
                             w1=""))
    write("bench", rows)


if __name__ == "__main__":
    main()

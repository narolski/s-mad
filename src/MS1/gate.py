"""MS1 gates (prereg part 1, section 4).

path  : the MS1 wrappers re-run on existing AF0 / AR1 rows must reproduce the existing files pixel for pixel:
        4 AF0 u50, 4 AF0 zero (af_morph._job), 4 AF0 halves (ghost.py line), 4 AF0 fm61 copies (soften.e7_branch),
        4 AR1 R4 OpenCV (78_tool_morph.py). Outputs in OUT/gate/ (scratch of this check).
pixel : on 8 MS1 FFHQ u50 pairs: af_morph u50 == unchanged hm.morph; zero == clip(W_A); MS1 R4 (78) of 8 ladder
        hosts == hm.morph of the same pair.
  python3 -I gate.py path | pixel
"""
import csv
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

G = C.OUT / "gate"
AF0 = pathlib.Path("/mnt/t7/smad_next/AF0")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")


def cmp(a, b):
    import cv2
    x, y = cv2.imread(str(a)), cv2.imread(str(b))
    if x is None or y is None or x.shape != y.shape:
        return dict(a=str(a), b=str(b), equal=False, max_abs=None)
    return dict(a=str(a), b=str(b), equal=bool((x == y).all()), max_abs=int(np.abs(x.astype(int) - y.astype(int)).max()))


def path():
    import cv2
    AM = C.load(C.SRC / "AF0/af_morph.py", "af_morph")
    S = C.load(C.SRC / "AF0/soften.py", "af0soften")
    P = S.load_pe()
    G.mkdir(parents=True, exist_ok=True)
    man = list(csv.DictReader(open(AF0 / "manifest.csv")))
    res = dict(u50=[], zero=[], half=[], fm61=[], r4=[])
    for field in ("u50", "zero"):
        for r in [x for x in man if x["split"] == "train" and x["field"] == field and pathlib.Path(x["image"]).exists()][:4]:
            q = dict(r, image=str(G / f"{r['id']}.png"), map=str(G / f"{r['id']}.npy"))
            AM._job(q)
            res[field].append(cmp(q["image"], r["image"]))
    hv = list(csv.DictReader(open(AF0 / "halves.csv")))
    byid = {r["id"]: r for r in man}
    for h in [x for x in hv if "_u50_" in x["id"] and x["split"] == "train"][:4]:
        r = byid[h["id"].rsplit("_", 1)[0]]
        a, b = cv2.imread(r["A"]), cv2.imread(r["B"])
        wA, wB, _, _ = AM.warped_pair(a, AM.parse_tem(r["A"][:-4] + ".tem"), b, AM.parse_tem(r["B"][:-4] + ".tem"))
        w = wA if h["field"] == "halfA" else wB
        o = G / f"{h['id']}.png"
        cv2.imwrite(str(o), np.clip(w, 0, 255).astype(np.uint8))
        res["half"].append(cmp(o, h["path"]))
    soft = [x for x in csv.DictReader(open(AF0 / "soft_soft_src.csv")) if x["strength"] == "fm61" and x["path"]]
    src = {r["id"]: r for r in csv.DictReader(open(AF0 / "lists" / "soft_src.csv"))}
    for s in soft[:4]:
        img, flag, nied, sc = S.e7_branch(P, cv2.imread(src[s["src_id"]]["path"]), S.STRENGTHS["fm61"])
        o = G / f"{s['src_id']}_fm61.png"
        cv2.imwrite(str(o), img)
        res["fm61"].append(cmp(o, s["path"]))
    ar1 = [r for r in csv.DictReader(open(AR1 / "manifest.csv"))
           if r["pool"] == "frgcferet" and r["rung"] == "R4" and r["tool"] == "opencv"][:4]
    pool = {r["pid"]: r for r in csv.DictReader(open(AR1 / "pool.csv"))}
    lines = []
    for r in ar1:
        pr = pool[r["p1"]]
        o = G / f"ar1_{r['id']}.png"
        lines.append("\t".join([pr["H"], pr["H"][:-4] + ".tem", pr["B"], pr["B"][:-4] + ".tem", str(o)]))
    (G / "r4.tsv").write_text("\n".join(lines) + "\n")
    out = subprocess.run(["/home/narolski/mambamorph-code/.venv-spark/bin/python", str(C.MC / "scripts/78_tool_morph.py"),
                          str(G / "r4.tsv"), "opencv"], capture_output=True, text=True)
    for r in ar1:
        res["r4"].append(cmp(G / f"ar1_{r['id']}.png", r["path"]))
    res["all_equal"] = all(x["equal"] for k in ("u50", "zero", "half", "fm61", "r4") for x in res[k])
    res["n"] = sum(len(res[k]) for k in ("u50", "zero", "half", "fm61", "r4"))
    res["sha256"] = {str(p): C.sha(p) for p in C.UNCHANGED}
    json.dump(res, open(C.RES / "gate_path.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "sha256"}, indent=1))


def pixel():
    import cv2
    AM = C.load(C.SRC / "AF0/af_morph.py", "af_morph")
    O = C.OUT / "ffhq"
    pairs = [r for r in csv.DictReader(open(O / "lists/af0_pairs.csv")) if r["split"] == "train"]
    res = dict(u50=[], zero=[], r4=[])
    for field in ("u50", "zero"):
        for r in [x for x in pairs if x["field"] == field][:8]:
            a, b = cv2.imread(r["A"]), cv2.imread(r["B"])
            la, lb = AM.parse_tem(r["A"][:-4] + ".tem"), AM.parse_tem(r["B"][:-4] + ".tem")
            mine = cv2.imread(r["image"])
            if field == "u50":
                ref = AM.hm.morph(a, la, b, lb)
            else:
                wA, _, _, _ = AM.warped_pair(a, la, b, lb)
                ref = np.clip(wA, 0, 255).astype(np.uint8)
            res[field].append(dict(id=r["id"], equal=bool((mine == ref).all()),
                                   max_abs=int(np.abs(mine.astype(int) - ref.astype(int)).max())))
    for r in list(csv.DictReader(open(O / "lists/ladder.csv")))[:8]:
        a, b = cv2.imread(r["H"]), cv2.imread(r["B"])
        ref = AM.hm.morph(a, AM.parse_tem(r["H"][:-4] + ".tem"), b, AM.parse_tem(r["B"][:-4] + ".tem"))
        mine = cv2.imread(r["R4"])
        res["r4"].append(dict(pid=r["pid"], equal=bool((mine == ref).all()),
                              max_abs=int(np.abs(mine.astype(int) - ref.astype(int)).max())))
    res["all_equal"] = all(x["equal"] for k in ("u50", "zero", "r4") for x in res[k])
    json.dump(res, open(C.RES / "gate_pixel.json", "w"), indent=1)
    print(json.dumps(res["all_equal"]), json.dumps({k: [x["max_abs"] for x in res[k]] for k in ("u50", "zero", "r4")}))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"path": path, "pixel": pixel}[sys.argv[1]]()

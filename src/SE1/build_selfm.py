"""Seam-shortcut training arm (SE1): mirror self-morphs of AF0 photos, built with approved operations only.

For every AF0 training photo of the Sb manifest (518) and every AF0 development (validation) photo of the FS1
evaluation manifest (126):
  Hm      = cv2.flip(H, 1)  (lossless mirror; written as PNG and read back pixel-equal)
  Hm.tem  = H's 106 points mirrored (x -> W-1-x) and re-indexed by AR1's measured left-right permutation
            (/mnt/t7/smad_next/AR1/mirror_perm106.json), exactly as src/AR1/variants.py mirror() does for R3m
  selfm   = the UNCHANGED OpenCV-style engine scripts/78_tool_morph.py (sha256 b8a389f1...) on (H, Hm)
            = the same engine and frame as the AF0 u50 two-person morphs (AF0 verified u50 == 78 CLI output)
No blur, no resampling, no new image code beyond the lossless flip and the .tem text.

Check first (--check): the same code path rebuilds AR1's R3m (OpenCV) for 8 ladder hosts pixel for pixel.
  python3 -I build_selfm.py --check
  python3 -I build_selfm.py [--limit 8]
Writes /mnt/t7/smad_next/SE1/{mirror,img/selfm}/<id>.png and /mnt/t7/smad_next/SE1/selfm_build.csv (+ log json).
"""
import argparse
import csv
import hashlib
import json
import pathlib
import subprocess
import sys
import time

PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
S78 = pathlib.Path("/home/narolski/mambamorph-code/scripts/78_tool_morph.py")
S78_SHA = "b8a389f10ce685fc95b50c69cbcdcf3d44a818ed3d6c04a79849534365cf12b1"
PERM = pathlib.Path("/mnt/t7/smad_next/AR1/mirror_perm106.json")
AF0_MAN = pathlib.Path("/mnt/t7/smad_next/AF0/manifest.csv")
SB = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv")
EV = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/SE1")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def read_tem(path):
    import numpy as np
    lines = open(path).read().splitlines()
    n = int(lines[0].strip())
    return np.array([list(map(float, lines[i].split())) for i in range(1, n + 1)], np.float32)


def write_tem(path, pts):                      # src/AR1/variants.py write_tem (73_delin_align format)
    with open(path, "w") as fo:
        fo.write(f"{len(pts)}\n")
        for x, y in pts:
            fo.write(f"{float(x):.4f}\t{float(y):.4f}\n")
        fo.write("0\n")


def mirror(H, out_png):
    import cv2
    import numpy as np
    perm = np.array(json.load(open(PERM))["perm"])
    assert (perm[perm] == np.arange(106)).all()
    img = cv2.imread(str(H))
    W = img.shape[1]
    fl = cv2.flip(img, 1)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_png), fl)
    assert (cv2.imread(str(out_png)) == fl).all()
    lm = read_tem(str(H)[:-4] + ".tem")
    assert lm.shape == (106, 2), lm.shape
    m = lm[perm].copy()
    m[:, 0] = W - 1 - m[:, 0]
    write_tem(str(out_png)[:-4] + ".tem", m)


def run78(jobs, work, workers=2):
    """jobs: list of (H, Hm, out). Unchanged CLI, chunked over `workers` processes."""
    work.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join([str(a), str(a)[:-4] + ".tem", str(b), str(b)[:-4] + ".tem", str(o)]) for a, b, o in jobs]
    procs = []
    for i in range(workers):
        ch = work / f"cv_chunk{i}.tsv"
        ch.write_text("\n".join(lines[i::workers]) + "\n")
        procs.append(subprocess.Popen([PY, str(S78), str(ch), "opencv"], stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True))
    outs = [p.communicate()[0] for p in procs]
    if any(p.returncode for p in procs):
        sys.exit("78_tool_morph failed:\n" + "\n".join(outs))
    return outs


def check():
    """Rebuild AR1's R3m (OpenCV) for 8 ladder hosts through this file's mirror() + run78(); must be pixel-equal."""
    import cv2
    rows = list(csv.DictReader(open("/mnt/t7/smad_next/AR1/pool_m.csv")))[:8]
    d = OUT / "check_r3m"
    jobs = []
    for r in rows:
        st = r["pid"].replace(":", "_")
        mp = d / "mirror" / f"{st}.png"
        mirror(r["H"], mp)
        jobs.append((r["H"], mp, d / "R3m" / f"{st}.png"))
    (d / "R3m").mkdir(parents=True, exist_ok=True)
    run78(jobs, d / "_work")
    res = []
    for r, (_, mp, o) in zip(rows, jobs):
        st = r["pid"].replace(":", "_")
        ref = cv2.imread(f"/mnt/t7/smad_next/AR1/img/frgcferet/opencv/R3m/{st}.png")
        mine = cv2.imread(str(o))
        refm = cv2.imread(r["M"])
        res.append(dict(host=r["pid"], mirror_equal=bool((cv2.imread(str(mp)) == refm).all()),
                        tem_equal=open(str(mp)[:-4] + ".tem").read() == open(r["M"][:-4] + ".tem").read(),
                        r3m_equal=bool(mine is not None and ref is not None and (mine == ref).all())))
    json.dump(dict(s78_sha256=sha(S78), rows=res), open(OUT / "check_r3m.json", "w"), indent=1)
    print(json.dumps(res, indent=0))
    if not all(x["mirror_equal"] and x["tem_equal"] and x["r3m_equal"] for x in res):
        sys.exit("CHECK FAILED")
    print("CHECK OK: AR1 R3m reproduced pixel for pixel on 8 hosts")


def targets():
    man = {r["id"]: r for r in csv.DictReader(open(AF0_MAN))}
    tr = sorted({r["id"] for r in csv.DictReader(open(SB)) if r["kind"] == "af0_photo"})
    dv = sorted({r["id"] for r in csv.DictReader(open(EV))
                 if r["fam"] == "af0" and r["rung"] == "photo" and r["strength"] == "" and r["role"] == "dev"})
    out = []
    for split, ids in (("train", tr), ("dev", dv)):
        for i in ids:
            m = man[i]
            assert m["kind"] == "photo" and m["pid_A"] == m["pid_B"], i
            assert m["image"] == m["A"], i
            out.append(dict(id=i, split=split, person=m["pid_A"], db=m["db"], H=m["image"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    assert sha(S78) == S78_SHA, "78_tool_morph.py is not at its pin"
    if a.check:
        return check()
    T = targets()[: a.limit or None]
    t0 = time.time()
    jobs = []
    for t in T:
        mp = OUT / "mirror" / f"{t['id']}.png"
        mirror(t["H"], mp)
        o = OUT / ("img_limit" if a.limit else "img") / "selfm" / f"{t['id']}_selfm.png"
        o.parent.mkdir(parents=True, exist_ok=True)
        t.update(M=str(mp), path=str(o))
        if not o.exists():
            jobs.append((t["H"], mp, o))
    run78(jobs, OUT / "_work", a.workers)
    miss = [t["id"] for t in T if not pathlib.Path(t["path"]).exists()]
    for t in T:
        t["sha256"] = sha(t["path"]) if pathlib.Path(t["path"]).exists() else ""
    name = "selfm_build" + (f"_limit{a.limit}" if a.limit else "")
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(T[0]))
        w.writeheader()
        w.writerows(T)
    log = dict(n=len(T), built=len(jobs), missing=miss, seconds=round(time.time() - t0, 1), s78_sha256=S78_SHA,
               by_split={s: sum(t["split"] == s for t in T) for s in ("train", "dev")})
    json.dump(log, open(OUT / f"{name}.json", "w"), indent=1)
    print(json.dumps(log))
    if miss:
        sys.exit("missing outputs")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

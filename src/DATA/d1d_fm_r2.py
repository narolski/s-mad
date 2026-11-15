"""D1d: one-photo FaceMorpher renders R2 = tool(H, H) on the 900 MS1 FFHQ frames (lead's go, 13 Nov 2026).

Runs the UNCHANGED scripts/96_facemorpher_tool.py (sha256 954e9c02..., the same file AR1 used) on pairs (H, H) with
H's own .tem. No other image operation. Inputs: /mnt/t7/smad_next/MS1/ffhq/persons.csv (frame, tem; never modified).
Outputs: /mnt/t7/smad_next/DATA/D1d/facemorpher/R2/<key>.png, manifest.csv (pid, key, part, frame, frame_sha256,
out, out_sha256), SHA256SUMS, build_log.json.

  OMP_NUM_THREADS=2 ... nice -n 10 python3 -I d1d_fm_r2.py --workers 2 [--limit 8]
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
S96 = pathlib.Path("/home/narolski/mambamorph-code/scripts/96_facemorpher_tool.py")
S96_SHA = "954e9c02e7360847dee379f66f17e6a0fb70a272ad3f2ae08390244248f311d3"
PERSONS = pathlib.Path("/mnt/t7/smad_next/MS1/ffhq/persons.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/DATA/D1d")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if sha(S96) != S96_SHA:
        sys.exit("96_facemorpher_tool.py changed: refusing")
    rows = list(csv.DictReader(open(PERSONS)))
    if a.limit:
        rows = rows[: a.limit]
    sub = "test8" if a.limit else "facemorpher"
    od = OUT / sub / "R2"
    od.mkdir(parents=True, exist_ok=True)
    work = OUT / "_work"
    work.mkdir(parents=True, exist_ok=True)
    lines, todo = [], 0
    for r in rows:
        assert r["frame"].endswith(".png") and r["tem"] == r["frame"][:-4] + ".tem"
        out = od / f"{r['key']}.png"
        if not out.exists():
            lines.append("\t".join([r["frame"], r["tem"], r["frame"], r["tem"], str(out)]))
            todo += 1
    t0 = time.time()
    if lines:
        pt = work / f"pairs_{sub}.tsv"
        pt.write_text("\n".join(lines) + "\n")
        p = subprocess.run([PY, str(S96), str(pt), str(od), str(a.workers)], capture_output=True, text=True)
        if p.returncode:
            sys.exit("96_facemorpher_tool failed:\n" + p.stdout + p.stderr)
    dt = time.time() - t0
    man, missing = [], []
    for r in rows:
        out = od / f"{r['key']}.png"
        if not out.exists():
            missing.append(r["key"])
            continue
        man.append(dict(pid=r["pid"], key=r["key"], part=r["part"], rung="R2", engine="facemorpher",
                        frame=r["frame"], frame_sha256=sha(r["frame"]), out=str(out), out_sha256=sha(out)))
    mp = OUT / ("manifest.csv" if not a.limit else "manifest_test8.csv")
    with open(mp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys()) if man else ["pid"])
        w.writeheader()
        w.writerows(man)
    sp = OUT / ("SHA256SUMS" if not a.limit else "SHA256SUMS_test8")
    sp.write_text("".join(f"{m['out_sha256']}  {pathlib.Path(m['out']).relative_to(OUT)}\n" for m in man))
    log = dict(rows=len(rows), attempted=todo, present=len(man), n_missing=len(missing), missing=missing[:50],
               seconds=round(dt, 1), images_per_minute=round(60 * todo / dt, 1) if todo and dt > 0 else None,
               s96_sha256=S96_SHA, workers=a.workers, host=os.uname().nodename,
               manifest_sha256=sha(mp), persons_csv_sha256=sha(PERSONS))
    json.dump(log, open(OUT / ("build_log.json" if not a.limit else "build_log_test8.json"), "w"), indent=1)
    print(json.dumps(log))
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()

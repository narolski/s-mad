"""AR1 stage 2: run the UNCHANGED landmark morphers on the pool (pipeline-only, twin, morph, negative control).

  OpenCV      : scripts/78_tool_morph.py <pairs.tsv> opencv   (unchanged; single process, so chunked lists in parallel)
  FaceMorpher : scripts/96_facemorpher_tool.py <pairs.tsv> <outdir> <workers>   (unchanged; own Pool)
Inputs are the 512^2 aligned frames + 106-point .tem of pool.csv; outputs are lossless PNG at tool size (512^2).
Rungs per host p (pool.csv): R2 = tool(H_p, H_p), R3 = tool(H_p, S_p), R4 = tool(H_p, B_p), NC = tool(S_p, H_p).
Bridge (FRLL only): tool(a_03, b_03) for every published FRLL-Morphs pair of that tool.

  python3 -I build.py --pool POOL.csv --name frgcferet --rungs R2,R3,R4,NC --workers 12 [--limit 8] [--tag smoke]
  python3 -I build.py --pairs BRIDGE.csv --name frll_bridge --workers 12 ...   (rows: pid,a,b,out_stem)
Writes OUT/img/<name>/<tool>/<rung>/<stem>.png and OUT/img/<name>/build_log.json (timings: images per minute).
"""
import argparse
import csv
import json
import os
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402

PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
S78 = K.MC / "scripts/78_tool_morph.py"
S96 = K.MC / "scripts/96_facemorpher_tool.py"
S78_SHA = K.sha(S78)
S96_SHA = K.sha(S96)


def stem(pid):
    return pid.replace(":", "_")


def jobs_from_pool(rows, rungs):
    out = []
    for r in rows:
        roles = {"R2": (r["H"], r["H"]), "R3": (r["H"], r["S"]), "R4": (r["H"], r["B"]), "NC": (r["S"], r["H"])}
        if r.get("M"):                                   # R3m: H with its lossless mirror (mirror .tem, variants.py)
            roles["R3m"] = (r["H"], r["M"])
        for g in rungs:
            a, b = roles[g]
            out.append((g, stem(r["pid"]), a, b))
    return out


def tsv_line(a, b, out):
    a, b = str(a), str(b)
    return "\t".join([a, a[:-4] + ".tem", b, b[:-4] + ".tem", str(out)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool")
    ap.add_argument("--pairs")
    ap.add_argument("--name", required=True)
    ap.add_argument("--rungs", default="R2,R3,R4,NC")
    ap.add_argument("--tools", default="opencv,facemorpher")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    root = K.OUT / "img" / a.name
    work = root / "_work"
    work.mkdir(parents=True, exist_ok=True)
    if a.pool:
        rows = list(csv.DictReader(open(a.pool)))[: a.limit or None]
        jobs = jobs_from_pool(rows, a.rungs.split(","))
    else:
        rows = list(csv.DictReader(open(a.pairs)))[: a.limit or None]
        jobs = [("BR", r["out_stem"], r["a"], r["b"]) for r in rows]
    log = dict(name=a.name, n_jobs_per_tool=len(jobs), workers=a.workers, s78_sha256=S78_SHA, s96_sha256=S96_SHA,
               host=os.uname().nodename, cpu_count=os.cpu_count(), tools={})
    for tool in a.tools.split(","):
        for g in sorted({j[0] for j in jobs}):
            (root / tool / g).mkdir(parents=True, exist_ok=True)
        todo = [j for j in jobs if not (root / tool / j[0] / f"{j[1]}.png").exists()]
        t0 = time.time()
        if tool == "opencv":
            lines = [tsv_line(x, y, root / tool / g / f"{s}.png") for g, s, x, y in todo]
            procs = []
            for i in range(a.workers):
                ch = work / f"cv_chunk{i}.tsv"
                ch.write_text("\n".join(lines[i::a.workers]) + "\n")
                procs.append(subprocess.Popen([PY, str(S78), str(ch), "opencv"], stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT, text=True))
            outs = [p.communicate()[0] for p in procs]
            if any(p.returncode for p in procs):
                sys.exit("78_tool_morph failed:\n" + "\n".join(outs))
        else:
            for g in sorted({j[0] for j in todo}):
                lines = [tsv_line(x, y, root / tool / g / f"{s}.png") for gg, s, x, y in todo if gg == g]
                pt = work / f"fm_{g}.tsv"
                pt.write_text("\n".join(lines) + "\n")
                r = subprocess.run([PY, str(S96), str(pt), str(root / tool / g), str(a.workers)], capture_output=True,
                                   text=True)
                if r.returncode:
                    sys.exit("96_facemorpher_tool failed:\n" + r.stdout + r.stderr)
        dt = time.time() - t0
        made = sum((root / tool / g / f"{s}.png").exists() for g, s, _, _ in jobs)
        missing = [f"{g}/{s}" for g, s, _, _ in jobs if not (root / tool / g / f"{s}.png").exists()]
        log["tools"][tool] = dict(attempted=len(todo), present=made, missing=missing[:50], n_missing=len(missing),
                                  seconds=round(dt, 1),
                                  images_per_minute=round(60 * len(todo) / dt, 1) if dt > 0 and todo else None)
        print(tool, json.dumps(log["tools"][tool]), flush=True)
    lp = root / ("build_log.json" if not a.limit else f"build_log_limit{a.limit}.json")
    json.dump(log, open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()

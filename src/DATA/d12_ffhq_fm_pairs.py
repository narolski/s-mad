"""D12: FFHQ FaceMorpher two-person morphs FM(H, B) on the MS1 hold-out frames (registration: REQUESTS.md D12, 77a5513).

Persons: MS1 FFHQ hold-out frames with a D1d render (key 08060 left out), minus any training person.
Pairing: derangement by minimum-cost assignment on |pre-alignment eye distance| (frames_ied.csv), self-pairs forbidden.
No sex matching (no label exists). Build: unchanged scripts/96_facemorpher_tool.py (D1d file, sha 954e9c02...).
  OMP_NUM_THREADS=1 nice -n 19 python -I d12_ffhq_fm_pairs.py --workers 2 [--limit 8]
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import runpy
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import linear_sum_assignment

PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
S96 = pathlib.Path("/home/narolski/mambamorph-code/scripts/96_facemorpher_tool.py")
S96_SHA = "954e9c02e7360847dee379f66f17e6a0fb70a272ad3f2ae08390244248f311d3"
T7 = pathlib.Path("/mnt/t7/smad_next")
OUT = T7 / "DATA/D12"   # D12a: --no-mutual writes to DATA/D12a
HERE = pathlib.Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-mutual", action="store_true", help="D12 amendment a: forbid 2-cycles")
    a = ap.parse_args()
    global OUT
    if a.no_mutual:
        OUT = T7 / "DATA/D12a"
    assert sha(S96) == S96_SHA, "96_facemorpher_tool.py changed"
    d1d = {r["key"]: r for r in csv.DictReader(open(T7 / "DATA/D1d/manifest.csv")) if r["part"] == "holdout"}
    ied = {r["person"]: float(r["ied_src"]) for r in csv.DictReader(open(T7 / "DATA/D5/frames_ied.csv"))
           if r["source"] == "ms1_ffhq" and r["ied_src"]}
    g = runpy.run_path(str(HERE / "battery_persons.py"))
    trainp = set().union(*g["arms"].values())
    persons = sorted(k for k in d1d if f"ffhq:{k}" not in trainp and f"ffhq:{k}" in ied)
    dropped_training = sorted(k for k in d1d if f"ffhq:{k}" in trainp)
    x = np.array([ied[f"ffhq:{k}"] for k in persons])
    cost = np.abs(x[:, None] - x[None, :])
    np.fill_diagonal(cost, 1e9)
    ri, ci = linear_sum_assignment(cost)
    rounds = 1
    while a.no_mutual:
        m = dict(zip(ri, ci))
        mutual = [(i, j) for i, j in m.items() if m.get(j) == i and i < j]
        if not mutual:
            break
        for i, j in mutual:
            cost[i, j] = cost[j, i] = 1e9
        ri, ci = linear_sum_assignment(cost)
        rounds += 1
    pairs = [dict(host=persons[i], partner=persons[j], ied_host=round(x[i], 4), ied_partner=round(x[j], 4),
                  cost=round(float(cost[i, j]), 4)) for i, j in zip(ri, ci)]
    assert all(p["host"] != p["partner"] for p in pairs) and len({p["partner"] for p in pairs}) == len(pairs)
    if a.limit:
        pairs = pairs[: a.limit]
    sub = "test8" if a.limit else "facemorpher"
    od = OUT / sub / "R4"
    od.mkdir(parents=True, exist_ok=True)
    work = OUT / "_work"
    work.mkdir(parents=True, exist_ok=True)
    pp = OUT / ("pairs.csv" if not a.limit else "pairs_test8.csv")
    with open(pp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pairs[0].keys()))
        w.writeheader()
        w.writerows(pairs)
    lines = []
    for p in pairs:
        fh, fb = d1d[p["host"]]["frame"], d1d[p["partner"]]["frame"]
        o = od / f"{p['host']}__{p['partner']}.png"
        if not o.exists():
            lines.append("\t".join([fh, fh[:-4] + ".tem", fb, fb[:-4] + ".tem", str(o)]))
    t0 = time.time()
    tool_out = ""
    if lines:
        pt = work / f"pairs_{sub}.tsv"
        pt.write_text("\n".join(lines) + "\n")
        r = subprocess.run([PY, str(S96), str(pt), str(od), str(a.workers)], capture_output=True, text=True)
        tool_out = r.stdout + r.stderr
        if r.returncode:
            sys.exit("96_facemorpher_tool failed:\n" + tool_out)
    dt = time.time() - t0
    man, fails = [], []
    for p in pairs:
        o = od / f"{p['host']}__{p['partner']}.png"
        if not o.exists():
            fails.append(dict(host=p["host"], partner=p["partner"],
                              tool_message=next((l for l in tool_out.splitlines() if o.name in l), "")))
            continue
        H, B = d1d[p["host"]], d1d[p["partner"]]
        man.append(dict(host=f"ffhq:{p['host']}", partner=f"ffhq:{p['partner']}", rung="R4", engine="facemorpher",
                        frame_host=H["frame"], frame_host_sha256=H["frame_sha256"], frame_partner=B["frame"],
                        frame_partner_sha256=B["frame_sha256"], out=str(o), out_sha256=sha(o),
                        d1d_render_host=H["out"], d1d_render_host_sha256=H["out_sha256"]))
    sfx = "" if not a.limit else "_test8"
    mp = OUT / f"manifest{sfx}.csv"
    with open(mp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys()))
        w.writeheader()
        w.writerows(man)
    with open(OUT / f"failures{sfx}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["host", "partner", "tool_message"])
        w.writeheader()
        w.writerows(fails)
    (OUT / f"SHA256SUMS{sfx}").write_text("".join(f"{m['out_sha256']}  {pathlib.Path(m['out']).relative_to(OUT)}\n" for m in man))
    mm = {p["host"]: p["partner"] for p in pairs}
    log = dict(rule="D12a no mutual pairs" if a.no_mutual else "D12", assignment_rounds=rounds,
               mutual_pairs=sum(mm.get(mm[h]) == h for h in mm) // 2, persons=len(persons), dropped_training_persons=len(dropped_training), pairs=len(pairs), present=len(man),
               failures=len(fails), seconds=round(dt, 1), s96_sha256=S96_SHA, workers=a.workers,
               host=os.uname().nodename, pairs_sha256=sha(pp), manifest_sha256=sha(mp),
               cost_median=float(np.median([p["cost"] for p in pairs])), cost_max=float(max(p["cost"] for p in pairs)))
    json.dump(log, open(OUT / f"build_log{sfx}.json", "w"), indent=1)
    print(json.dumps(log))


if __name__ == "__main__":
    main()

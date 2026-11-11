"""SM1 morph builds with the UNCHANGED OpenCV-style engine (scripts/68_hires_morph.morph as loaded by
scripts/78_tool_morph.py), plus the engine's own two warped source images ("halves") where the list asks for them.

Wrapper (the src/AF0/af_morph.warped_pair logic): while hm.morph runs unchanged, its module-level _warp_tri is wrapped
by a recorder that only remembers the two destination arrays (the engine's float32 wA, wB); the morph returned is the
engine's own output. Halves = clip(W, 0, 255).astype(uint8) (the engine's own clip and cast). Asserted on EVERY pair
with halves: max |0.5 hA + 0.5 hB - morph| <= 1 grey level. Landmarks: the .tem files of the list, read with 78's
parse_tem. Output: cv2.imwrite PNG (lossless). No other pixel operation.

  python3 -I build.py --list LIST.csv [--workers 6] [--limit 8]
  python3 -I build.py --list LIST.csv --verify-cli 8     (wrapper morph vs the unchanged 78 command line, pixel-equal)
  python3 -I build.py --list ar1h.csv --check-ref        (also: morph == the list's ref file, the AR1 OpenCV R4 PNG)
List columns: id, a, ta, b, tb, out, halves (0/1) [, ref]. Halves go to <out stem>_hA.png / _hB.png.
"""
import argparse
import csv
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

import os  # noqa: E402

S78 = pathlib.Path(os.environ.get("SM1_S78", str(K.S78)))          # WCSS: the packed copy (same bytes, sha logged)
S68 = S78.parent / "68_hires_morph.py"
ROOT = None                                                         # --root: list paths are relative to it
_spec = importlib.util.spec_from_file_location("tool78", S78)
tool78 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool78)          # module top-level loads 68 as "hm68", exactly as 78 does
hm = tool78.hm
parse_tem = tool78.parse_tem
CHECK_REF = False


def warped_pair(imgA, lmA, imgB, lmB):
    rec = []
    orig = hm._warp_tri

    def recorder(src, dst, tri_s, tri_d):
        if not any(dst is d for d in rec):
            rec.append(dst)
        return orig(src, dst, tri_s, tri_d)

    hm._warp_tri = recorder
    try:
        m = hm.morph(imgA, lmA, imgB, lmB)
    finally:
        hm._warp_tri = orig
    assert len(rec) == 2, "engine structure changed"
    return rec[0], rec[1], m


def halves_names(out):
    return out[:-4] + "_hA.png", out[:-4] + "_hB.png"


def _abs(r):
    if not ROOT:
        return r
    r = dict(r)
    for k in ("a", "ta", "b", "tb", "out", "ref"):
        if r.get(k) and not r[k].startswith("/"):
            r[k] = str(pathlib.Path(ROOT) / r[k])
    return r


def _job(r):
    import cv2
    cv2.setNumThreads(1)
    r = _abs(r)
    out = r["out"]
    want_h = r.get("halves", "0") == "1"
    hA_p, hB_p = halves_names(out)
    if pathlib.Path(out).exists() and (not want_h or (pathlib.Path(hA_p).exists() and pathlib.Path(hB_p).exists())) \
            and not CHECK_REF:
        return r["id"], "exists", None
    a, b = cv2.imread(r["a"]), cv2.imread(r["b"])
    if a is None or b is None:
        return r["id"], "unreadable", None
    la, lb = parse_tem(r["ta"]), parse_tem(r["tb"])
    try:
        wA, wB, m = warped_pair(a, la, b, lb)
    except (cv2.error, ValueError) as e:                 # the engine's own failure: 78 counts it and writes nothing
        return r["id"], "tool_failed", dict(error=str(e).splitlines()[-1][:200])
    info = {}
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(out, m)
    if want_h:
        hA = np.clip(wA, 0, 255).astype(np.uint8)
        hB = np.clip(wB, 0, 255).astype(np.uint8)
        d = np.abs(0.5 * hA.astype(np.float64) + 0.5 * hB.astype(np.float64) - m.astype(np.float64)).max()
        assert d <= 1.0, (r["id"], d)
        info["halves_maxabs"] = float(d)
        assert cv2.imwrite(hA_p, hA) and cv2.imwrite(hB_p, hB)
    if CHECK_REF and r.get("ref"):
        ref = cv2.imread(r["ref"])
        info["ref_maxabs"] = int(np.abs(ref.astype(int) - m.astype(int)).max())
        if want_h:
            info["ref_halves_maxabs"] = float(np.abs(0.5 * hA.astype(np.float64) + 0.5 * hB.astype(np.float64)
                                                     - ref.astype(np.float64)).max())
            assert info["ref_halves_maxabs"] <= 1.0, (r["id"], info)
    return r["id"], "made", info


def verify_cli(rows, n):
    """Wrapper morph vs the unchanged 78 command line (subprocess, its own TSV), pixel by pixel."""
    import cv2
    rows = [_abs(r) for r in rows[:n]]
    res = []
    with tempfile.TemporaryDirectory(dir=ROOT or str(K.OUT)) as td:
        tsv = pathlib.Path(td) / "pairs.tsv"
        tsv.write_text("".join("\t".join([r["a"], r["ta"], r["b"], r["tb"], f"{td}/{i}.png"]) + "\n"
                               for i, r in enumerate(rows)))
        p = subprocess.run([sys.executable, "-I", str(S78), str(tsv), "opencv"], capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        for i, r in enumerate(rows):
            cli = cv2.imread(f"{td}/{i}.png")
            _, _, m = warped_pair(cv2.imread(r["a"]), parse_tem(r["ta"]), cv2.imread(r["b"]), parse_tem(r["tb"]))
            res.append(dict(id=r["id"], maxabs=int(np.abs(cli.astype(int) - m.astype(int)).max()),
                            shape=list(m.shape)))
    return res


def main():
    global CHECK_REF
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--verify-cli", type=int, default=0)
    ap.add_argument("--check-ref", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--log-dir", default=str(K.OUT / "logs"))
    ap.add_argument("--compare", default=None, help="CSV (out, ref): pixel comparison of our outputs with references")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    global ROOT
    ROOT = a.root
    CHECK_REF = a.check_ref
    if a.compare:
        import cv2
        res = []
        for r in csv.DictReader(open(a.compare)):
            o = cv2.imread(str(pathlib.Path(ROOT or "/") / r["out"]))
            f = cv2.imread(str(pathlib.Path(ROOT or "/") / r["ref"]))
            res.append(dict(out=r["out"], maxabs=int(np.abs(o.astype(int) - f.astype(int)).max()),
                            n_diff_px=int((o != f).any(2).sum())))
        out = dict(n=len(res), max_abs=max(x["maxabs"] for x in res), cv2=cv2.__version__, np=np.__version__,
                   rows=res)
        pathlib.Path(a.log_dir).mkdir(parents=True, exist_ok=True)
        json.dump(out, open(pathlib.Path(a.log_dir) / "compare_ref.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
        return
    rows = list(csv.DictReader(open(a.list)))[: a.limit or None]
    name = pathlib.Path(a.list).stem
    if a.verify_cli:
        res = verify_cli(rows, a.verify_cli)
        out = dict(list=a.list, n=len(res), max_abs=max(x["maxabs"] for x in res), pairs=res,
                   s68_sha256=K.sha(S68), s78_sha256=K.sha(S78))
        pathlib.Path(a.log_dir).mkdir(parents=True, exist_ok=True)
        json.dump(out, open(pathlib.Path(a.log_dir) / f"verify_cli_{name}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in out.items() if k != "pairs"}))
        return
    t0 = time.time()
    from multiprocessing import Pool
    st, infos = {}, {}
    with Pool(a.workers) as p:
        for i, (rid, s, info) in enumerate(p.imap_unordered(_job, rows, chunksize=8)):
            st[s] = st.get(s, 0) + 1
            if info:
                infos[rid] = info
            if (i + 1) % 2000 == 0:
                print(f"{i + 1}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
    dt = time.time() - t0
    log = dict(list=a.list, rows=len(rows), status=st, seconds=round(dt, 1), workers=a.workers,
               images_per_minute=round(60 * st.get("made", 0) / dt, 1) if st.get("made") else None,
               halves_maxabs_max=max((v.get("halves_maxabs", 0) for v in infos.values()), default=None),
               n_halves_checked=sum("halves_maxabs" in v for v in infos.values()),
               tool_failed=sorted(k for k, v in infos.items() if "error" in v)[:100],
               ref_maxabs_max=max((v["ref_maxabs"] for v in infos.values() if "ref_maxabs" in v), default=None),
               ref_halves_maxabs_max=max((v["ref_halves_maxabs"] for v in infos.values() if "ref_halves_maxabs" in v),
                                         default=None),
               s68_sha256=K.sha(S68), s78_sha256=K.sha(S78))
    tag = name + (f"_limit{a.limit}" if a.limit else "")
    import cv2
    log.update(cv2=cv2.__version__, numpy=np.__version__, python=sys.version.split()[0])
    pathlib.Path(a.log_dir).mkdir(parents=True, exist_ok=True)
    json.dump(log, open(pathlib.Path(a.log_dir) / f"build_{tag}.json", "w"), indent=1)
    print(json.dumps(log), flush=True)


if __name__ == "__main__":
    main()

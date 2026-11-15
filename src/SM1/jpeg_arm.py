"""SM1 amendment A10: JPEG copies for arm (f) with the registered prep_eval.degrade (imported unchanged, sha256 pinned;
only the jpeg90 / jpeg70 branches are called on training images).

  python3 -I jpeg_arm.py verify       reproduce existing jpeg70 evaluation files byte for byte with prep_eval's own
                                      degrade + align (verification only) -> RES/jpeg_verify.json
  python3 -I jpeg_arm.py assign       fixed per-image assignment (none / jpeg90 / jpeg70) over every image that can
                                      enter arm (e) -> OUT/lists/jpeg_assign.csv (id, path, op, out)
  python3 -I jpeg_arm.py build [--workers 2] [--limit 8]   -> OUT/img/armf/<op>/<file>.png, OUT/logs/jpeg_build.json
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

PE_PATH = K.MC / "smadcvpr/prep_eval.py"
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
FL = K.OUT / "flists"
POOLS = ("train_bf", "train_arme_bfS", "train_armc_halves", "train_arme_hS", "train_armc", "train_arme_cS")
PE = None


def load_pe():
    assert K.sha(PE_PATH) == PE_SHA
    spec = importlib.util.spec_from_file_location("prep_eval", PE_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def verify():
    import cv2
    pe = load_pe()
    src_dir = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted/neutral_front")
    res = []
    for stem in ("001_03", "002_03"):
        src = src_dir / f"{stem}.jpg"
        ref = K.MC / f"smadcvpr_data/eval/frllm/frll_bona/{stem}_jpeg70.png"
        img = cv2.imread(str(src))
        aligned, ok, _ = pe.align(pe.degrade(img, "jpeg70"))
        okw, enc = cv2.imencode(".png", aligned)
        stored = cv2.imread(str(ref))
        res.append(dict(src=str(src), ref=str(ref), aligned=bool(ok),
                        png_bytes_equal=enc.tobytes() == ref.read_bytes(),
                        pixels_equal=bool((stored == aligned).all()),
                        max_abs=int(np.abs(stored.astype(int) - aligned.astype(int)).max())))
        print(res[-1], flush=True)
    out = dict(rows=res, prep_eval_sha256=PE_SHA, call='prep_eval.align(prep_eval.degrade(cv2.imread(src), "jpeg70"))')
    json.dump(out, open(K.RES / "jpeg_verify.json", "w"), indent=1)


def assign():
    rows = []
    for n in POOLS:
        for r in csv.DictReader(open(FL / f"{n}.csv")):
            h = int(hashlib.sha256(f"{K.SEED + 50}:{r['id']}".encode()).hexdigest()[:8], 16) / 2 ** 32
            op = "jpeg90" if h < 1 / 6 else "jpeg70" if h < 1 / 3 else ""
            if op:
                rows.append(dict(id=r["id"], path=r["path"], op=op,
                                 out=str(K.OUT / "img/armf" / op / (n + "__" + pathlib.Path(r["path"]).name))))
    with open(K.OUT / "lists/jpeg_assign.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    import collections
    print(len(rows), collections.Counter(r["op"] for r in rows))


def _init():
    global PE
    PE = load_pe()


def _job(r):
    import cv2
    cv2.setNumThreads(1)
    out = pathlib.Path(r["out"])
    if out.exists():
        return "exists"
    img = cv2.imread(r["path"], cv2.IMREAD_COLOR)
    if img is None:
        return "unreadable"
    deg = PE.degrade(img, r["op"])
    out.parent.mkdir(parents=True, exist_ok=True)
    okw, enc = cv2.imencode(".png", deg)
    back = cv2.imdecode(enc, cv2.IMREAD_COLOR)
    assert okw and np.array_equal(back, deg)
    out.write_bytes(enc.tobytes())
    return "ok"


def build(a):
    from multiprocessing import Pool
    rows = list(csv.DictReader(open(K.OUT / "lists/jpeg_assign.csv")))[: a.limit or None]
    t0 = time.time()
    st = {}
    with Pool(a.workers, initializer=_init) as p:
        for s in p.imap_unordered(_job, rows, chunksize=32):
            st[s] = st.get(s, 0) + 1
    log = dict(n=len(rows), status=st, seconds=round(time.time() - t0, 1), prep_eval_sha256=PE_SHA)
    (K.OUT / "logs").mkdir(exist_ok=True)
    json.dump(log, open(K.OUT / ("logs/jpeg_build.json" if not a.limit else "logs/jpeg_build_limit.json"), "w"))
    print(json.dumps(log))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("verify", "assign", "build"))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"verify": verify, "assign": assign}.get(a.cmd, lambda: build(a))()

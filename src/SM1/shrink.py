"""SM1 arm (e): the existing registered shrink step, unchanged (amendment A4).

Loads mambamorph-code-a47/smadcvpr/a47_data.py (sha256 pinned) and calls its own _init (prep_eval.py at its pin) and
_one((src, dst)): cv2.imread(IMREAD_COLOR) -> prep_eval.degrade(img, "R", scale=0.3125) (cv2.INTER_AREA 256 -> 80) ->
cv2.imencode PNG, read back and compared, bytes written. Nothing else touches pixels.

  python3 -I shrink.py verify            8 genuine renders vs the stored a47 copies (bytes equal) -> RES/shrink_verify.json
  python3 -I shrink.py run --list L.csv --out-dir D [--workers 2] [--limit 8]    (list columns id, path)
-> D/<same relative name>.png, D/shrink_log.json
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

A47 = pathlib.Path("/home/narolski/mambamorph-code-a47/smadcvpr/a47_data.py")
A47_SHA = "fcd48e1a9d0495457ca290a9fc1182c8eff4cb3ddc7a844c9a25ca5073014640"
PE = K.MC / "smadcvpr/prep_eval.py"
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
STORED = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t")


def load():
    assert K.sha(A47) == A47_SHA and K.sha(PE) == PE_SHA
    spec = importlib.util.spec_from_file_location("a47_data", A47)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _init():
    global M
    M = load()
    M._init(str(PE))


def _job(args):
    if pathlib.Path(args[1]).exists():
        return (args[0], "exists")
    return M._one((pathlib.Path(args[0]), pathlib.Path(args[1])))


def verify():
    import tempfile
    _init()
    names = sorted(p.name for p in K.BF_T.glob("*.png"))[::3125][:8]
    res = []
    with tempfile.TemporaryDirectory(dir=str(K.OUT)) as td:
        for n in names:
            r = M._one((K.BF_T / n, pathlib.Path(td) / n))
            ours, stored = (pathlib.Path(td) / n).read_bytes(), (STORED / n).read_bytes()
            res.append(dict(name=n, status=r[1], bytes_equal=ours == stored, sha_ours=hashlib.sha256(ours).hexdigest(),
                            sha_stored=hashlib.sha256(stored).hexdigest(), out_shape=r[3] if len(r) > 3 else None))
    out = dict(n=len(res), all_bytes_equal=all(x["bytes_equal"] for x in res), a47_data_sha256=A47_SHA,
               prep_eval_sha256=PE_SHA, call='prep_eval.degrade(img, "R", scale=0.3125) via a47_data._one', rows=res)
    json.dump(out, open(K.RES / "shrink_verify.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))


def run(a):
    from multiprocessing import Pool
    rows = list(csv.DictReader(open(a.list)))[: a.limit or None]
    od = pathlib.Path(a.out_dir)
    jobs = [(r["path"], str(od / pathlib.Path(r["path"]).name)) for r in rows]
    od.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    st = {}
    with Pool(a.workers, initializer=_init) as p:
        for r in p.imap_unordered(_job, jobs, chunksize=16):
            st[r[1]] = st.get(r[1], 0) + 1
    log = dict(list=a.list, n=len(jobs), status=st, seconds=round(time.time() - t0, 1), a47_data_sha256=A47_SHA,
               prep_eval_sha256=PE_SHA)
    json.dump(log, open(od / ("shrink_log.json" if not a.limit else f"shrink_log_limit{a.limit}.json"), "w"), indent=1)
    print(json.dumps(log))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("verify", "run"))
    ap.add_argument("--list")
    ap.add_argument("--out-dir")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    verify() if a.cmd == "verify" else run(a)

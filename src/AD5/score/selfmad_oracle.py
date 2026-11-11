"""Retrains of released methods (AD5): SelfMAD oracle-epoch diagnostic (prereg amendment 2), DGX.

The saved epochs (every 5) of each SelfMAD retrain are scored on the FRLL cells only (204 raw FRLL photos and the five
FRLL-Morphs families). The SelfMAD own preprocessing (rsx_selfmad_own._prep: dlib 81 landmarks, landmark box + 6.25%
margin, cv2.resize to 384) is computed ONCE per image and cached as the uint8 array that _prep produces before its
"/ 255" (exact: _prep returns cv2.resize(uint8) / 255); every epoch is then scored on the cache with the network
builder of score.py's own mode (a41g_score.selfmad_net; softmax[:, 1], logit = z1 - z0). Check (registered): for one
network, the cached path equals RS1's score.py --mode own on the same images (max |logit difference| printed).

  python3 -I selfmad_oracle.py cache --out CACHE_DIR [--workers 4]
  python3 -I selfmad_oracle.py score --cache CACHE_DIR --weights W.safetensors --name NAME --out OUT.npz
  python3 -I selfmad_oracle.py pick --scores DIR --out oracle.json     (mean native EER of the five FRLL cells)
"""
import argparse
import csv
import glob
import hashlib
import json
import pathlib
import sys

import numpy as np

RS1 = pathlib.Path("/home/narolski/smad-next/src/RS1")
sys.path.insert(0, str(RS1))
import ar1_common as K  # noqa: E402

FRLL_SETS = {"G_raw", "M_amsl", "M_facemorpher", "M_opencv", "M_stylegan", "M_webmorph"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rows_frll():
    return [r for r in csv.DictReader(open("/mnt/t7/smad_next/RS1/manifest.csv")) if r["set"] in FRLL_SETS]


def _prep_u8(path):
    import rsx_selfmad_own as RO
    x, ok = RO._prep(path)
    return np.rint(x * 255).astype(np.uint8), ok


def cache(a):
    K.add_paths(K.MC, K.W46 / "smadcvpr")
    for p in K.PINS:
        if p.parent == K.W46 / "smadcvpr":
            assert K.sha(p) == K.PINS[p], p
    import multiprocessing as mp
    import rsx_selfmad_own as RO
    rows = rows_frll()
    od = pathlib.Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    arr = np.lib.format.open_memmap(od / "x_u8.npy", mode="w+", dtype=np.uint8, shape=(len(rows), 3, 384, 384))
    ok = np.zeros(len(rows), bool)
    with mp.get_context("fork").Pool(a.workers, initializer=RO._init, initargs=(str(K.PREDICTOR81),)) as pool:
        for i, (x, k) in enumerate(pool.imap(_prep_u8, [r["src_path"] for r in rows], chunksize=8)):
            arr[i], ok[i] = x, k
    arr.flush()
    np.savez(od / "meta.npz", id=np.array([r["id"] for r in rows]), cropped=ok)
    print(json.dumps(dict(images=len(rows), no_face=int((~ok).sum()), out=str(od))))


def score(a):
    K.add_paths(K.MC, K.W46 / "smadcvpr")
    import torch
    import common as C
    import a12_released as R
    import a41g_score as S
    R.np, R.torch, R.C = np, torch, C
    m = np.load(pathlib.Path(a.cache) / "meta.npz")
    x = np.load(pathlib.Path(a.cache) / "x_u8.npy", mmap_mode="r")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = S.selfmad_net(R, str(a.weights), torch).eval().to(dev)
    logits, scores = [], []
    with torch.no_grad():
        for i in range(0, len(x), 32):
            b = torch.from_numpy(np.asarray(x[i:i + 32]).astype(np.float32) / 255).to(dev)
            out = model(b).float()
            scores += out.softmax(1)[:, 1].cpu().tolist()
            logits += (out[:, 1] - out[:, 0]).cpu().tolist()
    np.savez(a.out, id=m["id"], score=np.array(scores, np.float32), score_noTTA=np.array(scores, np.float32),
             logit_noTTA=np.array(logits, np.float32), cropped=m["cropped"], name=a.name, weights_sha256=sha(a.weights))
    print(a.name, len(logits))


def pick(a):
    sys.path.insert(0, str(RS1))
    import analyse as RA
    man = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/RS1/manifest.csv"))}
    res = {}
    for f in sorted(glob.glob(str(pathlib.Path(a.scores) / "oracle_*.npz"))):
        z = np.load(f)
        by = {}
        for i, l in zip(z["id"].tolist(), z["logit_noTTA"]):
            by.setdefault(man[i]["set"], []).append(float(l))
        eers = {c: 100 * RA.A.eer(np.array(by["G_raw"]), np.array(by[f"M_{c}"]))
                for c in ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")}
        res[pathlib.Path(f).stem] = dict(eers=eers, mean=float(np.mean(list(eers.values()))))
    best = {}
    for k, v in res.items():                         # oracle_<retrain>_e<epoch>
        net, ep = k[len("oracle_"):].rsplit("_e", 1)
        if net not in best or v["mean"] < best[net][1] or (v["mean"] == best[net][1] and int(ep) < best[net][0]):
            best[net] = (int(ep), v["mean"])
    json.dump(dict(per_epoch=res, oracle={n: dict(epoch=e, mean_eer=m) for n, (e, m) in best.items()},
                   label="oracle epoch: selected on the FRLL test data, as the public code's default does; "
                         "diagnostic only"), open(a.out, "w"), indent=1)
    print(json.dumps({n: e for n, (e, _) in best.items()}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cache")
    c.add_argument("--out", required=True)
    c.add_argument("--workers", type=int, default=4)
    s = sub.add_parser("score")
    s.add_argument("--cache", required=True)
    s.add_argument("--weights", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--out", required=True)
    p = sub.add_parser("pick")
    p.add_argument("--scores", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"cache": cache, "score": score, "pick": pick}[a.cmd](a)


if __name__ == "__main__":
    main()

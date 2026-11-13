"""BB2 amendment 7c: platform gate by bit identity, reproducing the fit job's scorer exactly. This is the gate step of
src/RZ1/rz1_rescore.py (sha256 recorded in the amendment), copied without RZ1's input-transform patch (BB2 has none):
  1. rebuild the network: common.build_run_model(meta) and load last_trainable.pt (strict=False); the missing keys must
     be exactly the frozen parameters and there must be no unexpected key;
  2. score the fit job's evaluation manifest exactly as pn1_score.py did in the fit job: common.ImageItems at meta res,
     DataLoader batch 64 in manifest order over the whole manifest (so every row sits in the same batch as at fit
     time), TF32 on, logit without flip;
  3. compare with the tar's stored scores_eval.npz: same manifest sha256, same ids in the same order, and every float32
     logit equal (np.array_equal). gate.json: verdict "passed" or "failed" with n_differ, max |delta|, own-rule agreement.
  python -I bb2_gate.py --tar NET.tar --code CODE --manifest pn1_eval.csv|ab1_eval.csv --out OUTDIR [--workers 7]
SMAD_DATA must point at a data root holding that manifest and its images; HF_HOME at the pack's hf folder. Exit 0 if
passed, 3 if failed, 1 on an error."""
import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import tarfile
import time

import numpy as np


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tar", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    T = pathlib.Path(a.tar).name[:-4]
    work = out / "_net"
    with tarfile.open(a.tar) as t:
        for m in ("meta.json", "last_trainable.pt", "scores_eval.npz"):
            t.extract(f"{T}/{m}", work)
    src = work / T
    meta = json.load(open(src / "meta.json"))
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    model, _ = C.build_run_model(meta)
    trn = {n for n, p in model.named_parameters() if p.requires_grad}
    sd = torch.load(src / "last_trainable.pt", map_location="cpu", weights_only=True)
    if set(sd) != trn:
        sys.exit(f"BB2GATE FAIL: trainable keys differ ({len(set(sd) ^ trn)})")
    res = model.load_state_dict(sd, strict=False)
    frozen = set(model.state_dict()) - trn
    if res.unexpected_keys or set(res.missing_keys) != frozen:
        sys.exit(f"BB2GATE FAIL: load_state_dict missing/unexpected {len(res.missing_keys)}/{len(res.unexpected_keys)}")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev).eval()
    t0 = time.time()
    rows = C.read_manifest(a.manifest)
    dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]), batch_size=64,
                    num_workers=a.workers)
    lg = []
    with torch.no_grad():
        for x, _ in dl:
            lg += C.forward_logit(model, x.to(dev, non_blocking=True))[0].float().cpu().tolist()
    lg = np.array(lg, np.float32)
    z = np.load(src / "scores_eval.npz")
    ids = [r["id"] for r in rows]
    stored_ids = [str(i) for i in z["id"]]
    if str(z["manifest_sha256"]) != sha256(C.data_root() / "manifests" / a.manifest) or stored_ids != ids:
        sys.exit("BB2GATE FAIL: manifest rows or manifest sha256 differ from the fit job")
    ref = z["logit"].astype(np.float32)
    same = bool(np.array_equal(lg, ref))
    d = np.abs(lg.astype(np.float64) - ref.astype(np.float64))
    gate = dict(tar=pathlib.Path(a.tar).name, tar_sha256=sha256(a.tar), manifest=a.manifest, n=len(ids),
                verdict="passed" if same else "failed", n_differ=int((lg != ref).sum()), max_abs=float(d.max()),
                own_rule_agree=float(((lg > 0) == (ref > 0)).mean()), seconds=round(time.time() - t0, 1),
                device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu")
    json.dump(gate, open(out / f"gate_{T}.json", "w"), indent=1)
    shutil.rmtree(work)
    print("BB2GATE", json.dumps(gate), flush=True)
    sys.exit(0 if same else 3)


if __name__ == "__main__":
    main()

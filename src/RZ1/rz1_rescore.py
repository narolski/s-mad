"""RZ1 amendment 1: rescore AB1's kept A and Sb networks (seeds 408-412, WCSS H100) with the RZ1 scorer, on the same GPU
model and software build, so that every RZ1 read has a same-arm, same-seed refit yardstick (A0 against AB1 A, Sb0 against
AB1 Sb).
Per AB1 tar:
  1. rebuild the network: common.build_run_model(meta) (pretrained tower from the pack, LoRA structure from meta) and
     load last_trainable.pt over it (strict=False). The missing keys must be exactly the frozen parameters, and there
     must be no unexpected key. Save the full state as last.pt in a run folder with meta.json.
  2. gate (bit identity): score ab1_eval.csv exactly as pn1_score.py did in the fit job (common.ImageItems at meta res,
     DataLoader bs 64 in manifest order, TF32 on, logit without flip). Compare with the tar's stored scores_eval.npz
     logits: gate "passed" iff every float32 logit is equal (np.array_equal, same id order). Otherwise "failed", with the
     number of differing rows, max |delta| and own-rule agreement.
  3. run rz1_score.py (unchanged, from the RZ1 overlay) on the rebuilt run: primary fixed:pil_bilinear and the 13-spec
     cross table, i.e. the outputs of an RZ1 A0 / Sb0 fit job.
  python rz1_rescore.py --tar AB1_A_s408.tar --code CODE --rz1 RZ1_SRC --train-manifest train_A.csv --out OUT --cross SPECS
SMAD_DATA must point at the RZ1 data root (as run_rz1.sh builds it)."""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
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
    ap.add_argument("--rz1", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cross", required=True)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    T = pathlib.Path(a.tar).name[:-4]
    work = out / "_net"
    with tarfile.open(a.tar) as t:
        for m in ("meta.json", "last_trainable.pt", "scores_eval.npz", "last_pt.sha256"):
            t.extract(f"{T}/{m}", work)
    src = work / T
    meta = json.load(open(src / "meta.json"))
    os.environ["RZ1_TRANSFORM"] = "fixed:pil_bilinear"
    sys.path.insert(0, a.rz1)
    import rz1_patch
    rz1_patch.apply(a.code)
    import torch
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    model, _ = C.build_run_model(meta)
    trn = {n for n, p in model.named_parameters() if p.requires_grad}
    sd = torch.load(src / "last_trainable.pt", map_location="cpu", weights_only=True)
    if set(sd) != trn:
        sys.exit(f"RZ1R FAIL: trainable keys differ ({len(set(sd) ^ trn)})")
    res = model.load_state_dict(sd, strict=False)
    frozen = set(model.state_dict()) - trn
    if res.unexpected_keys or set(res.missing_keys) != frozen:
        sys.exit(f"RZ1R FAIL: load_state_dict missing/unexpected {len(res.missing_keys)}/{len(res.unexpected_keys)}")
    run = out / "_run"
    run.mkdir(exist_ok=True)
    torch.save(model.state_dict(), run / "last.pt")
    json.dump(meta, open(run / "meta.json", "w"))
    json.dump(dict(spec="fixed:pil_bilinear", res=meta["res"], note="AB1 network rebuilt for the RZ1 rescoring"),
              open(run / "rz1_transform.json", "w"))
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev).eval()
    t0 = time.time()
    rows = C.read_manifest("ab1_eval.csv")
    if a.limit:
        rows = rows[::max(1, len(rows) // a.limit)][:a.limit]
    dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]), batch_size=64,
                    num_workers=a.workers)
    lg = []
    with torch.no_grad():
        for x, _ in dl:
            lg += C.forward_logit(model, x.to(dev, non_blocking=True))[0].float().cpu().tolist()
    lg = np.array(lg, np.float32)
    z = np.load(src / "scores_eval.npz")
    ids = [r["id"] for r in rows]
    st = dict(zip([str(i) for i in z["id"]], z["logit"].astype(np.float32)))
    ref = np.array([st[i] for i in ids], np.float32)
    same = bool(np.array_equal(lg, ref))
    d = np.abs(lg.astype(np.float64) - ref.astype(np.float64))
    gate = dict(tar=pathlib.Path(a.tar).name, tar_sha256=sha256(a.tar), n=len(ids), verdict="passed" if same else "failed",
                n_differ=int((lg != ref).sum()), max_abs=float(d.max()), p99_abs=float(np.percentile(d, 99)),
                own_rule_agree=float(((lg > 0) == (ref > 0)).mean()), seconds=round(time.time() - t0, 1),
                device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", limit=a.limit)
    json.dump(gate, open(out / "gate.json", "w"), indent=1)
    np.savez(out / "gate_scores.npz", id=np.array(ids), logit=lg)
    print("RZ1R GATE", json.dumps(gate), flush=True)
    r = subprocess.run([sys.executable, str(pathlib.Path(a.rz1) / "rz1_score.py"), "--run", str(run), "--code", a.code,
                        "--primary", "fixed:pil_bilinear", "--cross", a.cross, "--out", str(out),
                        "--workers", str(a.workers), "--limit", str(a.limit)])
    if r.returncode:
        sys.exit(f"RZ1R FAIL: rz1_score rc {r.returncode}")
    (out / "last_pt.sha256").write_text((src / "last_pt.sha256").read_text())   # AB1's own hash of its last.pt
    import shutil
    shutil.copy2(src / "meta.json", out / "meta.json")
    shutil.rmtree(work)
    shutil.rmtree(run)
    print("RZ1R_NET_DONE", T, gate["verdict"], flush=True)


if __name__ == "__main__":
    main()

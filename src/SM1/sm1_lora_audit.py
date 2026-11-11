"""SM1 amendment A12 item 10 (H-new-5): score the Part 2 audit set with a finished LoRA fit, scoring only.

The network is rebuilt exactly as AD4's scorer does (common.build_run_model(meta), the frozen CLIP tower from the
AD4 pack's HF cache), then the fit's saved trainable parameters (ad4eval/last_trainable.pt, written by ad4_score.py
from the fit's last.pt) are loaded; every other parameter must be frozen and untouched by training (checked: the
loaded keys = the trainable parameters, nothing unexpected). Scoring core = ad4_score.py (common.ImageItems at meta
res, sigmoid of forward_logit, TTA = mean with the h-flip; no-TTA kept). Reproduction check before the audit: the
first 256 rows of the fit's own AD4 evaluation scores are rescored and must match the stored scores_eval.npz within
2e-3 (TF32 on both sides), else the task stops.

  python sm1_lora_audit.py --fit FIT_DIR --code CODE_DIR --manifest sm1_audit_eval.csv --out OUT_DIR
-> OUT_DIR/scores_audit.npz (id, score, score_noTTA), OUT_DIR/check.json
"""
import argparse
import hashlib
import json
import pathlib
import sys
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
    ap.add_argument("--fit", required=True, help="extracted result folder SM1L_<arm>_s<seed> / SM1B_...")
    ap.add_argument("--code", required=True)
    ap.add_argument("--manifest", default="sm1_audit_eval.csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--ncheck", type=int, default=256)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    fit = pathlib.Path(a.fit)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = json.load(open(fit / "meta.json"))
    model, _ = C.build_run_model(meta)
    trn = {n for n, p in model.named_parameters() if p.requires_grad}
    sd = torch.load(fit / "ad4eval/last_trainable.pt", map_location="cpu", weights_only=True)
    assert set(sd) == trn, (sorted(set(sd) ^ trn)[:5])
    res = model.load_state_dict(sd, strict=False)
    assert not res.unexpected_keys and not (set(trn) & set(res.missing_keys))
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev).eval()

    def score(rows):
        dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]),
                        batch_size=a.bs, num_workers=a.workers)
        s_tta, s_one = [], []
        with torch.no_grad():
            for x, _ in dl:
                x = x.to(dev, non_blocking=True)
                p0 = torch.sigmoid(C.forward_logit(model, x)[0].float())
                p1 = torch.sigmoid(C.forward_logit(model, torch.flip(x, dims=[3]))[0].float())
                s_one += p0.cpu().tolist()
                s_tta += ((p0 + p1) / 2).cpu().tolist()
        return np.array(s_tta, np.float32), np.array(s_one, np.float32)

    t0 = time.time()
    ev = C.read_manifest("ad4_eval.csv")[:a.ncheck]
    st = np.load(fit / "ad4eval/scores_eval.npz", allow_pickle=False)
    assert [str(i) for i in st["id"][:a.ncheck]] == [r["id"] for r in ev]
    c_tta, c_one = score(ev)
    dmax = float(max(np.abs(c_one - st["score_noTTA"][:a.ncheck]).max(), np.abs(c_tta - st["score"][:a.ncheck]).max()))
    chk = dict(fit=fit.name, n_check=len(ev), max_abs_score_diff=dmax, passed=bool(dmax <= 2e-3),
               n_trainable_tensors=len(sd), last_trainable_sha256=sha256(fit / "ad4eval/last_trainable.pt"),
               steps=meta.get("steps"), arch=meta.get("arch"), seed=meta.get("seed"))
    json.dump(chk, open(out / "check.json", "w"), indent=1)
    print("SM1A check", json.dumps(chk), flush=True)
    if not chk["passed"]:
        sys.exit("reproduction check failed")
    rows = C.read_manifest(a.manifest)
    s_tta, s_one = score(rows)
    np.savez(out / "scores_audit.npz", id=np.array([r["id"] for r in rows]), score=s_tta, score_noTTA=s_one,
             manifest_sha256=sha256(C.data_root() / "manifests" / a.manifest))
    chk.update(n_audit=len(rows), seconds=round(time.time() - t0, 1))
    json.dump(chk, open(out / "check.json", "w"), indent=1)
    print("SM1A_DONE", json.dumps(chk), flush=True)


if __name__ == "__main__":
    main()

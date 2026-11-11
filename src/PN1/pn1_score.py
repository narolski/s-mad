"""PN1 scorer (tier 1): one train.py run (meta.json + last.pt) on the PN1 evaluation manifest and on the unique rows of
its training manifest. The scoring core is the morph-free networks scorer's (src/AD4/ad4_score.py, itself score.py's
core: common.ImageItems at meta res, bilinear resize of the whole frame, sigmoid of the logit; flip average stored
beside). The PN1 reads use the logit without flip averaging (prereg section 4).

  python pn1_score.py --run RUN_DIR --code CODE_DIR --eval-manifest pn1_eval.csv --train-manifest train.csv \
      --out OUT_DIR [--workers 7] [--bs 64] [--limit 8]
SMAD_DATA must point at the data root. Writes OUT_DIR/scores_eval.npz (id, logit, score_noTTA, score_TTA),
OUT_DIR/scores_train.npz (path, logit, label), OUT_DIR/last_trainable.pt (LoRA and head), last_pt.sha256, info.json.
"""
import argparse
import hashlib
import json
import os
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
    ap.add_argument("--run", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--eval-manifest", default="pn1_eval.csv")
    ap.add_argument("--train-manifest", default="train.csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    run = pathlib.Path(a.run)
    meta = json.load(open(run / "meta.json"))
    model, _ = C.build_run_model(meta)
    ck = run / "last.pt"
    sd = torch.load(ck, map_location="cpu", weights_only=True)
    model.load_state_dict(sd)
    trn = {n for n, p in model.named_parameters() if p.requires_grad}
    torch.save({k: v for k, v in sd.items() if k in trn}, out / "last_trainable.pt")
    (out / "last_pt.sha256").write_text(f"{sha256(ck)}  last.pt\n")
    model.to(dev).eval()

    def score(rows, tta):
        dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]),
                        batch_size=a.bs, num_workers=a.workers)
        lg, s_tta = [], []
        with torch.no_grad():
            for x, _ in dl:
                x = x.to(dev, non_blocking=True)
                l0 = C.forward_logit(model, x)[0].float()
                lg += l0.cpu().tolist()
                if tta:
                    l1 = C.forward_logit(model, torch.flip(x, dims=[3]))[0].float()
                    s_tta += ((torch.sigmoid(l0) + torch.sigmoid(l1)) / 2).cpu().tolist()
        return np.array(lg, np.float32), np.array(s_tta, np.float32)

    def take(rows):
        return rows if not a.limit else rows[::max(1, len(rows) // a.limit)][:a.limit]

    t0 = time.time()
    ev = take(C.read_manifest(a.eval_manifest))
    lg, s_tta = score(ev, True)
    np.savez(out / "scores_eval.npz", id=np.array([r["id"] for r in ev]), logit=lg,
             score_noTTA=1 / (1 + np.exp(-lg.astype(np.float64))), score_TTA=s_tta,
             manifest_sha256=sha256(C.data_root() / "manifests" / a.eval_manifest))
    t1 = time.time()
    seen, tr = set(), []
    for r in C.read_manifest(a.train_manifest):
        if r["path"] not in seen:
            seen.add(r["path"])
            tr.append(r)
    tr = take(tr)
    lt, _ = score(tr, False)
    np.savez(out / "scores_train.npz", path=np.array([r["path"] for r in tr]), logit=lt,
             label=np.array([int(r["label"]) for r in tr]), kind=np.array([r.get("kind", "") for r in tr]),
             manifest_sha256=sha256(C.data_root() / "manifests" / a.train_manifest))
    y = np.array([int(r["label"]) for r in tr])
    info = dict(torch=torch.__version__, device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu",
                host=os.uname().nodename, run=str(run), seed=meta["seed"], steps=meta["steps"],
                train_hours=meta.get("train_hours"), last_pt_sha256=sha256(ck), n_eval=len(ev), n_train_unique=len(tr),
                train_acc_rule0=float(((lt > 0).astype(int) == y).mean()), eval_seconds=round(t1 - t0, 1),
                train_seconds=round(time.time() - t1, 1), limit=a.limit,
                common_py_sha256=sha256(pathlib.Path(a.code) / "smadcvpr" / "common.py"))
    json.dump(info, open(out / "info.json", "w"), indent=1)
    print("PN1_SCORE_DONE", json.dumps({"n_eval": len(ev), "n_train": len(tr), "s": round(time.time() - t0)}), flush=True)


if __name__ == "__main__":
    main()

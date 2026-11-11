"""AD4 scorer: one network (a train.py run directory, or the zero-step network of a recipe) on the AD4 evaluation
manifest and on its own training manifest. The scoring core is score.py's (smadcvpr/score.py main(): common.ImageItems
at meta res, bilinear resize, TTA = mean of sigmoid(original, h-flip)); nothing else is changed. score.py itself is not
called because its A12 locks refuse non-registered manifests.

  python ad4_score.py --run RUN_DIR --code CODE_DIR --eval-manifest ad4_eval.csv --train-manifest train.csv \
      --out OUT_DIR [--workers 7] [--bs 64] [--limit 8]
  python ad4_score.py --zero-step --recipe m3|m3l --seed 401 --code CODE_DIR ... (no RUN_DIR: the network train.py
      holds at step 0 for that seed: seeds set as train.py line 618, then build_model + apply_lora as train.py)

SMAD_DATA must point at the data root holding manifests/<eval> and manifests/<train> and the image paths.
Writes OUT_DIR/scores_eval.npz, OUT_DIR/scores_train.npz (no TTA, the training labels and the true labels),
OUT_DIR/metrics.json (per cell: n_morph, n_bona, signed AUC, EER; training accuracy), and with --run
OUT_DIR/last_trainable.pt (only the parameters train.py trained: LoRA and head) plus OUT_DIR/last_pt.sha256.
--limit N scores N rows spread over each manifest (smoke only; metrics are then meaningless and flagged).
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import random
import sys
import time

import numpy as np

RECIPES = {   # the A12BR R rows (plans/A12/A12_BR_T1.tsv M3, A12_BR_T2.tsv M3L): only what build_run_model reads
    "m3": dict(arch="a12_clip_vitb16_madation", res=224, drop_path=0.0, ft="lora", lora_r=2, lora_targets="qv",
               lora_alpha=4.0, lora_dropout=0.4, lora_rs=True, lora_train_norms=False),
    "m3l": dict(arch="a12_clip_vitl14_madation", res=224, drop_path=0.0, ft="lora", lora_r=2, lora_targets="qv",
                lora_alpha=4.0, lora_dropout=0.4, lora_rs=True, lora_train_norms=False),
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def auc(s, y):
    """Signed AUC, morph (y = 1) positive, higher score = more morph; ties count one half (average ranks)."""
    s, y = np.asarray(s, float), np.asarray(y, int)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    if n1 == 0 or n0 == 0:
        return None
    o = np.argsort(s, kind="mergesort")
    r = np.empty(len(s), float)
    ss = s[o]
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def cells(rows):
    """{cell name: (morph row idx, bona row idx)}. native: family F (label 1, variant orig) vs the set's bona fide
    (label 0, variant orig); e7: F orig vs the set's resmatch photos of family F (label 0, variant resmatch)."""
    out = {}
    sets = sorted({r["set"] for r in rows})
    for st in sets:
        rs = [(i, r) for i, r in enumerate(rows) if r["set"] == st]
        bona = [i for i, r in rs if r["label"] == "0" and r["variant"] == "orig"]
        for fam in sorted({r["family"] for _, r in rs if r["label"] == "1"}):
            m = [i for i, r in rs if r["label"] == "1" and r["family"] == fam and r["variant"] == "orig"]
            e7 = [i for i, r in rs if r["label"] == "0" and r["family"] == fam and r["variant"] == "resmatch"]
            out[f"{st}/{fam}/native"] = (m, bona)
            if e7:
                out[f"{st}/{fam}/e7"] = (m, e7)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None)
    ap.add_argument("--zero-step", action="store_true")
    ap.add_argument("--recipe", choices=sorted(RECIPES), default=None)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--code", required=True, help="directory holding smadcvpr/ (common.py) and morphmamba/")
    ap.add_argument("--eval-manifest", default="ad4_eval.csv")
    ap.add_argument("--train-manifest", default="train.csv")
    ap.add_argument("--true-manifest", default="train_i3.csv", help="the unpermuted i3 manifest (true labels)")
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
    info = {"torch": torch.__version__, "device": torch.cuda.get_device_name(0) if dev == "cuda" else "cpu",
            "smad_data": str(C.data_root()), "limit": a.limit, "host": os.uname().nodename,
            "common_py_sha256": sha256(pathlib.Path(a.code) / "smadcvpr" / "common.py")}
    if a.zero_step:
        if a.run or a.recipe is None or a.seed is None:
            ap.error("--zero-step needs --recipe and --seed and no --run")
        meta = dict(RECIPES[a.recipe], seed=a.seed, steps=0)
        random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed); torch.cuda.manual_seed_all(a.seed)
        model, _ = C.build_run_model(meta)          # build_model + apply_lora, the order train.py uses
        info.update(network="zero-step", recipe=a.recipe, seed=a.seed)
    else:
        if not a.run:
            ap.error("--run or --zero-step")
        run = pathlib.Path(a.run)
        meta = json.load(open(run / "meta.json"))
        model, _ = C.build_run_model(meta)
        ck = run / "last.pt"
        sd = torch.load(ck, map_location="cpu", weights_only=True)
        model.load_state_dict(sd)
        trn = {n for n, p in model.named_parameters() if p.requires_grad}
        keep = {k: v for k, v in sd.items() if k in trn}
        torch.save(keep, out / "last_trainable.pt")
        (out / "last_pt.sha256").write_text(f"{sha256(ck)}  last.pt\n")
        info.update(network="trained", run=str(run), seed=meta["seed"], steps=meta["steps"],
                    train_hours=meta.get("train_hours"), last_pt_sha256=sha256(ck), n_trainable_tensors=len(keep))
    info["meta_core"] = {k: meta.get(k) for k in ("arch", "res", "ft", "lora_r", "lora_targets", "lora_alpha",
                                                   "lora_dropout", "lora_rs", "seed", "steps")}
    model.to(dev).eval()

    def score(rows, tta):
        dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]),
                        batch_size=a.bs, num_workers=a.workers)
        s_tta, s_one = [], []
        with torch.no_grad():
            for x, _ in dl:
                x = x.to(dev, non_blocking=True)
                p0 = torch.sigmoid(C.forward_logit(model, x)[0].float())
                s_one += p0.cpu().tolist()
                if tta:
                    p1 = torch.sigmoid(C.forward_logit(model, torch.flip(x, dims=[3]))[0].float())
                    s_tta += ((p0 + p1) / 2).cpu().tolist()
        return np.array(s_tta, np.float32), np.array(s_one, np.float32)

    def take(rows):
        if not a.limit:
            return rows
        return rows[::max(1, len(rows) // a.limit)][:a.limit]

    t0 = time.time()
    ev = take(C.read_manifest(a.eval_manifest))
    msha = sha256(C.data_root() / "manifests" / a.eval_manifest)
    s_tta, s_one = score(ev, True)
    np.savez(out / "scores_eval.npz", id=np.array([r["id"] for r in ev]), score=s_tta, score_noTTA=s_one,
             manifest_sha256=msha)
    t1 = time.time()
    met = {}
    for name, (m, b) in cells(ev).items():
        idx = m + b
        y = [1] * len(m) + [0] * len(b)
        sc = s_tta[idx]
        met[name] = {"n_morph": len(m), "n_bona": len(b), "auc": auc(sc, y),
                     "eer": float(C.eer(sc.tolist(), y)) if m and b else None}
    tr = take(C.read_manifest(a.train_manifest))
    true = {r["path"]: r["label"] for r in C.read_manifest(a.true_manifest)}
    _, tr_one = score(tr, False)
    y_tr = np.array([int(r["label"]) for r in tr])
    y_true = np.array([int(true[r["path"]]) for r in tr])
    np.savez(out / "scores_train.npz", path=np.array([r["path"] for r in tr]), score_noTTA=tr_one,
             label_train=y_tr, label_true=y_true,
             manifest_sha256=sha256(C.data_root() / "manifests" / a.train_manifest))
    pred = (tr_one >= 0.5).astype(int)
    trainacc = {"n": int(len(tr)), "acc_vs_training_labels": float((pred == y_tr).mean()),
                "acc_vs_true_labels": float((pred == y_true).mean()),
                "auc_vs_training_labels": auc(tr_one, y_tr), "auc_vs_true_labels": auc(tr_one, y_true),
                "frac_labels_permuted": float((y_tr != y_true).mean())}
    info.update(eval_manifest=a.eval_manifest, eval_manifest_sha256=msha, n_eval=len(ev),
                eval_seconds=round(t1 - t0, 1), train_score_seconds=round(time.time() - t1, 1))
    json.dump({"info": info, "cells": met, "train": trainacc}, open(out / "metrics.json", "w"), indent=1)
    print("AD4_SCORE_DONE", json.dumps({"n_eval": len(ev), "n_train": len(tr), "seconds": round(time.time() - t0)}),
          flush=True)


if __name__ == "__main__":
    main()

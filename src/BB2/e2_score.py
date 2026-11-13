"""BB2 amendment 5 (E2): zero-LoRA ablation scoring and frozen DINOv3 features. Runs on a WCSS H100 inside
wcss/bb2_e2.sbatch, on the FS1 pack with the BB2 overlay (CLIP and DINOv3 entries both present; train.py/common.py
unchanged). TF32 on for matmul and cuDNN (as pn1_score.py in the fits). Logit without flip.
For each result tar (meta.json + last_trainable.pt):
  - CLIP nets only: the full network (LoRA as trained) on the platform-gate rows (fam af0 + ffhq of pn1_eval.csv) ->
    E2_<T>_gate.npz (the reader compares them with the fit's stored A100 logits by C2P.2's thresholds);
  - every net: the same network with every LoRA B matrix set to zero (head on the frozen tower = the base features)
    on the unique rows of its own training manifest -> E2_<T>_train0.npz (path, logit, kind) and on the whole FS1
    evaluation manifest -> E2_<T>_eval0.npz (id, logit).
Once: the frozen DINOv3 feature (CLS after the final norm, L2-normalised) of the unique rows of train_Sb.csv ->
E2_dinov3_feat_trainSb.npz (path, kind, id, feat) for the linear probe (read on the DGX CPU).
  python -I e2_score.py --code CODE --out OUT --tars T1.tar T2.tar ... [--workers 7] [--limit 0]
SMAD_DATA must point at the data root (manifests/, train/, eval/) and HF_HOME at the pack's hf folder."""
import argparse
import csv
import json
import pathlib
import sys
import tarfile

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tars", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    work = out / "_nets"
    work.mkdir(exist_ok=True)

    def take(rows):
        return rows if not a.limit else rows[::max(1, len(rows) // a.limit)][:a.limit]

    def run(model, rows, res, feat=False):
        dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], res), batch_size=64, num_workers=a.workers)
        lg, ft = [], []
        with torch.no_grad():
            for x, _ in dl:
                x = x.to(dev, non_blocking=True)
                if feat:
                    ft.append(F.normalize(model.net((x - model.mean) / model.std), dim=-1).float().cpu().numpy())
                else:
                    lg += C.forward_logit(model, x)[0].float().cpu().tolist()
        return np.concatenate(ft) if feat else np.array(lg, np.float32)

    def uniq(rows):
        seen, u = set(), []
        for r in rows:
            if r["path"] not in seen:
                seen.add(r["path"])
                u.append(r)
        return u

    ev = take(C.read_manifest("pn1_eval.csv"))
    gate_rows = take([r for r in C.read_manifest("pn1_eval.csv") if r["fam"] in ("af0", "ffhq")])
    log = {}
    feat_done = False
    for tp in a.tars:
        tp = pathlib.Path(tp)
        T = tp.name[:-4]
        with tarfile.open(tp) as t:
            for m in ("meta.json", "last_trainable.pt"):
                t.extract(f"{T}/{m}", work)
        d = work / T
        meta = json.load(open(d / "meta.json"))
        arm = T.split("_")[1]
        model, _ = C.build_run_model(meta)
        tr = torch.load(d / "last_trainable.pt", map_location="cpu", weights_only=True)
        names = {n for n, p in model.named_parameters() if p.requires_grad}
        assert set(tr) == names, (T, len(tr), len(names))
        missing, unexpected = model.load_state_dict(tr, strict=False)
        assert not unexpected
        model.to(dev).eval()
        clip = meta["arch"].startswith("a12_clip")
        if clip:
            g = run(model, gate_rows, meta["res"])
            np.savez(out / f"E2_{T}_gate.npz", id=np.array([r["id"] for r in gate_rows]), logit=g)
        nb = 0
        with torch.no_grad():
            for n, p in model.named_parameters():
                if ".B_" in n:
                    p.zero_()
                    nb += 1
        trows = take(uniq(C.read_manifest(f"train_{arm}.csv")))
        lt = run(model, trows, meta["res"])
        np.savez(out / f"E2_{T}_train0.npz", path=np.array([r["path"] for r in trows]), logit=lt,
                 kind=np.array([r.get("kind", "") for r in trows]), label=np.array([int(r["label"]) for r in trows]))
        le = run(model, ev, meta["res"])
        np.savez(out / f"E2_{T}_eval0.npz", id=np.array([r["id"] for r in ev]), logit=le)
        log[T] = dict(arch=meta["arch"], b_zeroed=nb, n_train=len(trows), n_eval=len(ev), finite=bool(np.isfinite(lt).all() and np.isfinite(le).all()))
        if not clip and not feat_done:
            srows = take(uniq(C.read_manifest("train_Sb.csv")))
            f = run(model, srows, meta["res"], feat=True)
            np.savez(out / "E2_dinov3_feat_trainSb.npz", path=np.array([r["path"] for r in srows]),
                     kind=np.array([r.get("kind", "") for r in srows]), id=np.array([r["id"] for r in srows]), feat=f.astype(np.float32))
            feat_done = True
        print("E2_NET_DONE", T, json.dumps(log[T]), flush=True)
        del model
        if dev == "cuda":
            torch.cuda.empty_cache()
    json.dump(dict(nets=log, torch=torch.__version__, device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu"), open(out / "e2_info.json", "w"), indent=1)
    print("E2_DONE", len(log), flush=True)


if __name__ == "__main__":
    main()

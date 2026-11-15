"""RZ1 scorer, run inside each fit job right after training (same GPU, same software build). The scoring core is
pn1_score.py's (common.ImageItems at meta res, TF32 on, logit without flip as the read value), with the input
transform of rz1_patch:

  scores_eval.npz   the AB1 border evaluation manifest (ab1x_eval.csv: ab1_eval.csv's 21,277 rows + 3,582 border rows),
                    primary transform; same fields as pn1_score.py (id, logit, score_noTTA, score_TTA, manifest_sha256)
  scores_train.npz  unique rows of the training manifest, primary transform (path, logit, label, kind, manifest_sha256)
  scores_tt1.npz    TT1 unseen genuine sources with their border and geometry references (tt1_score.csv), primary
  scores_meds.npz   NIST MEDS (meds_score.csv), primary; ids only, no image or identifier leaves the job except the id
  scores_cross.npz  the cross-table rows (rz1_cross.csv) under every spec of --cross (logit[k, i]); empty if no --cross
  python rz1_score.py --run RUN --code CODE --primary fixed:pil_bilinear --cross fixed:pil_bilinear,... --out OUT
SMAD_DATA must point at the data root (manifests/ holds ab1x_eval.csv, tt1_score.csv, meds_score.csv, rz1_cross.csv)."""
import argparse
import hashlib
import json
import os
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rz1_patch  # noqa: E402


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
    ap.add_argument("--out", required=True)
    ap.add_argument("--primary", required=True)
    ap.add_argument("--cross", default="")
    ap.add_argument("--eval-manifest", default="ab1x_eval.csv")
    ap.add_argument("--train-manifest", default="train.csv")
    ap.add_argument("--tt1-manifest", default="tt1_score.csv")
    ap.add_argument("--meds-manifest", default="meds_score.csv")
    ap.add_argument("--cross-manifest", default="rz1_cross.csv")
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.environ["RZ1_TRANSFORM"] = a.primary
    rz1_patch.apply(a.code)
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
    mdir = C.data_root() / "manifests"

    def score(rows, tta, spec):
        rz1_patch.set_spec(spec)
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

    T = {}
    t0 = time.time()
    ev = take(C.read_manifest(a.eval_manifest))
    lg, s_tta = score(ev, True, a.primary)
    np.savez(out / "scores_eval.npz", id=np.array([r["id"] for r in ev]), logit=lg,
             score_noTTA=1 / (1 + np.exp(-lg.astype(np.float64))), score_TTA=s_tta,
             manifest_sha256=sha256(mdir / a.eval_manifest), spec=a.primary)
    T["eval"] = round(time.time() - t0, 1)
    seen, tr = set(), []
    for r in C.read_manifest(a.train_manifest):
        if r["path"] not in seen:
            seen.add(r["path"])
            tr.append(r)
    tr = take(tr)
    lt, _ = score(tr, False, a.primary)
    np.savez(out / "scores_train.npz", path=np.array([r["path"] for r in tr]), logit=lt,
             label=np.array([int(r["label"]) for r in tr]), kind=np.array([r.get("kind", "") for r in tr]),
             manifest_sha256=sha256(mdir / a.train_manifest), spec=a.primary)
    T["train"] = round(time.time() - t0, 1)
    for tag, man in (("tt1", a.tt1_manifest), ("meds", a.meds_manifest)):
        rows = take(C.read_manifest(man))
        l, _ = score(rows, False, a.primary)
        np.savez(out / f"scores_{tag}.npz", id=np.array([r["id"] for r in rows]), logit=l,
                 manifest_sha256=sha256(mdir / man), spec=a.primary)
        T[tag] = round(time.time() - t0, 1)
    specs = [s for s in a.cross.split(",") if s]
    cr = take(C.read_manifest(a.cross_manifest)) if specs else []
    L = np.stack([score(cr, False, s)[0] for s in specs]) if specs else np.zeros((0, 0), np.float32)
    np.savez(out / "scores_cross.npz", id=np.array([r["id"] for r in cr]), logit=L, specs=np.array(specs),
             manifest_sha256=sha256(mdir / a.cross_manifest) if specs else "")
    T["cross"] = round(time.time() - t0, 1)
    y = np.array([int(r["label"]) for r in tr])
    info = dict(torch=torch.__version__, device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu",
                host=os.uname().nodename, run=str(run), seed=meta["seed"], steps=meta["steps"], res=meta["res"],
                primary=a.primary, cross=specs, train_hours=meta.get("train_hours"), last_pt_sha256=sha256(ck),
                n_eval=len(ev), n_train_unique=len(tr), n_cross=len(cr),
                train_acc_rule0=float(((lt > 0).astype(int) == y).mean()), seconds=T, limit=a.limit,
                common_py_sha256=sha256(pathlib.Path(a.code) / "smadcvpr" / "common.py"),
                rz1_kernels_sha256=sha256(pathlib.Path(__file__).resolve().parent / "rz1_kernels.py"))
    json.dump(info, open(out / "info.json", "w"), indent=1)
    print("RZ1_SCORE_DONE", json.dumps(info["seconds"]), flush=True)


if __name__ == "__main__":
    main()

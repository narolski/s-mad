"""PD1 DiffAE family: frozen features, one model per process (the shared GB10 refuses two at load).

Images through the existing loader smadcvpr/common.ImageItems(res=224) (PIL bilinear, the only resize). Models built by
FZ1's build() (src/FZ1/fz1_feats.py, imported unchanged): CLIP ViT-L/14 OpenAI with CLIP-native input, DINOv3 ViT-L/16.
Per image: clip_pool (768, projected embedding = model(x)), clip_patch (1024, mean of patch tokens after the final norm),
dino_pool (1024, pooled pre-logits), dino_patch (1024, mean of patch tokens). fp32, TF32 off. No gradients.

  pd1_feats.py --model clip|dino --sets tr,f256,... [--limit 8] [--tag smoke] [--bs 16] [--workers 3]
  pd1_feats.py --model clip|dino --check-fz1   my pooled vectors vs FZ1's a43 caches on 8 A43 frames per arm

Writes /mnt/t7/smad_next/PD1/diffae/feat/<model>/<set>[_<tag>].npz with id, pool, patch
Run: nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_feats.py ...
"""
import argparse, csv, json, os, pathlib, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import numpy as np
import torch
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
import fz1_feats as FZ  # noqa: E402  (build, prep: unchanged)
from common import ImageItems  # noqa: E402

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/diffae")
ITEMS = BIG / "lists/items.csv"


def load_items():
    return list(csv.DictReader(open(ITEMS)))


@torch.no_grad()
def run(models, paths, bs, workers, dev):
    ds = ImageItems([(p, 0) for p in paths], res=224, root="/")
    dl = torch.utils.data.DataLoader(ds, batch_size=bs, shuffle=False, num_workers=workers, pin_memory=True)
    out = {k: [] for k in ("pool", "patch")}
    t0 = time.time()
    for k, (x, _) in enumerate(dl):
        x = x.to(dev, non_blocking=True)
        for name, (m, norm) in models.items():
            tok = m.forward_features(FZ.prep(x, norm))
            pooled = m.forward_head(tok, pre_logits=(name == "dino"))
            patch = tok[:, m.num_prefix_tokens:].mean(1)
            out["pool"].append(pooled.float().cpu())
            out["patch"].append(patch.float().cpu())
        if k % 20 == 0:
            print(f"  batch {k}/{len(dl)} {time.time() - t0:.0f}s", flush=True)
    return {k: torch.cat(v).numpy().astype(np.float32) for k, v in out.items()}, time.time() - t0


def build_models(name, dev):
    m, n, i = FZ.build({"clip": "clip_native", "dino": "dinov3"}[name])
    return {name: (m.to(dev), n)}, {name: i}


def check_fz1(models, name, dev):
    """Equality of my pooled vectors with FZ1's caches (clip_native, dinov3) on 8 A43 frames per arm."""
    it = [r for r in load_items() if r["set"] == "fr512"]
    by = {}
    for r in it:
        by.setdefault(r["arm"], []).append(r)
    sel = [r for a in sorted(by) for r in by[a][:8]]
    feats, _ = run(models, [r["path"] for r in sel], 16, 2, dev)
    fz = {"clip": "clip_native", "dino": "dinov3"}[name]
    z = np.load(f"/mnt/t7/smad_next/FZ1/feats/{fz}/a43.npz", allow_pickle=False)
    pos = {i: k for k, i in enumerate(z["id"].tolist())}
    ref = z["feat"][[pos[r["id"].split("|", 1)[1]] for r in sel]]
    d = np.abs(ref - feats["pool"])
    res = dict(model=name, fz1_cache=fz, n=len(sel), max_abs=float(d.max()), mean_abs=float(d.mean()),
               ref_absmean=float(np.abs(ref).mean()), passes=bool(d.max() <= 1e-4))
    print(json.dumps(res, indent=1))
    json.dump(res, open(BIG / f"feat/check_vs_fz1_{name}.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--model", required=True, choices=("clip", "dino"))
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--check-fz1", action="store_true")
    a = ap.parse_args()
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    dev = "cuda"
    models, info = build_models(a.model, dev)
    (BIG / "feat" / a.model).mkdir(parents=True, exist_ok=True)
    if a.check_fz1:
        return check_fz1(models, a.model, dev)
    items = load_items()
    for s in a.sets.split(","):
        out = BIG / "feat" / a.model / (f"{s}_{a.tag}.npz" if a.tag else f"{s}.npz")
        if out.exists() and not a.tag:
            print("exists, skipped:", out)
            continue
        rows = [r for r in items if r["set"] == s]
        if a.limit:
            rows = rows[:a.limit]
        feats, dt = run(models, [r["path"] for r in rows], a.bs, a.workers, dev)
        print(f"{s}: {len(rows)} images in {dt:.0f}s; max GPU mem {torch.cuda.max_memory_allocated() / 2**30:.2f} GB", flush=True)
        np.savez(out, id=np.array([r["id"] for r in rows]), **feats,
                 meta=json.dumps(dict(info=info, model=a.model, set=s, n=len(rows), seconds=dt, tf32=False, loader="ImageItems(res=224)")))
        print("wrote", out, flush=True)


if __name__ == "__main__":
    main()

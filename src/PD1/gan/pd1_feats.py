"""Signal isolation by paired differences (PD1), GAN family: frozen features.

Images through the existing loader smadcvpr/common.ImageItems(res=224) (its PIL bilinear resize is the only resize).
Backbones (weights from the local HF cache, offline, weights_only / safetensors):
  clip  : OpenAI CLIP ViT-L/14, timm vit_large_patch14_clip_quickgelu_224 loaded as in FZ1 (src/FZ1/fz1_feats.py),
          CLIP RGB mean/std. pool = 768-d projected embedding; patch = mean of the 256 patch tokens after the final norm.
  dinov3: timm vit_large_patch16_dinov3.lvd1689m, its mean/std. pool = timm pooled pre-logits; patch = mean of the
          patch tokens after the final norm (CLS and register tokens excluded).
Writes /mnt/t7/smad_next/PD1/gan/feats/<backbone>/<set>.npz (id, pool, patch float32; meta json).

  pd1_feats.py --backbone clip|dinov3 --sets G,Hr,Ha,S,Fm,Fe,Bm,Be [--smoke] [--bs 32]
Run: nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/gan/pd1_feats.py ...
"""
import argparse, csv, json, os, pathlib, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import numpy as np
import torch
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
from common import ImageItems  # noqa: E402  (existing loader)

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
HUB = pathlib.Path.home() / ".cache/huggingface/hub"
CLIP_BIN = next((HUB / "models--timm--vit_large_patch14_clip_224.openai/snapshots").glob("*/pytorch_model.bin"))
DINO3 = next((HUB / "models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots").glob("*/model.safetensors"))
CLIP_MEAN, CLIP_STD = (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)


def build(backbone):
    import timm
    if backbone == "clip":
        m = timm.create_model("vit_large_patch14_clip_quickgelu_224", pretrained=False, num_classes=768, img_size=224)
        from timm.models.vision_transformer import checkpoint_filter_fn
        sd = checkpoint_filter_fn(torch.load(CLIP_BIN, map_location="cpu", weights_only=True), m)
        missing, unexpected = m.load_state_dict(sd, strict=False)
        assert not unexpected and set(missing) <= {"head.bias"}, (missing, unexpected)
        if "head.bias" in missing:
            torch.nn.init.zeros_(m.head.bias)
        norm = (CLIP_MEAN, CLIP_STD)
        info = dict(timm="vit_large_patch14_clip_quickgelu_224", weights=str(CLIP_BIN), missing=list(missing))
    elif backbone == "dinov3":
        m = timm.create_model("vit_large_patch16_dinov3.lvd1689m", pretrained=True, num_classes=0, img_size=224,
                              pretrained_cfg_overlay=dict(file=str(DINO3)))
        c = m.pretrained_cfg
        norm = (tuple(c["mean"]), tuple(c["std"]))
        info = dict(timm="vit_large_patch16_dinov3.lvd1689m", weights=str(DINO3), global_pool=str(getattr(m, "global_pool", "")))
    else:
        raise SystemExit(backbone)
    info.update(mean=norm[0], std=norm[1], num_prefix_tokens=int(m.num_prefix_tokens), timm_version=timm.__version__)
    return m.eval(), norm, info


@torch.no_grad()
def extract(model, norm, paths, bs, dev, check=False, workers=3):
    ds = ImageItems([(p, 0) for p in paths], res=224, root="/")
    dl = torch.utils.data.DataLoader(ds, batch_size=bs, shuffle=False, num_workers=workers, pin_memory=False)
    mean = torch.tensor(norm[0], device=dev).view(1, 3, 1, 1)
    std = torch.tensor(norm[1], device=dev).view(1, 3, 1, 1)
    P, Q, t0, dmax = [], [], time.time(), 0.0
    npt = model.num_prefix_tokens
    for k, (x, _) in enumerate(dl):
        x = (x.to(dev) - mean) / std
        tok = model.forward_features(x)
        pool = model.forward_head(tok)
        if check and k == 0:
            dmax = float((model(x) - pool).abs().max())
        P.append(pool.float().cpu())
        Q.append(tok[:, npt:].mean(1).float().cpu())
        if k % 20 == 0:
            print(f"  batch {k}/{len(dl)} {time.time() - t0:.0f}s", flush=True)
    return torch.cat(P).numpy(), torch.cat(Q).numpy(), time.time() - t0, dmax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--sets", required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    torch.backends.cuda.matmul.allow_tf32 = True      # as FZ1 (recorded in meta)
    torch.backends.cudnn.allow_tf32 = True
    dev = "cuda"
    items = list(csv.DictReader(open(BIG / "items.csv")))
    model, norm, info = build(a.backbone)
    model = model.to(dev)
    for s in a.sets.split(","):
        rows = [r for r in items if r["set"] == s]
        if a.smoke:
            rows = rows[:8]
        out = BIG / "feats" / a.backbone / f"{s}{'_smoke' if a.smoke else ''}.npz"
        if out.exists() and not a.smoke:
            print("exists, skipped:", out)
            continue
        pool, patch, dt, dmax = extract(model, norm, [r["path"] for r in rows], a.bs, dev, check=True, workers=a.workers)
        out.parent.mkdir(parents=True, exist_ok=True)
        meta = dict(info, set=s, n=len(rows), seconds=dt, tf32=True, check_forward_vs_head_maxabs=dmax,
                    max_gpu_mem_gb=torch.cuda.max_memory_allocated() / 2**30)
        np.savez(out, id=np.array([r["id"] for r in rows]), pool=pool.astype(np.float32), patch=patch.astype(np.float32),
                 meta=json.dumps(meta))
        print(f"{a.backbone} {s}: {pool.shape} {patch.shape} in {dt:.0f}s; fwd-vs-head {dmax:.2e}; "
              f"max GPU mem {meta['max_gpu_mem_gb']:.2f} GB -> {out}", flush=True)


if __name__ == "__main__":
    main()

"""Frozen read of the new diffusion ladder (FZ2): frozen feature extraction, runnable on the DGX (spark venv) and on
Athena (container smad_torch221_cu121_v1.sif). Registered in experiments/FZ2_frozen-read-new-diffusion-ladder/prereg.md.

  python -I fz2_feats.py --backbone clip_mad|dinov2 --weights FILE --common DIR --img-root DIR --out NPZ
                         [--list CSV] [--smoke] [--bs 64] [--workers 6]

- Images: every *.png under --img-root (sorted relative paths), or the relative paths in --list (column 'path').
- Loader: ImageItems(res=224) from the unchanged mambamorph-code/smadcvpr/common.py found in --common (PIL bilinear
  resize of the file to 224; no other image operation).
- clip_mad: timm vit_large_patch14_clip_quickgelu_224 (no download), tensors 'net.*' of the released MADation FE
  ViT-L/14 model.safetensors (bit-identical to OpenAI CLIP ViT-L/14, FZ1 check); input BGR, (x - 0.5) / 0.5; output the
  768-d projected embedding (not normalised here).
- dinov2: timm vit_large_patch14_dinov2.lvd142m, img_size 224, weights from the local safetensors (timm interpolates the
  position table); ImageNet mean / std; pooled pre-logits (CLS).
- fp32, TF32 off. Writes id (relative path), feat float32, meta json (versions, weights sha256, n, seconds).
"""
import argparse, csv, hashlib, json, os, pathlib, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np
import torch


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def build(backbone, weights):
    import timm
    if backbone == "clip_mad":
        from safetensors.torch import load_file
        m = timm.create_model("vit_large_patch14_clip_quickgelu_224", pretrained=False, num_classes=768, img_size=224)
        sd = {k[4:]: v for k, v in load_file(weights).items() if k.startswith("net.")}
        m.load_state_dict(sd, strict=True)
        norm = dict(bgr=True, mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
    elif backbone == "dinov2":
        m = timm.create_model("vit_large_patch14_dinov2.lvd142m", pretrained=True, num_classes=0, img_size=224,
                              pretrained_cfg_overlay=dict(file=weights))
        c = m.pretrained_cfg
        norm = dict(bgr=False, mean=tuple(c["mean"]), std=tuple(c["std"]))
    else:
        raise SystemExit(f"unknown backbone {backbone}")
    return m.eval(), norm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--common", required=True)
    ap.add_argument("--img-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--list", default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    sys.path.insert(0, a.common)
    from common import ImageItems  # noqa: E402  (unchanged loader)
    root = pathlib.Path(a.img_root)
    if a.list:
        rel = [r["path"] for r in csv.DictReader(open(a.list))]
    else:
        rel = sorted(str(p.relative_to(root)) for p in root.rglob("*.png"))
    if a.smoke:
        rel = rel[:8]
    assert rel, "no images"
    dev = "cuda"
    model, norm = build(a.backbone, a.weights)
    model = model.to(dev)
    mean = torch.tensor(norm["mean"], device=dev).view(1, 3, 1, 1)
    std = torch.tensor(norm["std"], device=dev).view(1, 3, 1, 1)
    ds = ImageItems([(str(root / r), 0) for r in rel], res=224, root="/")
    dl = torch.utils.data.DataLoader(ds, batch_size=a.bs, shuffle=False, num_workers=a.workers, pin_memory=True)
    out, t0 = [], time.time()
    with torch.no_grad():
        for k, (x, _) in enumerate(dl):
            x = x.to(dev, non_blocking=True)
            if norm["bgr"]:
                x = x[:, [2, 1, 0]]
            out.append(model((x - mean) / std).float().cpu())
            if k % 20 == 0:
                print(f"  batch {k}/{len(dl)} {time.time() - t0:.0f}s", flush=True)
    f = torch.cat(out).numpy().astype(np.float32)
    dt = time.time() - t0
    import timm, PIL
    meta = dict(backbone=a.backbone, weights=str(a.weights), weights_sha256=sha256(a.weights), n=len(rel), seconds=dt,
                tf32=False, torch=torch.__version__, timm=timm.__version__, numpy=np.__version__, pillow=PIL.__version__,
                python=sys.version.split()[0], common_sha256=sha256(pathlib.Path(a.common) / "common.py"),
                device=torch.cuda.get_device_name(0), img_root=str(root), norm=norm)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez(a.out, id=np.array(rel), feat=f, meta=json.dumps(meta))
    print(f"{a.backbone}: {f.shape} in {dt:.0f}s ({len(rel) / max(dt, 1e-9):.1f} img/s); wrote {a.out}", flush=True)


if __name__ == "__main__":
    main()

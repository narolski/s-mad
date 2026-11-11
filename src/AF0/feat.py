"""AF0 frozen patch-token cache.

Backbones (timm, local Hugging Face cache, offline, weights as cached; each model's own standard preprocessing from its
pretrained config via timm.data.create_transform, eval mode):
  dinov3_512 : vit_large_patch16_dinov3.lvd1689m, img_size 512 -> 32 x 32 patch tokens (5 prefix tokens dropped).
               Transform at input_size 512 (Resize 512 is the identity on our 512^2 frames; checked), ImageNet mean/std.
  clip336    : vit_large_patch14_clip_336.openai -> 24 x 24 (Resize 336 bicubic + CenterCrop 336 + OpenAI mean/std)
  clip224    : vit_large_patch14_clip_224.openai -> 16 x 16 (Resize 224 bicubic + CenterCrop 224 + OpenAI mean/std)
Tokens = forward_features output (final norm), patch tokens only, float16, (N, T, 1024) memmap.
--flip (lead's addition 2, mirror distance): the left-right flipped image (PIL FLIP_LEFT_RIGHT, lossless) is also
passed; per patch we store two L2 distances (float16, (N, T, 2)):
  [0] content-aligned : || t(i, j) - t_flip(i, n-1-j) ||   (same image content, mirrored)
  [1] position-aligned: || t(i, j) - t_flip(i, j) ||       (left half against mirrored right half)
Resumable: progress in <name>.done.

  python3 -I feat.py --backbone dinov3_512 --list OUT/lists/af0.csv --name af0 [--flip] [--limit 8] [--bs 16]
"""
import argparse
import csv
import json
import os
import pathlib
import sys
import time

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
BACKBONES = {
    "dinov3_512": dict(timm="vit_large_patch16_dinov3.lvd1689m", size=512, kw=dict(img_size=512)),
    "clip336": dict(timm="vit_large_patch14_clip_336.openai", size=336, kw={}),
    "clip224": dict(timm="vit_large_patch14_clip_224.openai", size=224, kw={}),
}


class Items:
    def __init__(self, paths, tf, flip):
        self.paths, self.tf, self.flip = paths, tf, flip

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        from PIL import Image
        im = Image.open(self.paths[i]).convert("RGB")
        assert im.size == (512, 512), (self.paths[i], im.size)
        x = self.tf(im)
        if not self.flip:
            return x, x[:0]
        return x, self.tf(im.transpose(Image.FLIP_LEFT_RIGHT))


def build(name):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import timm
    b = BACKBONES[name]
    m = timm.create_model(b["timm"], pretrained=True, **b["kw"]).eval()
    cfg = timm.data.resolve_data_config({}, model=m)
    cfg["input_size"] = (3, b["size"], b["size"])
    cfg["crop_pct"] = 1.0
    tf = timm.data.create_transform(**cfg, is_training=False)
    return m, tf, cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True, choices=list(BACKBONES))
    ap.add_argument("--list", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--flip", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    rows = list(csv.DictReader(open(a.list)))[: a.limit or None]
    ids = [r["id"] for r in rows]
    paths = [r["path"] for r in rows]
    od = OUT / "feat" / a.backbone
    od.mkdir(parents=True, exist_ok=True)
    tag = a.name + (f"_limit{a.limit}" if a.limit else "")
    model, tf, cfg = build(a.backbone)
    npt = model.num_prefix_tokens
    g = BACKBONES[a.backbone]["size"] // model.patch_embed.patch_size[0]
    T, D = g * g, model.embed_dim
    fT, fD, fM = od / f"{tag}.tokens.npy", od / f"{tag}.done", od / f"{tag}.mirror.npy"
    done = int(fD.read_text()) if fD.exists() else 0
    if done and not fT.exists():
        done = 0
    mode = "r+" if done else "w+"
    tok = np.lib.format.open_memmap(fT, mode=mode, dtype=np.float16, shape=(len(rows), T, D))
    mir = np.lib.format.open_memmap(fM, mode=mode, dtype=np.float16, shape=(len(rows), T, 2)) if a.flip else None
    np.save(od / f"{tag}.ids.npy", np.array(ids))
    json.dump(dict(backbone=a.backbone, timm=BACKBONES[a.backbone]["timm"], data_config={k: list(v) if isinstance(
        v, tuple) else v for k, v in cfg.items()}, transform=str(tf), grid=g, prefix_tokens=npt, list=a.list,
        n=len(rows), flip=a.flip), open(od / f"{tag}.meta.json", "w"), indent=1)
    if a.backbone == "dinov3_512":      # resize-to-512 must be the identity on 512^2 frames
        from PIL import Image
        im = Image.open(paths[0]).convert("RGB")
        x0 = tf(im)
        x1 = (torch.from_numpy(np.asarray(im).copy()).permute(2, 0, 1).float() / 255 -
              torch.tensor(cfg["mean"])[:, None, None]) / torch.tensor(cfg["std"])[:, None, None]
        assert float((x0 - x1).abs().max()) < 1e-5, "dinov3 transform is not the identity resize"
    dev = "cuda"
    model.to(dev)
    dl = torch.utils.data.DataLoader(Items(paths[done:], tf, a.flip), batch_size=a.bs, num_workers=a.workers)
    t0, i = time.time(), done
    perm = torch.arange(T).reshape(g, g).flip(1).reshape(-1).to(dev)     # (i, j) -> (i, n-1-j)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for x, xf in dl:
            n = len(x)
            t = model.forward_features(x.to(dev, non_blocking=True))[:, npt:].float()
            assert t.shape[1] == T
            tok[i:i + n] = t.half().cpu().numpy()
            if a.flip:
                tf_ = model.forward_features(xf.to(dev, non_blocking=True))[:, npt:].float()
                dc = (t - tf_[:, perm]).norm(dim=-1)
                dp = (t - tf_).norm(dim=-1)
                mir[i:i + n] = torch.stack([dc, dp], -1).half().cpu().numpy()
            i += n
            if (i - done) % (a.bs * 25) < a.bs:
                tok.flush()
                if a.flip:
                    mir.flush()
                fD.write_text(str(i))
                el = time.time() - t0
                print(f"{i}/{len(rows)} {(i - done) / el:.1f} img/s, max mem "
                      f"{torch.cuda.max_memory_allocated() / 2**30:.1f} GB", flush=True)
    tok.flush()
    if a.flip:
        mir.flush()
    fD.write_text(str(i))
    el = time.time() - t0
    print(f"DONE {tag}: {i} images, {T} tokens x {D}, {(i - done) / max(el, 1e-9):.1f} img/s, "
          f"max mem {torch.cuda.max_memory_allocated() / 2**30:.1f} GB", flush=True)


if __name__ == "__main__":
    main()

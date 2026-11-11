"""ID0 frozen features, one decode per image, nothing written as an image.

  glint : glintr100 unit embedding through AR1's registered route (src/AR1/fr.py, imported unchanged: prep_eval.kps
          pinned -> insightface norm_crop -> a2f_common.embed_crops('glint') pinned)
  clip  : timm vit_large_patch14_clip_224.openai, num_classes=0 (pooled, pre-projection, 1024), its own transform
  dino  : timm vit_large_patch16_dinov3.lvd1689m, num_classes=0 (pooled, 1024), its own transform (default 256)
Offline HF cache, eval mode, no grad. Output /mnt/t7/smad_next/ID0/feat/<model>.npz (keys, feat, found), written in
parts (resumable) and merged at the end.

  python3 -I feat.py [--models glint,clip,dino] [--limit 8] [--tag test] [--bs 32] [--workers 3]
"""
import argparse
import csv
import json
import os
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402

TIMM = {"clip": "vit_large_patch14_clip_224.openai", "dino": "vit_large_patch16_dinov3.lvd1689m"}


def all_items():
    out = [(r["key"], r["path"]) for r in C.rows(C.OUT / "fit.csv")]
    out += [(r["key"], r["path"]) for r in C.rows(C.OUT / "items.csv")]
    return out


class DS:
    def __init__(self, paths, tfs):
        self.paths, self.tfs = paths, tfs

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        import cv2
        import torch
        from PIL import Image
        bgr = cv2.imread(self.paths[i], cv2.IMREAD_COLOR)
        assert bgr is not None, self.paths[i]
        im = Image.fromarray(bgr[:, :, ::-1].copy())
        xs = [tf(im) for tf in self.tfs]
        return i, torch.from_numpy(bgr.copy()), xs


def collate(b):
    import torch
    idx = [x[0] for x in b]
    bgr = [x[1].numpy() for x in b]
    xs = [torch.stack([x[2][k] for x in b]) for k in range(len(b[0][2]))]
    return idx, bgr, xs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="glint,clip,dino")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--max-tier", type=int, default=3)
    ap.add_argument("--merge-only", action="store_true")
    ap.add_argument("--shard", default="0/1", help="i/n: process only chunks with (c0 / chunk) % n == i")
    ap.add_argument("--dtype", default="fp16", choices=["fp16", "bf16", "fp32"],
                    help="timm models' precision (DINOv3 overflows in fp16: every feature non-finite)")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import torch
    import timm
    torch.set_num_threads(2)
    models = a.models.split(",")
    items = all_items()
    if a.limit:
        # a few of every group
        seen, kept = {}, []
        for k, p in items:
            g = k.split("|")[0] + "|" + k.split("|")[1]
            seen[g] = seen.get(g, 0) + 1
            if seen[g] <= 1 and len(kept) < a.limit:
                kept.append((k, p))
        items = kept
    if a.models == "glint":
        # only items without an existing embedding from the same registered route (AR1 npz files, a46)
        have = set(C.existing_glint())
        items = [(k, p) for k, p in items if k not in have]
        print(f"glint subset: {len(items)} items need a new embedding", flush=True)
    items = C.ordered(items, "spark", a.max_tier)
    if a.models == "glint":
        r = [(C.glint_rank(k), i) for i, (k, _) in enumerate(items)]
        items = [items[i] for _, i in sorted(r)]
    print(f"items after tier order (max tier {a.max_tier}): {len(items)}", flush=True)
    keys = [k for k, _ in items]
    paths = [p for _, p in items]
    for p in paths:
        assert not C.forbidden(p), p
    fd = C.OUT / "feat"
    if a.merge_only:
        merge(fd, f"_{a.tag}" if a.tag else "", models, keys)
        return
    dev = "cuda"
    DT = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}[a.dtype]
    nets, tfs = {}, []
    for m in models:
        if m == "glint":
            continue
        net = timm.create_model(TIMM[m], pretrained=True, num_classes=0).eval().to(DT).to(dev)
        cfg = timm.data.resolve_data_config({}, model=net)
        nets[m] = net
        tfs.append(timm.data.create_transform(**cfg, is_training=False))
    tnames = [m for m in models if m != "glint"]
    fr = None
    if "glint" in models:
        sys.path.insert(0, str(C.AR1_SRC))
        import fr as FR  # AR1's module, unchanged
        fr = FR
    fd = C.OUT / "feat"
    fd.mkdir(parents=True, exist_ok=True)
    sfx = f"_{a.tag}" if a.tag else ""
    t0 = time.time()
    si, sn = map(int, a.shard.split("/"))
    for c0 in range(0, len(items), a.chunk):
        part = fd / f"part{sfx}_{c0:06d}.npz"
        if part.exists() or (c0 // a.chunk) % sn != si:
            continue
        sel = list(range(c0, min(c0 + a.chunk, len(items))))
        ds = DS([paths[i] for i in sel], tfs)
        dl = torch.utils.data.DataLoader(ds, batch_size=a.bs, num_workers=a.workers, collate_fn=collate)
        res = {m: np.zeros((len(sel), 512 if m == "glint" else 1024), np.float32) for m in models}
        found = np.ones(len(sel), bool)
        with torch.no_grad():
            for idx, bgr, xs in dl:
                for m, x in zip(tnames, xs):
                    res[m][idx] = nets[m](x.to(dev).to(DT)).float().cpu().numpy()
                if fr is not None:
                    e, f = fr.embed_images(bgr)
                    res["glint"][idx] = e
                    found[idx] = f
        for m in tnames:
            if not np.isfinite(res[m]).all():
                sys.exit(f"{m}: non-finite features in chunk {c0} ({a.dtype}); nothing saved")
        np.savez(part, idx=np.array(sel), found=found, **res)
        print(f"{time.strftime('%T')} part {c0} done ({len(sel)}), {time.time() - t0:.0f} s", flush=True)
    merge(fd, sfx, models, keys)
    info = dict(models={m: TIMM.get(m, "glintr100 (AR1 fr.py)") for m in models}, n=len(items),
                seconds=round(time.time() - t0, 1), torch=torch.__version__, timm=timm.__version__)
    json.dump(info, open(fd / f"feat{sfx}.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


def merge(fd, sfx, models, keys):
    """only processed rows are written (a stopped run gives a usable partial file)."""
    parts = sorted(fd.glob(f"part{sfx}_*.npz"))
    for m in models:
        F = np.zeros((len(keys), 512 if m == "glint" else 1024), np.float32)
        fo = np.ones(len(keys), bool)
        done = np.zeros(len(keys), bool)
        for p in parts:
            z = np.load(p)
            F[z["idx"]] = z[m]
            fo[z["idx"]] = z["found"]
            done[z["idx"]] = True
        np.savez(fd / f"{m}{sfx}.npz", keys=np.array(keys)[done], feat=F[done], found=fo[done])
        print(f"merged {m}: {int(done.sum())} of {len(keys)} rows", flush=True)


def _unused():
    pass


if __name__ == "__main__":
    main()

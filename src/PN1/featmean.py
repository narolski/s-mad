"""PN1 frozen features: the mean of the patch tokens of CLIP ViT-L/14 at 224 and DINOv3 ViT-L/16 at 512, for lists whose
images are not in the alpha-field probe's caches (AF0). The model build, transform and forward pass are those of
/home/narolski/smad-next/src/AF0/feat.py (imported, unchanged; sha256 4529c523...): build(name) and Items, bf16 autocast,
forward_features, prefix tokens dropped. One difference: instead of the (N, T, 1024) float16 token memmap we store the
mean over the T patch tokens of the float16-cast tokens, computed in float32, i.e. exactly what PN1 computes from the
AF0 token files (featpool.py), so new and cached features are the same statistic.
Output: /mnt/t7/smad_next/PN1/feat/<backbone>/<name>.mean.npy (N, 1024) float32, <name>.ids.npy, <name>.meta.json.

  python3 -I featmean.py --backbone clip224 --job <name>=<list.csv> [--job ...] [--limit 8]
(one process, one model load, the jobs in order; a finished job is skipped)
"""
import argparse
import csv
import importlib.util
import json
import os
import pathlib
import sys
import time

import numpy as np

AF0FEAT = pathlib.Path(os.environ.get("PN1_AF0FEAT", "/home/narolski/smad-next/src/AF0/feat.py"))   # Athena: featx copy
AF0FEAT_SHA = "4529c523456455743b241e701ed1b022008f43812a6897cfe4824a570278c84f"
OUT = pathlib.Path(os.environ.get("PN1_FEAT_OUT", "/mnt/t7/smad_next/PN1/feat"))   # Athena: featx/out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True, choices=["clip224", "dinov3_512"])
    ap.add_argument("--job", action="append", required=True, help="name=list.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    import hashlib
    assert hashlib.sha256(AF0FEAT.read_bytes()).hexdigest() == AF0FEAT_SHA, "AF0 feat.py changed"
    spec = importlib.util.spec_from_file_location("af0_feat", AF0FEAT)
    F = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(F)
    import torch
    model, tf, cfg = None, None, None
    for job in a.job:
        name, lst = job.split("=", 1)
        rows = list(csv.DictReader(open(lst)))[: a.limit or None]
        tag = name + (f"_limit{a.limit}" if a.limit else "")
        od = OUT / a.backbone
        od.mkdir(parents=True, exist_ok=True)
        if (od / f"{tag}.mean.npy").exists():
            print("exists", od / f"{tag}.mean.npy", flush=True)
            continue
        if model is None:
            model, tf, cfg = F.build(a.backbone)
            model.to("cuda")
        npt = model.num_prefix_tokens
        g = F.BACKBONES[a.backbone]["size"] // model.patch_embed.patch_size[0]
        T, D = g * g, model.embed_dim
        dl = torch.utils.data.DataLoader(F.Items([r["path"] for r in rows], tf, False), batch_size=a.bs,
                                         num_workers=a.workers)
        out = np.zeros((len(rows), D), np.float32)
        i, t0 = 0, time.time()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, _ in dl:
                t = model.forward_features(x.to("cuda", non_blocking=True))[:, npt:].float()
                assert t.shape[1] == T
                out[i:i + len(x)] = t.half().float().mean(1).cpu().numpy()
                i += len(x)
                if (i // a.bs) % 25 == 0:
                    print(f"{tag} {i}/{len(rows)} {i / (time.time() - t0):.1f} img/s", flush=True)
        assert i == len(rows)
        np.save(od / f"{tag}.ids.npy", np.array([r["id"] for r in rows]))
        np.save(od / f"{tag}.mean.npy", out)
        json.dump(dict(backbone=a.backbone, timm=F.BACKBONES[a.backbone]["timm"], transform=str(tf), grid=g,
                       prefix_tokens=npt, list=lst, list_sha256=hashlib.sha256(open(lst, "rb").read()).hexdigest(),
                       n=len(rows), af0_feat_sha256=AF0FEAT_SHA, seconds=round(time.time() - t0, 1),
                       gpu=torch.cuda.get_device_name(0), torch=torch.__version__),
                  open(od / f"{tag}.meta.json", "w"), indent=1)
        print(f"DONE {tag} {len(rows)} images {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()

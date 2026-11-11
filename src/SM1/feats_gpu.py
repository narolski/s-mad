"""SM1 frozen-feature pass for one x86 CUDA machine (amendment A7: all rebuilt-arm head features from one platform).

Self-contained pack (gpu_pack.py): code/{feats_gpu.py, common.py, a12_released.py} (the loader and the release input
adapter, unchanged, sha256 in MANIFEST.json), weights/vit_large_patch14_clip_224.openai.bin (the timm hub file
cached on the DGX, sha256 in MANIFEST.json), lists/<name>.csv (id, rel), images/<rel> (one tar per image set).
Feature = F.normalize(tower(x)) with tower = timm vit_large_patch14_clip_quickgelu_224 (QuickGELU, OpenAI weights,
CLIP projection as head, 768-d): the MADation FE release's feature; input = common.ImageItems at 224 (PIL bilinear)
-> a12_released.adapt_input with the FE spec (BGR, (x - 0.5) / 0.5); TF32 matmuls; no TTA.
Resumable: each list is cut into shards of 5,000 rows; a shard's npz (id, feat) is written once and skipped if present.

  python feats_gpu.py --pack DIR --out DIR [--lists a,b,...] [--workers 6] [--bs 128] [--limit 8]
-> OUT/<list>__<k>.npz, OUT/feats_gpu_log.jsonl, OUT/env.json
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import sys
import time

import numpy as np

SHARD = 5000


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lists", default="")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--bs", type=int, default=128)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    pk = pathlib.Path(a.pack)
    man = json.load(open(pk / "MANIFEST.json"))
    for rel, h in man["code_and_weights"].items():
        assert sha(pk / rel) == h, rel
    sys.path.insert(0, str(pk / "code"))
    os.environ["HF_HUB_OFFLINE"] = "1"
    import torch
    import torch.nn.functional as F
    import timm
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    spec = R.RELEASES["madation_fe_vitl14"]
    net = timm.create_model("vit_large_patch14_clip_quickgelu_224", pretrained=True,
                            pretrained_cfg_overlay=dict(file=str(pk / "weights/vit_large_patch14_clip_224.openai.bin")))
    net = net.cuda().eval()
    od = pathlib.Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    env = dict(python=sys.version.split()[0], torch=torch.__version__, timm=timm.__version__, numpy=np.__version__,
               pillow=__import__("PIL").__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
               head_shape=list(net.head.weight.shape), act=str(type(net.blocks[0].mlp.act)))
    json.dump(env, open(od / "env.json", "w"), indent=1)
    print(json.dumps(env), flush=True)
    names = a.lists.split(",") if a.lists else sorted(p.stem for p in (pk / "lists").glob("*.csv"))
    root = pk / "images"
    for name in names:
        rows = list(csv.DictReader(open(pk / "lists" / f"{name}.csv")))[: a.limit or None]
        for k in range(0, len(rows), SHARD):
            fo = od / (f"{name}__{k // SHARD:03d}" + (f"_limit{a.limit}" if a.limit else "") + ".npz")
            if fo.exists():
                continue
            part = rows[k:k + SHARD]
            dl = torch.utils.data.DataLoader(C.ImageItems([(r["rel"], 0) for r in part], 224, root=str(root)),
                                             batch_size=a.bs, num_workers=a.workers)
            t0, feats = time.time(), []
            with torch.no_grad():
                for x, _ in dl:
                    x = R.adapt_input(x.cuda(non_blocking=True), spec)
                    feats.append(F.normalize(net(x).float(), dim=-1).cpu().numpy())
            Fm = np.concatenate(feats).astype(np.float32)
            assert len(Fm) == len(part)
            np.savez(str(fo) + ".tmp.npz", id=np.array([r["id"] for r in part]), feat=Fm)
            os.replace(str(fo) + ".tmp.npz", fo)
            log = dict(list=name, shard=k // SHARD, n=len(part), seconds=round(time.time() - t0, 1),
                       img_per_s=round(len(part) / max(time.time() - t0, 1e-9), 1))
            with open(od / "feats_gpu_log.jsonl", "a") as f:
                f.write(json.dumps(log) + "\n")
            print(json.dumps(log), flush=True)
    print("FEATS_GPU_DONE", flush=True)


if __name__ == "__main__":
    main()

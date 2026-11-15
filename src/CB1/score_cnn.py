"""CB1: score our CNN retrains of published S-MAD recipes (A12-BR R x d0 primaries, A45 arms) on the CB1 image list.

Scoring only. Model build and image loader are imported unchanged from the pinned program code (the code root given by
--code, e.g. /home/narolski/mambamorph-code-a36/smadcvpr: common.py b5d42a99..., archs_a12.py bedfeb86...): the network is
archs_a12.build_a12(arch, res, pretrained=False) and loads the checkpoint with torch.load(weights_only=True); the input
is common.ImageItems (PIL bilinear 512 -> res, /255, no augmentation), exactly the loader of score.py; normalisation is
inside the model. Output per network and checkpoint: sigmoid(logit) of the original image (score_noTTA) and the mean
with the horizontally flipped image (score, the TTA of score.py). One pass over the images per resolution feeds every
network of that resolution.
  python3 -I score_cnn.py --code CODE_DIR --nets NETS.tsv --images IMAGES.csv --out OUT_DIR [--limit N] [--bs 64]
NETS.tsv columns: net_id, arch, res, ckpt (absolute path), sha256 (checked before loading)
Writes OUT_DIR/<net_id>.npz (id, score, score_noTTA, logit_noTTA, images_sha256, ckpt_sha256) once; existing files skip.
"""
import argparse
import csv
import hashlib
import pathlib
import sys
import time

import numpy as np


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--images", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    sys.path.insert(0, a.code)
    import torch
    from torch.utils.data import DataLoader
    import common as C
    import archs_a12
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(a.images)))
    if a.limit:
        rows = rows[:a.limit]
    ids = np.array([r["id"] for r in rows])
    isha = sha(a.images)
    nets = [r for r in csv.DictReader(open(a.nets), delimiter="\t")]
    todo = [n for n in nets if not (out / f"{n['net_id']}.npz").exists()]
    print(f"{len(todo)} of {len(nets)} networks to score on {len(rows)} images; device {dev}", flush=True)
    for res in sorted({int(n["res"]) for n in todo}):
        group = [n for n in todo if int(n["res"]) == res]
        models = []
        for n in group:
            h = sha(n["ckpt"])
            if h != n["sha256"]:
                sys.exit(f"checkpoint sha256 mismatch {n['ckpt']}: {h} != {n['sha256']}")
            m, _ = archs_a12.build_a12(n["arch"], res, None, pretrained=False)
            sd = torch.load(n["ckpt"], map_location="cpu", weights_only=True)
            missing, unexpected = m.load_state_dict(sd, strict=True), None
            m.to(dev).eval()
            models.append((n, m, h))
        dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], res, root="/"),
                        batch_size=a.bs, num_workers=a.workers)
        acc = {n["net_id"]: ([], [], []) for n, _, _ in models}
        t0 = time.time()
        with torch.no_grad():
            for bi, (x, _) in enumerate(dl):
                x = x.to(dev, non_blocking=True)
                xf = torch.flip(x, dims=[3])
                for n, m, _ in models:
                    l0 = C.forward_logit(m, x)[0].float()
                    l1 = C.forward_logit(m, xf)[0].float()
                    p0, p1 = torch.sigmoid(l0), torch.sigmoid(l1)
                    s = acc[n["net_id"]]
                    s[0].append(((p0 + p1) / 2).cpu().numpy())
                    s[1].append(p0.cpu().numpy())
                    s[2].append(l0.cpu().numpy())
                if bi % 20 == 0:
                    print(f"res {res}: batch {bi} of {len(dl)} ({time.time() - t0:.0f}s)", flush=True)
        for n, _, h in models:
            s = acc[n["net_id"]]
            dst = out / f"{n['net_id']}.npz"
            np.savez(str(dst) + ".tmp.npz", id=ids, score=np.concatenate(s[0]), score_noTTA=np.concatenate(s[1]),
                     logit_noTTA=np.concatenate(s[2]), images_sha256=isha, ckpt_sha256=h, arch=n["arch"], res=res)
            pathlib.Path(str(dst) + ".tmp.npz").replace(dst)
            print(f"WRITTEN {dst}", flush=True)
        del models
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()

"""Signal isolation by paired differences (PD1), cross-family transfer: frozen features in the common space.

Model, weights and loader are those of the GAN family (src/PD1/gan/pd1_feats.py: build() and extract(), imported
unchanged; same timm model and OpenAI checkpoint as the frozen-features experiment (FZ1) and the diffusion family; the
existing loader smadcvpr/common.ImageItems(res=224) with its PIL bilinear resize is the only resize).
  clip   : pool = 768-d projected embedding, patch = mean patch token (1,024)
  dinov3 : pool = pooled pre-logits at 224 (1,024; equals the mean patch token)

  tf_feats.py --backbone clip|dinov3 --sets Lad,Lbench,... [--limit 8] [--bs 32] [--workers 2]
  tf_feats.py --backbone clip|dinov3 --check      re-extract 8 diffusion and 8 GAN training images, compare with caches
Writes /mnt/t7/smad_next/PD1/transfer/feats/<backbone>/<set>[_limit8].npz (id, pool, patch float32; meta json).
Run: OMP_NUM_THREADS=2 ... nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I tf_feats.py ...
"""
import argparse
import csv
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/PD1/transfer")
GAN_FEATS = pathlib.Path("/home/narolski/smad-next/src/PD1/gan/pd1_feats.py")


def gan_module():
    spec = importlib.util.spec_from_file_location("pd1_gan_feats", GAN_FEATS)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def check(M, model, norm, backbone, dev, torch):
    res = {}
    D = [r for r in csv.DictReader(open("/mnt/t7/smad_next/PD1/diffae/lists/items.csv")) if r["set"] == "tr"][:8]
    G = [r for r in csv.DictReader(open("/mnt/t7/smad_next/PD1/gan/items.csv")) if r["set"] == "G"][:8]
    cache = {"diffusion": (f"/mnt/t7/smad_next/PD1/diffae/feat/{'clip' if backbone == 'clip' else 'dino'}/tr.npz", D),
             "gan": (f"/mnt/t7/smad_next/PD1/gan/feats/{backbone}/G.npz", G)}
    for fam, (p, rr) in cache.items():
        z = np.load(p, allow_pickle=False)
        pos = {i: k for k, i in enumerate(z["id"].tolist())}
        pool, patch, _, _ = M.extract(model, norm, [r["path"] for r in rr], 8, dev, workers=2)
        k = [pos[r["id"]] for r in rr]
        res[fam] = dict(cache=p, n=len(rr),
                        pool_maxabs=float(np.abs(z["pool"][k] - pool).max()),
                        patch_maxabs=float(np.abs(z["patch"][k] - patch).max()),
                        pool_min_cos=float(min(np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b)
                                               for a, b in zip(z["pool"][k], pool))),
                        ref_absmean=float(np.abs(z["pool"][k]).mean()))
        res[fam]["passes"] = bool(res[fam]["pool_maxabs"] < 1e-3 and res[fam]["patch_maxabs"] < 1e-3)
    print(json.dumps(res, indent=1))
    (OUT / "feats").mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT / f"feats/check_common_space_{backbone}.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True, choices=("clip", "dinov3"))
    ap.add_argument("--sets", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    M = gan_module()
    import torch
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = True     # as the GAN family's extraction (recorded in meta)
    torch.backends.cudnn.allow_tf32 = True
    dev = "cuda"
    model, norm, info = M.build(a.backbone)
    model = model.to(dev)
    if a.check:
        return check(M, model, norm, a.backbone, dev, torch)
    items = list(csv.DictReader(open(OUT / "lists/landmark_items.csv")))
    for s in a.sets.split(","):
        rr = [r for r in items if r["set"] == s][: a.limit or None]
        for r in rr:
            assert not forbidden(r["path"]), r["path"]
        out = OUT / "feats" / a.backbone / f"{s}{'_limit%d' % a.limit if a.limit else ''}.npz"
        if out.exists():
            print("exists, skipped:", out)
            continue
        t0 = time.time()
        pool, patch, dt, dmax = M.extract(model, norm, [r["path"] for r in rr], a.bs, dev, check=True,
                                          workers=a.workers)
        out.parent.mkdir(parents=True, exist_ok=True)
        meta = dict(info, set=s, n=len(rr), seconds=dt, tf32=True, check_forward_vs_head_maxabs=dmax,
                    max_gpu_mem_gb=torch.cuda.max_memory_allocated() / 2**30, source=str(GAN_FEATS))
        np.savez(out, id=np.array([r["id"] for r in rr]), pool=pool.astype(np.float32),
                 patch=patch.astype(np.float32), meta=json.dumps(meta))
        print(f"{a.backbone} {s}: {pool.shape} {patch.shape} in {time.time() - t0:.0f}s; "
              f"max GPU mem {meta['max_gpu_mem_gb']:.2f} GB -> {out}", flush=True)


if __name__ == "__main__":
    main()

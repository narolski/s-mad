"""V4: CLIP ViT-L/14 features (CPU, 2 threads) of set G renders x1/x2/x3 with a fixed face ellipse blanked to grey
(surround only) or the surround blanked (face only). Blanking is done in memory on the 224 px model input; nothing is
written but the small feature file. A 'full' condition on the first N images checks against the owner's cache.
Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I v4_blank_feats.py [--n N] [--check 24]"""
import argparse, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np
import torch
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import vlib as V
sys.path.insert(0, "/home/narolski/smad-next/src/PD1/gan")
from pd1_feats import build  # owner's model builder (weights loading only)

torch.set_num_threads(2)


def ellipse(n=224):
    yy, xx = np.mgrid[0:n, 0:n] / n
    return ((xx - 0.5) / 0.27) ** 2 + ((yy - 0.56) / 0.36) ** 2 <= 1.0


def load(p):
    img = Image.open(p).convert("RGB")
    if img.size != (224, 224):
        img = img.resize((224, 224), Image.BILINEAR)
    return np.asarray(img, dtype=np.float32) / 255.0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--check", type=int, default=24)
    a = ap.parse_args()
    rows = [r for r in V.rows("items.csv") if r["set"] == "G" and r["role"] in ("x1", "x2", "x3")]
    if a.n:
        rows = rows[:a.n]
    model, norm, _ = build("clip")
    mean = torch.tensor(norm[0]).view(1, 3, 1, 1); std = torch.tensor(norm[1]).view(1, 3, 1, 1)
    m = torch.from_numpy(ellipse()).view(1, 1, 224, 224)
    res = {c: ([], []) for c in ("full", "face_only", "surround_only")}
    t0 = time.time()
    with torch.no_grad():
        for k in range(0, len(rows), 8):
            x = torch.from_numpy(np.stack([load(r["path"]) for r in rows[k:k + 8]])).permute(0, 3, 1, 2)
            conds = {"face_only": torch.where(m, x, torch.full_like(x, 0.5)),
                     "surround_only": torch.where(m, torch.full_like(x, 0.5), x)}
            if k < a.check:
                conds["full"] = x
            for c, xx in conds.items():
                tok = model.forward_features((xx - mean) / std)
                res[c][0].append(model.forward_head(tok).numpy()); res[c][1].append(tok[:, 1:].mean(1).numpy())
            print(k + 8, f"{time.time() - t0:.0f}s", flush=True)
    out = {"id": np.array([r["id"] for r in rows])}
    for c, (p, q) in res.items():
        out[f"{c}_pool"] = np.concatenate(p).astype(np.float32); out[f"{c}_patch"] = np.concatenate(q).astype(np.float32)
    np.savez(V.OUT / ("v4_blank_feats.npz" if not a.n else "v4_blank_smoke.npz"), **out)
    # check against owner's cache
    Fo = V.feats("clip", "pool", ["G"])
    f = out["full_pool"]; f = f / np.linalg.norm(f, axis=1, keepdims=True)
    print("min cosine full vs owner cache:", min(float(f[i] @ Fo[rows[i]["id"]]) for i in range(len(f))))

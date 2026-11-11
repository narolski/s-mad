"""FZ2 cross-environment check (registered): features of the 64 A43 check frames from fz2_feats.py (Athena container or
DGX) against FZ1's DGX features of the same frames. Passes if, for clip_mad, the FZ1 P3 head (seed 401) logits agree with
Spearman >= 0.999 and max |d logit| <= 0.05 and the minimum feature cosine is >= 0.9995; for dinov2 the minimum feature
cosine is >= 0.999.

  python -I fz2_envcheck.py --clip NPZ --dino NPZ --out JSON
"""
import argparse, json
import numpy as np
import torch
from scipy.stats import spearmanr

FZ1 = "/mnt/t7/smad_next/FZ1"


def load(p):
    z = np.load(p, allow_pickle=False)
    return {i.split("/")[-1].replace(".png", ""): f for i, f in zip(z["id"].tolist(), z["feat"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True)
    ap.add_argument("--dino", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {}
    for bb, p, thr in (("clip_mad", a.clip, 0.9995), ("dinov2", a.dino, 0.999)):
        new = load(p)
        z = np.load(f"{FZ1}/feats/{bb}/a43.npz", allow_pickle=False)
        ref = dict(zip(z["id"].tolist(), z["feat"]))
        ids = sorted(new)
        A = np.stack([new[i] for i in ids]).astype(np.float64)
        Bm = np.stack([ref[i] for i in ids]).astype(np.float64)
        cos = (A * Bm).sum(1) / np.linalg.norm(A, axis=1) / np.linalg.norm(Bm, axis=1)
        r = {"n": len(ids), "cos_min": float(cos.min()), "cos_mean": float(cos.mean()), "pass_cos": bool(cos.min() >= thr)}
        if bb == "clip_mad":
            sd = torch.load(f"{FZ1}/heads/head_s401.pt", map_location="cpu", weights_only=True)
            W, b = sd["weight"].double().numpy(), sd["bias"].double().numpy()
            lg = lambda X: (X / np.linalg.norm(X, axis=1, keepdims=True)) @ W.T + b  # noqa: E731
            la, lb = lg(A), lg(Bm)
            za, zb = la[:, 0] - la[:, 1], lb[:, 0] - lb[:, 1]
            r.update(logit_max_abs=float(np.abs(za - zb).max()), spearman=float(spearmanr(za, zb)[0]))
            r["pass_head"] = bool(r["spearman"] >= 0.999 and r["logit_max_abs"] <= 0.05)
            r["pass"] = r["pass_cos"] and r["pass_head"]
        else:
            r["pass"] = r["pass_cos"]
        res[bb] = r
    res["pass"] = all(res[b]["pass"] for b in ("clip_mad", "dinov2"))
    print(json.dumps(res, indent=1))
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()

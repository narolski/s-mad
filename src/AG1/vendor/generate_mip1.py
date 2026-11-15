"""MIPGAN-I-style generator (held-out test set only; never a training input). GPU part, cluster or local.

MIPGAN-I (Zhang et al., IEEE T-BIOM 3(3):365-383, 2021, arXiv:2009.01729) = the MIPGAN optimisation on StyleGAN (v1)
FFHQ-1024; init = the average of the two contributors' predicted latents (Eq. 1, w1 = w2 = 1/2), then 150 Adam steps on
the MIPGAN loss (Eq. 10) - exactly generate.py's mipgan() (same losses, lambdas, lr schedule and deviations as our
MIPGAN-II), with the generator swapped for StyleGAN v1 (stylegan1.py, the official karras2019 FFHQ weights).
Deviation (logged): the paper's MIPGAN-I latent predictor (a ResNet-50 encoder for StyleGAN v1) is not released; the
contributor latents are obtained by W+ optimisation instead: init = W+ mean (w_avg x 18), INV_STEPS Adam steps
(lr INV_LR), loss LPIPS-VGG + MSE + 0.1 * (1 - cos ArcFace w600k) at 256^2, stored noise fixed (the
generate.py refine() objective).
Inputs: gan_inputs format (pairs.jsonl rows idx / a / b; contributors.json crop / kps256), db name "casia".
Output: casia_mipgan1_<idx>.png (1024 RGB), _w.npz, log.jsonl.
Usage: generate_mip1.py --inputs DIR --start S --count N --out DIR
"""
import argparse
import json
import os
import pathlib
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arcface as AF  # noqa: E402
import generate as GEN  # noqa: E402
from stylegan1 import StyleGAN1  # noqa: E402

W = GEN.W
SG1 = pathlib.Path(os.environ.get("SG1_WEIGHTS", "/tmp/opencode/mipgan1/models/stylegan1_ffhq1024.pt"))
INV_STEPS = int(os.environ.get("MIP1_INV_STEPS", 500))
INV_LR = float(os.environ.get("MIP1_INV_LR", 0.02))


class Models1(GEN.Models):
    def __init__(self, dev):                     # GEN.Models without e4e; G = StyleGAN v1
        self.G = StyleGAN1()
        self.G.load_state_dict(torch.load(SG1, map_location="cpu"))
        self.G = self.G.to(dev).eval().requires_grad_(False)
        self.arc = AF.IResNet50Fused.load(W / "w600k_r50_fused.pth", dev)
        import torchvision
        vgg = torchvision.models.vgg16()
        vgg.load_state_dict(torch.load(W / "torch/hub/checkpoints/vgg16-397923af.pth", map_location="cpu"))
        vgg = vgg.features.eval().requires_grad_(False)
        self.vgg = vgg[:16].to(dev)
        from lpips_vgg import LPIPSVGG
        self.lpips = LPIPSVGG(vgg, W / "lpips_vgg_v0.1.pth").to(dev).eval().requires_grad_(False)
        from pytorch_msssim import ms_ssim
        self.ms_ssim = ms_ssim
        self.dev = dev

    def synth(self, w):
        return self.G.synthesis(w)


def invert(m, x, M):
    w = m.G.w_avg.view(1, 1, -1).repeat(1, m.G.num_ws, 1).clone().requires_grad_(True)
    opt = torch.optim.Adam([w], lr=INV_LR)
    with torch.no_grad():
        e_t = m.emb(x, M)
    for _ in range(INV_STEPS):
        y = GEN.down(m.synth(w))
        loss = m.lpips(y, x).mean() + F.mse_loss(y, x) + 0.1 * (1 - (m.emb(y, M) * e_t).sum())
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    with torch.no_grad():
        y = GEN.down(m.synth(w))
        cos = float((m.emb(y, M) * e_t).sum())
    return w.detach(), float(loss), cos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    inp = pathlib.Path(a.inputs) / "casia"
    pairs = [json.loads(l) for l in open(inp / "pairs.jsonl")][a.start:a.start + a.count]
    meta = json.load(open(inp / "contributors.json"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    m = Models1(dev)
    print(f"models loaded in {time.time() - t0:.1f} s on {torch.cuda.get_device_name()}", flush=True)
    cache = {}

    def contributor(name):
        if name not in cache:
            x = GEN.load_png(inp / meta[name]["crop"]).to(dev)
            M = AF.estimate_norm(np.array(meta[name]["kps256"]))
            t = time.time()
            w, loss, cos = invert(m, x, M)
            cache[name] = {"x": x, "M": M, "w": w, "inv_loss": loss, "inv_cos_w600k": cos, "t_inv": time.time() - t}
        return cache[name]

    log = open(out / "log.jsonl", "a")
    for p in pairs:
        stem = f"casia_mipgan1_{p['idx']:04d}"
        if (out / f"{stem}.png").exists():
            continue
        t = time.time()
        ca, cb = contributor(p["a"]), contributor(p["b"])
        Mm = AF.estimate_norm((np.array(meta[p["a"]]["kps256"]) + np.array(meta[p["b"]]["kps256"])) / 2)
        w, terms = GEN.mipgan(m, ca["x"], cb["x"], ca["M"], cb["M"], Mm, (ca["w"] + cb["w"]) / 2)
        rec = {"stem": stem, **p, "gen": "mipgan1", "terms": terms,
               "inv": {n: {k: cache[n][k] for k in ("inv_loss", "inv_cos_w600k", "t_inv")} for n in (p["a"], p["b"])}}
        with torch.no_grad():
            img = m.synth(w)
            y = GEN.down(img)
            rec["w600k_cos_a"] = float((m.emb(y, ca["M"]) * m.emb(ca["x"], ca["M"])).sum())
            rec["w600k_cos_b"] = float((m.emb(y, cb["M"]) * m.emb(cb["x"], cb["M"])).sum())
        arr = ((img[0].clamp(-1, 1) + 1) * 127.5).round().byte().permute(1, 2, 0).cpu().numpy()
        torch.cuda.synchronize()
        rec["seconds"] = time.time() - t
        from PIL import Image
        Image.fromarray(arr).save(out / f"{stem}.png", compress_level=1)
        np.savez_compressed(out / f"{stem}_w.npz", w=w.cpu().numpy().astype(np.float32))
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(f"{stem} {rec['seconds']:.1f}s cosA={rec['w600k_cos_a']:.3f} cosB={rec['w600k_cos_b']:.3f} "
              f"inv_cos={ca['inv_cos_w600k']:.3f}/{cb['inv_cos_w600k']:.3f}", flush=True)
    print(f"GEN_DONE casia mipgan1 {len(pairs)} pairs in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()

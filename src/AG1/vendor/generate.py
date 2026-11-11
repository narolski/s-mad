"""GPU part of the GAN morph generators (cluster or local). Torch + torchvision only (+ pytorch_msssim, pure
Python, in the gan_weights pack; LPIPS-VGG is lpips_vgg.py), no insightface / onnxruntime: detection and the training-frame alignment run locally
(prep_inputs.py before, finalize.py after), so the aligner is bit-identical to the one of the bona fide pool.

Backbone: StyleGAN2 FFHQ config-f 1024 = the decoder inside e4e_ffhq_encode.pt (rosinality port; weight-identical to
ffhq.pkl: mapping and synthesis tensors compared, max |diff| = 0), run with the pure-PyTorch upfirdn2d / leaky-ReLU
ops (no nvcc in the container). Encoder: e4e (FFHQ). Identity model in the loss: buffalo_l w600k_r50 (arcface.py;
potency is measured with glintr100, never with this model).

Generators (--gen):
  stylegan  e4e W+ of each contributor, refined by REFINE_STEPS of W+ optimisation toward that contributor
            (LPIPS-VGG + MSE + 0.1 * (1 - cos ArcFace), Adam lr 0.01, fixed noise), then w = (wA + wB) / 2 -> decode.
  mipgan2   MIPGAN-style reimplementation of MIPGAN-II (Zhang et al., IEEE T-BIOM 3(3):365-383, 2021, Sec. II-A/II-B):
            init w = (e4e(A) + e4e(B)) / 2 (Eq. 1, w1 = w2 = 1, the encoder's predictions), then 150 Adam iterations
            (beta1 0.9, beta2 0.999, eps 1e-8, lr 0.03 decayed x0.95 every 6 iterations) on
            Loss = 0.0002 * Perceptual + 10 * Identity + 1 * MS-SSIM + 1 * ID-Diff   (Eq. 10, lambda1..4)
            Perceptual = mean over contributors of sum_i 1/N_i ||F_i(I_k) - F_i(I_M)||^2, VGG-16 conv1_1, conv1_2,
            conv2_2, conv3_3 (Eq. 2); Identity = mean of (1 - cos) to both (Eq. 3); ID-Diff = |d_A - d_B| (Eq. 7);
            MS-SSIM = mean of (1 - MS-SSIM) to both, 5 scales, standard weights (Eq. 9).
            Deviations (logged): perceptual / MS-SSIM at 256^2 (generator output area-downsampled), VGG fed 0-255
            mean-subtracted RGB (the paper's TF/Keras VGG scale convention), torchvision VGG-16 weights, ArcFace
            w600k_r50 on a differentiable 112^2 crop at the mean of the contributors' 5 points.
Output per morph (into --out, a node-local dir): <db>_<gen>_<pairidx>.png (raw 1024, RGB as PNG), plus the
latents (npz) and one JSON line per morph in log.jsonl (timings, loss terms, w600k cosines). tar at the end is
done by the job script.
Usage: generate.py --inputs DIR --gen stylegan|mipgan2 --db feret|frgc --start S --count N --out DIR
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
from argparse import Namespace

import numpy as np
import torch
import torch.nn.functional as F

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arcface as AF  # noqa: E402

W = pathlib.Path(os.environ.get("GAN_WEIGHTS", "/tmp/opencode/gan_protocol/pack/weights/gan"))
REFINE_STEPS = int(os.environ.get("GAN_REFINE_STEPS", 300))
MIP = dict(iters=150, lr=0.03, decay=0.95, every=6, l1=0.0002, l2=10.0, l3=1.0, l4=1.0)
VGG_MEAN = torch.tensor([123.68, 116.779, 103.939]).view(1, 3, 1, 1)


def load_png(p, size=256):
    from PIL import Image
    im = Image.open(p).convert("RGB")
    if im.size != (size, size):
        im = im.resize((size, size), Image.BOX)
    return torch.from_numpy(np.asarray(im, np.float32).transpose(2, 0, 1).copy())[None] / 127.5 - 1


class Models:
    def __init__(self, dev):
        sys.path.insert(0, str(W / "e4e_src"))
        from models.psp import pSp
        ck = torch.load(W / "e4e_ffhq_encode.pt", map_location="cpu", weights_only=False)
        opts = ck["opts"]
        opts["checkpoint_path"] = str(W / "e4e_ffhq_encode.pt")
        opts["device"] = dev
        del ck
        self.net = pSp(Namespace(**opts)).to(dev).eval().requires_grad_(False)
        self.G = self.net.decoder
        self.arc = AF.IResNet50Fused.load(W / "w600k_r50_fused.pth", dev)
        import torchvision
        vgg = torchvision.models.vgg16()
        vgg.load_state_dict(torch.load(W / "torch/hub/checkpoints/vgg16-397923af.pth", map_location="cpu"))
        vgg = vgg.features.eval().requires_grad_(False)
        self.vgg = vgg[:16].to(dev)                                          # up to relu3_3 (MIPGAN perceptual)
        from lpips_vgg import LPIPSVGG
        self.lpips = LPIPSVGG(vgg, W / "lpips_vgg_v0.1.pth").to(dev).eval().requires_grad_(False)
        from pytorch_msssim import ms_ssim
        self.ms_ssim = ms_ssim
        self.dev = dev

    def synth(self, w):
        img, _ = self.G([w], input_is_latent=True, randomize_noise=False, return_latents=False)
        return img                                            # (1,3,1024,1024) in ~[-1,1]

    @torch.no_grad()
    def encode(self, x256):
        _, w = self.net(x256, resize=True, return_latents=True)
        return w

    def emb(self, x256, M):
        e = self.arc(AF.warp_to_arcface(x256, M, (256, 256)))
        return F.normalize(e, dim=1)

    def vgg_feats(self, x):                                   # x in [-1,1] RGB -> conv1_1, conv1_2, conv2_2, conv3_3
        h = (x + 1) * 127.5 - VGG_MEAN.to(x.device)
        out = []
        for i, layer in enumerate(self.vgg):
            h = layer(h)
            if i in (1, 3, 8, 15):
                out.append(h)
        return out


def down(img):
    return F.avg_pool2d(img.clamp(-1, 1), 4)                  # 1024 -> 256, area


def refine(m, x, M, w0, steps):
    w = w0.clone().requires_grad_(True)
    opt = torch.optim.Adam([w], lr=0.01)
    with torch.no_grad():
        e_t = m.emb(x, M)
    for _ in range(steps):
        y = down(m.synth(w))
        loss = m.lpips(y, x).mean() + F.mse_loss(y, x) + 0.1 * (1 - (m.emb(y, M) * e_t).sum())
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    return w.detach(), loss.item()


def mipgan(m, xa, xb, Ma, Mb, Mm, w0):
    w = w0.clone().requires_grad_(True)
    opt = torch.optim.Adam([w], lr=MIP["lr"], betas=(0.9, 0.999), eps=1e-8)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=MIP["every"], gamma=MIP["decay"])
    with torch.no_grad():
        ea, eb = m.emb(xa, Ma), m.emb(xb, Mb)
        fa, fb = m.vgg_feats(xa), m.vgg_feats(xb)
        ya01, yb01 = (xa + 1) / 2, (xb + 1) / 2
    terms = {}
    for it in range(MIP["iters"]):
        y = down(m.synth(w))
        fy = m.vgg_feats(y)
        perc = 0.5 * sum(F.mse_loss(f, g) for f, g in zip(fy, fa)) + 0.5 * sum(F.mse_loss(f, g) for f, g in zip(fy, fb))
        e = m.emb(y, Mm)
        da, db = 1 - (e * ea).sum(), 1 - (e * eb).sum()
        ident = (da + db) / 2
        iddiff = (da - db).abs()
        y01 = (y + 1) / 2
        mss = 0.5 * (1 - m.ms_ssim(y01, ya01, data_range=1.0)) + 0.5 * (1 - m.ms_ssim(y01, yb01, data_range=1.0))
        loss = MIP["l1"] * perc + MIP["l2"] * ident + MIP["l3"] * mss + MIP["l4"] * iddiff
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        sched.step()
        if it in (0, MIP["iters"] - 1):
            terms[f"it{it}"] = {"perc_x_l1": float(MIP["l1"] * perc), "id": float(ident), "msssim": float(mss),
                                "iddiff": float(iddiff), "loss": float(loss), "cos_a": float(1 - da),
                                "cos_b": float(1 - db)}
    return w.detach(), terms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--gen", choices=["stylegan", "mipgan2"], required=True)
    ap.add_argument("--db", choices=["feret", "frgc"], required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = "cuda"
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    inp = pathlib.Path(a.inputs) / a.db
    pairs = [json.loads(l) for l in open(inp / "pairs.jsonl")][a.start:a.start + a.count]
    meta = json.load(open(inp / "contributors.json"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    m = Models(dev)
    print(f"models loaded in {time.time() - t0:.1f} s on {torch.cuda.get_device_name()}", flush=True)
    cache = {}

    def contributor(name):
        if name not in cache:
            x = load_png(inp / meta[name]["crop"]).to(dev)
            M = AF.estimate_norm(np.array(meta[name]["kps256"]))
            w_e4e = m.encode(x)
            cache[name] = {"x": x, "M": M, "w_e4e": w_e4e, "w_ref": None, "t_ref": 0.0}
        c = cache[name]
        if a.gen == "stylegan" and c["w_ref"] is None:
            torch.cuda.synchronize()
            t = time.time()
            c["w_ref"], c["ref_loss"] = refine(m, c["x"], c["M"], c["w_e4e"], REFINE_STEPS)
            torch.cuda.synchronize()
            c["t_ref"] = time.time() - t
        return c

    log = open(out / "log.jsonl", "a")
    for p in pairs:
        stem = f"{a.db}_{a.gen}_{p['idx']:04d}"
        if (out / f"{stem}.png").exists():
            continue
        torch.cuda.synchronize()
        t = time.time()
        new = [n for n in (p["a"], p["b"]) if n not in cache or (a.gen == "stylegan" and cache[n]["w_ref"] is None)]
        ca, cb = contributor(p["a"]), contributor(p["b"])
        rec = {"stem": stem, **p, "gen": a.gen, "new_contributors": len(new)}
        if a.gen == "stylegan":
            w = (ca["w_ref"] + cb["w_ref"]) / 2
            rec["refine_s"] = {n: cache[n]["t_ref"] for n in new}
        else:
            Mm = AF.estimate_norm((np.array(meta[p["a"]]["kps256"]) + np.array(meta[p["b"]]["kps256"])) / 2)
            w, rec["terms"] = mipgan(m, ca["x"], cb["x"], ca["M"], cb["M"], Mm, (ca["w_e4e"] + cb["w_e4e"]) / 2)
        with torch.no_grad():
            img = m.synth(w)
            y = down(img)
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
        print(f"{stem} {rec['seconds']:.1f}s new={len(new)} cosA={rec['w600k_cos_a']:.3f} cosB={rec['w600k_cos_b']:.3f}",
              flush=True)
    print(f"GEN_DONE {a.db} {a.gen} {len(pairs)} pairs in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()

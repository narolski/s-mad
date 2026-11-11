"""StyleGAN (v1, Karras et al. CVPR 2019) FFHQ-1024 generator in pure PyTorch, a re-implementation of the official
TF networks_stylegan.py G_style (mapping 8 x 512 lrmul 0.01, pixel-norm latents; synthesis: const 4x4, per layer
noise -> bias -> lrelu 0.2 -> instance norm -> StyleMod; upscale nearest + conv below 128, fused transposed conv from
128 up, [1,2,1] blur after every upscale; equalised learning rate everywhere; ToRGB at 1024 only, lod 0).
Weights: the official karras2019stylegan-ffhq-1024x1024.pkl (CC BY-NC 4.0), read with stylegan2-ada-pytorch's TF
stub unpickler (no TF) and stored as a plain state dict (convert mode).
Usage (convert): stylegan1.py <karras2019...pkl> <out.pt> <stylegan2-ada-pytorch dir>
"""
import math
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

NF = {4: 512, 8: 512, 16: 512, 32: 512, 64: 256, 128: 128, 256: 64, 512: 32, 1024: 16}


def lrelu(x):
    return F.leaky_relu(x, 0.2)


class Layer(nn.Module):
    """One synthesis layer: (conv | const) -> [blur] -> epilogue."""

    def __init__(self, res, cin, cout, kind):
        super().__init__()
        self.kind, self.res = kind, res
        if kind == "const":
            self.const = nn.Parameter(torch.zeros(1, cout, 4, 4))
        else:
            self.weight = nn.Parameter(torch.zeros(cout, cin, 3, 3))
            self.wcoef = math.sqrt(2) / math.sqrt(cin * 9)
        self.noise_weight = nn.Parameter(torch.zeros(cout))
        self.bias = nn.Parameter(torch.zeros(cout))
        self.style_w = nn.Parameter(torch.zeros(2 * cout, 512))
        self.style_b = nn.Parameter(torch.zeros(2 * cout))
        self.register_buffer("noise", torch.zeros(1, 1, res, res))
        self.register_buffer("blur", (torch.tensor([1., 2., 1.])[:, None] * torch.tensor([1., 2., 1.])[None] / 16)
                             [None, None])

    def forward(self, x, w):
        if self.kind == "const":
            x = self.const.expand(w.shape[0], -1, -1, -1)
        else:
            wt = self.weight * self.wcoef
            if self.kind == "conv":
                x = F.conv2d(x, wt, padding=1)
            elif self.kind == "up":
                x = F.conv2d(F.interpolate(x, scale_factor=2, mode="nearest"), wt, padding=1)
            else:                                   # fused: transposed conv with the 4-tap summed kernel
                k = F.pad(wt, (1, 1, 1, 1))
                k = k[:, :, 1:, 1:] + k[:, :, :-1, 1:] + k[:, :, 1:, :-1] + k[:, :, :-1, :-1]
                x = F.conv_transpose2d(x, k.transpose(0, 1), stride=2, padding=1)
            if self.kind in ("up", "fused"):
                c = x.shape[1]
                x = F.conv2d(x, self.blur.expand(c, 1, 3, 3), padding=1, groups=c)
        x = x + self.noise * self.noise_weight.view(1, -1, 1, 1)
        x = lrelu(x + self.bias.view(1, -1, 1, 1))
        x = x - x.mean((2, 3), keepdim=True)
        x = x * torch.rsqrt((x * x).mean((2, 3), keepdim=True) + 1e-8)
        s = F.linear(w, self.style_w * (1 / math.sqrt(512)), self.style_b).view(w.shape[0], 2, -1, 1, 1)
        return x * (s[:, 0] + 1) + s[:, 1]


class StyleGAN1(nn.Module):
    def __init__(self):
        super().__init__()
        self.map_w = nn.ParameterList([nn.Parameter(torch.zeros(512, 512)) for _ in range(8)])
        self.map_b = nn.ParameterList([nn.Parameter(torch.zeros(512)) for _ in range(8)])
        self.register_buffer("w_avg", torch.zeros(512))
        layers = [Layer(4, 512, 512, "const"), Layer(4, 512, 512, "conv")]
        res = 8
        while res <= 1024:
            layers += [Layer(res, NF[res // 2], NF[res], "fused" if res >= 128 else "up"),
                       Layer(res, NF[res], NF[res], "conv")]
            res *= 2
        self.layers = nn.ModuleList(layers)
        self.rgb_w = nn.Parameter(torch.zeros(3, 16, 1, 1))
        self.rgb_b = nn.Parameter(torch.zeros(3))
        self.num_ws = len(layers)

    def mapping(self, z):
        x = z * torch.rsqrt((z * z).mean(1, keepdim=True) + 1e-8)
        for w, b in zip(self.map_w, self.map_b):
            x = lrelu(F.linear(x, w * (math.sqrt(2) / math.sqrt(512) * 0.01), b * 0.01))
        return x

    def synthesis(self, ws):                       # ws (N, 18, 512) -> (N, 3, 1024, 1024), ~[-1, 1]
        x = None
        for i, layer in enumerate(self.layers):
            x = layer(x, ws[:, i])
        return F.conv2d(x, self.rgb_w * (1 / math.sqrt(16)), self.rgb_b)


def convert(pkl, out, sg2ada):
    sys.path.insert(0, sg2ada)
    import legacy
    Gs = legacy._LegacyUnpickler(open(pkl, "rb")).load()[2]
    p = {k: torch.from_numpy(np.asarray(v, np.float32)) for k, v in legacy._collect_tf_params(Gs).items()}
    G = StyleGAN1()
    sd = {"w_avg": p["dlatent_avg"], "rgb_w": p["synthesis/ToRGB_lod0/weight"].permute(3, 2, 0, 1),
          "rgb_b": p["synthesis/ToRGB_lod0/bias"]}
    for i in range(8):
        sd[f"map_w.{i}"] = p[f"mapping/Dense{i}/weight"].t()
        sd[f"map_b.{i}"] = p[f"mapping/Dense{i}/bias"]
    names = ["4x4/Const", "4x4/Conv"]
    r = 8
    while r <= 1024:
        names += [f"{r}x{r}/Conv0_up", f"{r}x{r}/Conv1"]
        r *= 2
    for i, n in enumerate(names):
        q = f"synthesis/{n}/"
        if i == 0:
            sd[f"layers.{i}.const"] = p[q + "const"]
        else:
            sd[f"layers.{i}.weight"] = p[q + "weight"].permute(3, 2, 0, 1)
        sd[f"layers.{i}.noise_weight"] = p[q + "Noise/weight"]
        sd[f"layers.{i}.bias"] = p[q + "bias"]
        sd[f"layers.{i}.style_w"] = p[q + "StyleMod/weight"].t()
        sd[f"layers.{i}.style_b"] = p[q + "StyleMod/bias"]
        sd[f"layers.{i}.noise"] = p[f"synthesis/noise{i}"]
        sd[f"layers.{i}.blur"] = G.layers[i].blur
    G.load_state_dict(sd, strict=True)
    torch.save(G.state_dict(), out)
    print(f"converted {len(p)} TF tensors -> {out}")


if __name__ == "__main__":
    convert(*sys.argv[1:4])

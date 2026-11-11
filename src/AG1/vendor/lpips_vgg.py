"""LPIPS v0.1 (VGG) without the lpips package (it imports scipy and tqdm, not guaranteed in the cluster container):
torchvision VGG-16 relu1_2 / relu2_2 / relu3_3 / relu4_3 / relu5_3, channel-unit-normalised, squared difference,
the learned 1x1 weights of lpips/weights/v0.1/vgg.pth (BSD-2, Zhang et al. 2018), spatial mean, summed over layers.
Verified against lpips.LPIPS(net='vgg') locally (verify_lpips in this file)."""
import torch
import torch.nn as nn

SHIFT = torch.tensor([-.030, -.088, -.188]).view(1, 3, 1, 1)
SCALE = torch.tensor([.458, .448, .450]).view(1, 3, 1, 1)
CUTS = (4, 9, 16, 23, 30)        # vgg16.features end indices (exclusive) of the five slices


class LPIPSVGG(nn.Module):
    def __init__(self, vgg_features, lin_path):
        super().__init__()
        self.slices = nn.ModuleList()
        prev = 0
        for c in CUTS:
            self.slices.append(nn.Sequential(*[vgg_features[i] for i in range(prev, c)]))
            prev = c
        sd = torch.load(lin_path, map_location="cpu")
        self.lins = nn.ParameterList([nn.Parameter(sd[f"lin{i}.model.1.weight"], requires_grad=False) for i in range(5)])
        self.register_buffer("shift", SHIFT)
        self.register_buffer("scale", SCALE)

    def forward(self, x, y):                 # x, y in [-1, 1]
        h1, h2 = (x - self.shift) / self.scale, (y - self.shift) / self.scale
        val = 0
        for s, w in zip(self.slices, self.lins):
            h1, h2 = s(h1), s(h2)
            n1 = h1 / (h1.pow(2).sum(1, keepdim=True).sqrt() + 1e-10)
            n2 = h2 / (h2.pow(2).sum(1, keepdim=True).sqrt() + 1e-10)
            val = val + (nn.functional.conv2d((n1 - n2) ** 2, w)).mean((2, 3), keepdim=True)
        return val


def verify_lpips(vgg_path, lin_path):
    import torchvision
    import lpips
    v = torchvision.models.vgg16()
    v.load_state_dict(torch.load(vgg_path, map_location="cpu"))
    mine = LPIPSVGG(v.features.eval(), lin_path).eval()
    ref = lpips.LPIPS(net="vgg", verbose=False).eval()
    g = torch.Generator().manual_seed(0)
    x, y = torch.rand(2, 3, 256, 256, generator=g) * 2 - 1, torch.rand(2, 3, 256, 256, generator=g) * 2 - 1
    with torch.no_grad():
        a, b = mine(x, y).flatten(), ref(x, y).flatten()
    return float((a - b).abs().max()), a.tolist(), b.tolist()

"""Differentiable ArcFace (insightface buffalo_l w600k_r50, IResNet-50) as a plain PyTorch module.

The ONNX graph of w600k_r50 is an IResNet-50 whose bn2/bn3 (and the downsample BN) are folded into the convolutions:
  stem   conv3x3(3->64, bias) -> PReLU
  block  x -> BN(x) -> conv3x3(bias) -> PReLU -> conv3x3(stride, bias)  (+ x, or conv1x1(stride, bias)(x))
  head   BN2d(512) -> flatten -> Linear(25088->512) -> BN1d(512)
build_from_onnx2torch() copies the weights of an onnx2torch conversion into this module in graph order (local only;
needs onnx2torch); IResNet50Fused.load(path) reads the saved state_dict (cluster: torch only).
Input: RGB in [-1, 1] ((x/255 - 0.5)/0.5, insightface's ArcFaceONNX input_mean = input_std = 127.5), 112x112,
aligned to ARCFACE_DST (insightface.utils.face_align.arcface_dst).
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ARCFACE_DST = np.array([[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [41.5493, 92.3655],
                        [70.7299, 92.2041]], dtype=np.float32)
LAYERS = (3, 4, 14, 3)
WIDTHS = (64, 128, 256, 512)


class Block(nn.Module):
    def __init__(self, cin, cout, stride):
        super().__init__()
        self.bn1 = nn.BatchNorm2d(cin, eps=1e-5)
        self.conv1 = nn.Conv2d(cin, cout, 3, 1, 1, bias=True)
        self.prelu = nn.PReLU(cout)
        self.conv2 = nn.Conv2d(cout, cout, 3, stride, 1, bias=True)
        self.down = nn.Conv2d(cin, cout, 1, stride, 0, bias=True) if (stride != 1 or cin != cout) else None

    def forward(self, x):
        y = self.conv2(self.prelu(self.conv1(self.bn1(x))))
        return y + (self.down(x) if self.down is not None else x)


class IResNet50Fused(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, 1, 1, bias=True)
        self.prelu = nn.PReLU(64)
        blocks, cin = [], 64
        for n, w in zip(LAYERS, WIDTHS):
            for i in range(n):
                blocks.append(Block(cin, w, 2 if i == 0 else 1))
                cin = w
        self.blocks = nn.Sequential(*blocks)
        self.bn2 = nn.BatchNorm2d(512, eps=1e-5)
        self.fc = nn.Linear(512 * 7 * 7, 512)
        self.features = nn.BatchNorm1d(512, eps=1e-5)

    def forward(self, x):
        x = self.blocks(self.prelu(self.conv1(x)))
        return self.features(self.fc(torch.flatten(self.bn2(x), 1)))

    @classmethod
    def load(cls, path, device="cpu"):
        m = cls()
        m.load_state_dict(torch.load(path, map_location="cpu"))
        return m.to(device).eval().requires_grad_(False)


def build_from_onnx2torch(onnx_path):
    """Convert with onnx2torch, then copy every parameter/buffer into IResNet50Fused in execution order."""
    import onnx2torch
    gm = onnx2torch.convert(str(onnx_path)).eval()
    mods = dict(gm.named_modules())
    order = {"Conv2d": [], "PReLU": [], "BatchNorm2d": [], "Linear": [], "BatchNorm1d": []}
    prelu_w = {}
    for node in gm.graph.nodes:
        if node.op == "call_module":
            m = mods[node.target]
            k = type(m).__name__
            if k == "OnnxPReLU":
                order["PReLU"].append(node)
            elif k in order:
                order[k].append(m)
        elif node.op == "get_attr":
            prelu_w[node.name] = gm.get_parameter(node.target) if node.target in dict(gm.named_parameters()) \
                else gm.get_buffer(node.target)
    net = IResNet50Fused().eval()
    convs = [net.conv1]
    for b in net.blocks:   # graph order inside a block: conv1, conv2, then the downsample conv (applied to x)
        convs += [b.conv1, b.conv2] + ([b.down] if b.down is not None else [])
    prelus = [net.prelu] + [b.prelu for b in net.blocks]
    bns = [b.bn1 for b in net.blocks] + [net.bn2]
    assert len(convs) == len(order["Conv2d"]) == 53 and len(prelus) == len(order["PReLU"]) == 25
    assert len(bns) == len(order["BatchNorm2d"]) == 25
    for dst, src in zip(convs, order["Conv2d"]):
        assert dst.weight.shape == src.weight.shape and dst.stride == src.stride, (dst, src)
        dst.weight.data.copy_(src.weight.data)
        dst.bias.data.copy_(src.bias.data)
    for dst, node in zip(prelus, order["PReLU"]):
        w = prelu_w[node.args[1].name]
        dst.weight.data.copy_(w.reshape(-1))
    for dst, src in zip(bns + [net.features], order["BatchNorm2d"] + order["BatchNorm1d"]):
        dst.load_state_dict(src.state_dict())
        dst.eps = src.eps
    net.fc.load_state_dict(order["Linear"][0].state_dict())
    return net, gm


def estimate_norm(kps):
    """2x3 similarity mapping 5 landmarks to ARCFACE_DST (least squares, as skimage SimilarityTransform)."""
    src = np.asarray(kps, np.float64)
    dst = ARCFACE_DST.astype(np.float64)
    sm, dm = src.mean(0), dst.mean(0)
    s0, d0 = src - sm, dst - dm
    a = (s0 * d0).sum() / (s0 ** 2).sum()
    b = (s0[:, 0] * d0[:, 1] - s0[:, 1] * d0[:, 0]).sum() / (s0 ** 2).sum()
    M = np.array([[a, -b, 0.0], [b, a, 0.0]])
    M[:, 2] = dm - M[:, :2] @ sm
    return M


def warp_to_arcface(img, M, size_hw):
    """Differentiable crop: img (B,3,H,W) in [-1,1], M (2x3, pixel coords of an image of size size_hw) -> (B,3,112,112)."""
    H, W = size_hw
    A = np.vstack([M, [0, 0, 1]])
    Ai = np.linalg.inv(A)                                  # output pixel -> input pixel
    ys, xs = np.meshgrid(np.arange(112) + 0.0, np.arange(112) + 0.0, indexing="ij")
    pts = np.stack([xs, ys, np.ones_like(xs)], -1) @ Ai.T  # (112,112,3)
    gx = (pts[..., 0] + 0.5) / W * 2 - 1
    gy = (pts[..., 1] + 0.5) / H * 2 - 1
    grid = torch.from_numpy(np.stack([gx, gy], -1)).float().to(img.device)[None].expand(img.shape[0], -1, -1, -1)
    return F.grid_sample(img, grid, mode="bilinear", padding_mode="border", align_corners=False)

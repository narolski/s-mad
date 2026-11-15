"""PROTOCOL A12 architectures (plans/A12/plan.md A.5 and A.7 C1; branch a12 only). Every name starts with ``a12_``.

Same interface as archs_v2: ARCHS_A12[arch] = (family, spec, norm), and
build_a12(arch, res, drop_path=None, *, pretrained=None) -> (model, extra). common.build_model dispatches here for the
``a12_`` prefix only (A.7 C2), so no E0-E11 / A8 / A9 / A10 name can reach this module.

Model output contract (common.forward_logit reads the first two elements of a tuple):
* every model maps x in [0,1] (B,3,R,R) to (logit[B], pixel_map or None);
* ``a12_pwmad_densenet121`` returns its pixel map as the second element: (B,1,h,w) logits (h = w = 14 at 224), which
  train.py supervises with lambda_px x BCE(map, y) (extra["lambda_px"] = 1.0);
* ``a12_resnet18_orthomad_scratch`` returns a 3-tuple (logit, None, {"aux": aux}), aux = 100 x mean_b((z1_b . z2_b)^2)
  (the full weighted term: train.py adds extra_out["aux"] to the loss unscaled; plan A.7 C3 "an aux-loss hook (a
  model may return aux in extra)"). The aux term is returned in eval mode as well; scoring ignores it.
extra = {"lambda_px", "lambda_ortho" (0: no MADMamba gate term), "drop_path" (the stochastic-depth rate actually set;
None = none set), "drop_path_skipped" (the requested rate that the architecture cannot apply: timm inception_v3 and
densenet121 have no stochastic depth and raise a TypeError on drop_path_rate; None otherwise; plan A.7 C1 "the
skipped value is recorded in meta"), "weights" (where the pretrained tensors came from: "file:<path>", "hf:<hub id>",
or None for random init)}.

Entries (plan A.5; native resolution and league in NATIVE_RES / LEAGUE):
* ``a12_inception_v3_scratch`` (M1): timm ``inception_v3``, random init, single logit, ImageNet normalisation (common
  Wrapped). Its stem needs res >= 75 (MIN_RES), so CPU smokes of this name run at >= 75 px (e.g. 96), not 64.
* ``a12_hrnet_w48_scratch`` (M2): timm ``hrnet_w48``, random init, timm's classification head; stochastic depth on the
  residual blocks by archs_v2._hrnet_drop_path (timm's HRNet ignores drop_path_rate), as the A9 hrnet_w18_scratch.
* ``a12_hrnet_w18_in1k`` (M4): timm ``hrnet_w18.ms_aug_in1k`` (ImageNet-1k), single logit, same drop path.
* ``a12_pwmad_densenet121`` (M5): timm ``densenet121.tv_in1k`` features up to ``transition2`` (256 x 14 x 14 at 224),
  a 1x1 conv to a one-channel map (logits), and a Linear((R/16)^2, 1) on the sigmoid of the map (the DeepPixBiS head)
  that gives the logit; the score is that logit.
* ``a12_clip_vitb16_madation`` (M3) / ``a12_clip_vitl14_madation`` (M3L, Tier 2): the CLIP visual tower (timm
  ``.openai`` weights, QuickGELU as in the original CLIP and MADation's ``clip`` package; the weights are the files of
  ``vit_{base_patch16,large_patch14}_clip_224.openai``), entirely frozen including its projection (512-d / 768-d),
  the projected feature L2-normalised, Linear(d, 1) as the only trainable module (513 / 769 parameters).
  ``head_parameters()`` = that Linear only, so common.head_param_names / apply_lora never unfreeze the projection.
  LoRA (q/v, r 2, alpha 4, rsLoRA, dropout 0.4) is applied by train.py --ft lora through common.apply_lora on the timm
  ``attn.qkv`` modules: 12 x 2 x (2 x 768 + 768 x 2) = 73,728 (ViT-B) and 24 x 2 x (2 x 1024 + 1024 x 2) = 196,608
  (ViT-L) parameters. With weights the tower is built at 224 only (CLIP_RES; any other res is refused, since timm
  would resample the pretrained position embedding); a random-init build (pretrained=False) takes any res.
* ``a12_resnet18_orthomad_scratch`` (M6): timm ``resnet18`` (random init, 512-d pooled feature), two Linear(512, 32)
  identity heads z1, z2, Linear(64, 1) on their concatenation, aux 100 x mean((z1 . z2)^2).
* ``a12_mixfacenet_s_scratch`` (M8, Tier 2; AI-2 approved 2026-10-31): MixFaceNet-MAD. The network is
  mixfacenet_port.mixnet_s (the reviewed port of the used blocks of the SMDD / MixFaceNets code, CC BY-NC-SA 4.0; its
  header lists the source commits, file sha256s, licences and every change) with the published SMDD configuration
  (embedding 128, gdw 1024, width 1.0, shuffle False; MixConv kernel sets, SE factors and expansions of MixNet-S;
  official _init_params, random init) and its MAD layer up to the BatchNorm1d(128) (weight frozen at 1, as published),
  then Linear(128, 1) = ``head.cls`` in place of the published Linear(128, 2) (single logit as every A12 entry).
  Input normalisation: the registry's (ImageNet mean/std, common Wrapped) in place of the published BGR / 0.5. No
  stochastic depth (a requested --drop-path is recorded as drop_path_skipped). Needs res >= 97 (MIN_RES: four
  stride-2 stages, then the unpadded 7x7 depthwise conv; 224 gives an 8 x 8 map before the global pool). It refuses
  unless the AI-2 approval file plans/A12/AI-2.approved exists.
* ``a12_mixfacenet_s_official`` (M8 O arm, the official-code arm of plans/A12/M8O.md; author's instruction of
  2026-10-31; same AI-2 refusal, random init only, NATIVE_RES 224, L0, MIN_RES 97): the same mixfacenet_port.mixnet_s
  network with the published head and input. ``head.cls`` = Linear(128, 2) built right after the backbone, i.e. after
  the official _init_params, with torch's default Linear init (SMDD main.py builds ``linear2`` there, so at the same seed
  ``head.cls`` gets the tensors the official ``linear2`` gets). Input "bgr05": our loader gives RGB in [0, 1], the
  network sees x[:, [2, 1, 0]] and then (x - 0.5) / 0.5, i.e. cv2.imread's BGR order, ToTensor and Normalize(0.5, 0.5)
  (a channel permutation and an affine map: no resampling). Official classes: 0 = attack, 1 = bona fide. forward ->
  (z[:, 0] - z[:, 1], None), the morph (official class 0) logit: sigmoid of it is the official softmax probability of
  class 0, so BCE with target 1 = morph is the 2-class cross-entropy of z (train.py --loss-norm wsum: the official
  class-weighted mean), and scoring / R-es read it as every other entry's logit. head_outputs(arch) = 2; train.py
  refuses the options defined on single-logit heads for it (--ft lpft / llrd / lora, --head-lr, --kd-teacher).

Weights (offline): pretrained towers are built by timm.create_model(pretrained=True), which reads the HF cache
(HF_HOME; on the cluster $L/hf with HF_HUB_OFFLINE=1, filled on the login node by cluster/fetch_weights.sh a12;
locally ~/.cache/huggingface). timm loads model.safetensors where the hub has one (hrnet_w18.ms_aug_in1k,
densenet121.tv_in1k) and otherwise pytorch_model.bin with torch.load(weights_only=True). The CLIP repos have no
timm-format safetensors, so fetch_weights.sh a12 converts their pytorch_model.bin (weights_only=True under python -I)
to $HF_HOME/a12/<weights tag>.safetensors; when that file exists it is loaded instead (same tensors, no pickle).
Head / classifier parameters: ``model.net.get_classifier()`` for the Wrapped timm entries; ``head.*`` (with
``head.cls`` the final Linear, common.head_linear) for PW-MAD, OrthoMAD and the CLIP entries.
"""
from __future__ import annotations

import os
import pathlib
import sys
from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
for _p in (ROOT, HERE):   # morphmamba, and common (Wrapped) / archs_v2 as train.py imports them
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

AI2_APPROVAL = HERE / "plans" / "A12" / "AI-2.approved"     # M8 MixFaceNet-MAD (author item AI-2; default dropped)
CONVERTED_SUBDIR = "a12"                                      # $HF_HOME/a12/<tag>.safetensors (fetch_weights.sh a12)

ARCHS_A12 = {
    # M1 Inception-MAD (L0)
    "a12_inception_v3_scratch": ("timm_scratch", "inception_v3", "imnet"),
    # M2 MorphHRNet-style (L0; width W48, AI-5)
    "a12_hrnet_w48_scratch": ("timm_scratch", "hrnet_w48", "imnet"),
    # M4 SelfMAD-style (L1)
    "a12_hrnet_w18_in1k": ("timm", "hrnet_w18.ms_aug_in1k", "imnet"),
    # M5 PW-MAD (L1; ImageNet-1k init, AI-4b)
    "a12_pwmad_densenet121": ("pwmad", dict(timm="densenet121.tv_in1k", pretrained=True, upto="transition2",
                                            lambda_px=1.0), "imnet"),
    # M3 MADation ViT-B/16 (L2)
    "a12_clip_vitb16_madation": ("clip_madation", dict(timm="vit_base_patch16_clip_quickgelu_224.openai",
                                                       weights="vit_base_patch16_clip_224.openai", dim=512,
                                                       pretrained=True), "clip"),
    # M6 OrthoMAD (L0; scratch, AI-4c)
    "a12_resnet18_orthomad_scratch": ("orthomad", dict(timm="resnet18", pretrained=False, z=32, aux_w=100.0),
                                      "imnet"),
    # Tier 2: M3L MADation ViT-L/14 (L2; descriptive)
    "a12_clip_vitl14_madation": ("clip_madation", dict(timm="vit_large_patch14_clip_quickgelu_224.openai",
                                                       weights="vit_large_patch14_clip_224.openai", dim=768,
                                                       pretrained=True), "clip"),
    # Tier 2: M8 MixFaceNet-MAD (L0; only if AI-2; refuses without plans/A12/AI-2.approved). Published configuration
    # (SMDD main.py: mixnet_s(embedding_size=128, width_scale=1.0, gdw_size=1024, shuffle=False)).
    "a12_mixfacenet_s_scratch": ("mixfacenet", dict(pretrained=False, approval=str(AI2_APPROVAL), embedding_size=128,
                                                    width_scale=1.0, gdw_size=1024, shuffle=False), "imnet"),
    # Tier 2: M8 O arm (plans/A12/M8O.md; AI-2): the same network with the official Linear(128, 2) head (built after
    # _init_params) and the official input (BGR, mean/std 0.5); forward returns the class-0 (attack) minus class-1 logit.
    "a12_mixfacenet_s_official": ("mixfacenet", dict(pretrained=False, approval=str(AI2_APPROVAL), embedding_size=128,
                                                     width_scale=1.0, gdw_size=1024, shuffle=False, official=True),
                                  "bgr05"),
    # BB2 (second backbone for the PN1 protocol recipe; experiments/BB2_second-backbone/prereg.md): the MADation head on
    # a frozen DINOv3 ViT-L/16 (timm vit_large_patch16_dinov3.lvd1689m), final-normed CLS token (1024-d),
    # L2-normalised, Linear(1024, 1); ImageNet normalisation (the DINOv3 processor's constants); 224 px only.
    "a12_dinov3_vitl16_madation": ("dinov3_madation", dict(timm="vit_large_patch16_dinov3.lvd1689m",
                                                         weights="vit_large_patch16_dinov3.lvd1689m", dim=1024,
                                                         pretrained=True), "imnet"),
}
NATIVE_RES = {"a12_inception_v3_scratch": 299, "a12_hrnet_w48_scratch": 256, "a12_hrnet_w18_in1k": 384,
              "a12_pwmad_densenet121": 224, "a12_clip_vitb16_madation": 224, "a12_resnet18_orthomad_scratch": 224,
              "a12_clip_vitl14_madation": 224, "a12_mixfacenet_s_scratch": 224, "a12_mixfacenet_s_official": 224,
              "a12_dinov3_vitl16_madation": 224}
LEAGUE = {"a12_inception_v3_scratch": "L0", "a12_hrnet_w48_scratch": "L0", "a12_hrnet_w18_in1k": "L1",
          "a12_pwmad_densenet121": "L1", "a12_clip_vitb16_madation": "L2", "a12_resnet18_orthomad_scratch": "L0",
          "a12_clip_vitl14_madation": "L2", "a12_mixfacenet_s_scratch": "L0", "a12_mixfacenet_s_official": "L0",
          "a12_dinov3_vitl16_madation": "L2"}
MIN_RES = {"a12_inception_v3_scratch": 75,                 # smallest input the timm stem accepts
           "a12_mixfacenet_s_scratch": 97,                 # side ceil(res / 16) >= 7 for the unpadded 7x7 dw conv
           "a12_mixfacenet_s_official": 97}
CLIP_RES = 224                  # pretrained CLIP towers are built at 224 only (no position-embedding resampling)
NO_DROP_PATH = ("inception_v3", "densenet121")              # timm models without stochastic depth (TypeError)


def is_pretrained(arch: str) -> bool | None:
    """Does the A12 architecture start from external weights? None for a name outside ARCHS_A12."""
    if arch not in ARCHS_A12:
        return None
    fam, spec, _ = ARCHS_A12[arch]
    return fam == "timm" if isinstance(spec, str) else bool(spec["pretrained"])


def head_outputs(arch: str) -> int | None:
    """Outputs of the arch's head.cls: 2 for an ``official=True`` entry (a12_mixfacenet_s_official: 2 logits, forward
    returns their difference), else 1 (every other A12 entry: a single logit); None for a name outside ARCHS_A12."""
    if arch not in ARCHS_A12:
        return None
    spec = ARCHS_A12[arch][1]
    return 2 if isinstance(spec, dict) and spec.get("official") else 1


def hf_home() -> pathlib.Path:
    """The HF cache root as huggingface_hub resolves it (HF_HOME, else $XDG_CACHE_HOME/huggingface, else
    ~/.cache/huggingface)."""
    h = os.environ.get("HF_HOME")
    if h:
        return pathlib.Path(h).expanduser()
    return pathlib.Path(os.environ.get("XDG_CACHE_HOME", "~/.cache")).expanduser() / "huggingface"


def converted_weights(tag: str) -> pathlib.Path:
    """The safetensors file fetch_weights.sh a12 writes for a hub repo without timm-format safetensors."""
    return hf_home() / CONVERTED_SUBDIR / f"{tag}.safetensors"


def _norm_buffers(module: nn.Module, norm: str) -> None:
    from common import CLIP_MEAN, CLIP_STD, IMNET_MEAN, IMNET_STD
    mean, std = (IMNET_MEAN, IMNET_STD) if norm == "imnet" else (CLIP_MEAN, CLIP_STD)
    module.register_buffer("mean", mean.clone(), persistent=False)
    module.register_buffer("std", std.clone(), persistent=False)


def _create(name: str, pretrained: bool, weights_tag: str | None = None, **kw) -> tuple[nn.Module, str | None]:
    """timm.create_model with offline weights -> (net, weights source). weights_tag: the hub tag whose converted
    safetensors (converted_weights) is preferred when present."""
    import timm
    if not pretrained:
        return timm.create_model(name, pretrained=False, **kw), None
    f = converted_weights(weights_tag) if weights_tag else None
    if f is not None and f.exists():
        return timm.create_model(name, pretrained=True, pretrained_cfg_overlay=dict(file=str(f)), **kw), f"file:{f}"
    hub = timm.models.get_pretrained_cfg(name).hf_hub_id
    try:
        return timm.create_model(name, pretrained=True, **kw), f"hf:{hub}"
    except Exception as e:      # noqa: BLE001 - re-raised with the fetch hint
        raise RuntimeError(f"{name}: pretrained weights ({hub}) not loadable from the HF cache {hf_home()} "
                           f"(offline jobs: run smadcvpr/cluster/fetch_weights.sh a12 on the login node)") from e


class _Head(nn.Module):
    """Container for the trainable head; ``cls`` is the final Linear (common.head_linear)."""

    def __init__(self, **mods):
        super().__init__()
        for k, m in mods.items():
            self.add_module(k, m)


def densenet_map_side(res: int) -> int:
    """Spatial side of timm DenseNet-121 after transition2: conv0 (k7 s2 p3), pool0 (k3 s2 p1), two 2x2 average pools
    (224 -> 112 -> 56 -> 28 -> 14)."""
    s = (res - 1) // 2 + 1
    s = (s - 1) // 2 + 1
    return s // 2 // 2


class PWMAD(nn.Module):
    """PW-MAD (DeepPixBiS template): DenseNet-121 up to transition2 -> 1x1 conv to a one-channel map (logits) ->
    Linear(h*w, 1) on sigmoid(map) = the logit. forward -> (logit[B], map (B,1,h,w) logits)."""

    LAYERS = ("conv0", "norm0", "pool0", "denseblock1", "transition1", "denseblock2", "transition2")

    def __init__(self, res: int, pretrained: bool, norm: str = "imnet", name: str = "densenet121.tv_in1k"):
        super().__init__()
        net, self.weights = _create(name, pretrained)
        self.features = nn.Sequential(OrderedDict((k, getattr(net.features, k)) for k in self.LAYERS))
        del net                                          # denseblock3/4, norm5 and the classifier are not used
        c = self.features.transition2.conv.out_channels   # 256
        self.side = densenet_map_side(res)
        self.head = _Head(pix=nn.Conv2d(c, 1, kernel_size=1), cls=nn.Linear(self.side * self.side, 1))
        _norm_buffers(self, norm)

    def forward(self, x):
        pix = self.head.pix(self.features((x - self.mean) / self.std))        # (B, 1, h, w) logits
        if pix.shape[-2:] != (self.side, self.side):
            raise ValueError(f"PWMAD built for a {self.side}x{self.side} map, got {tuple(pix.shape[-2:])} "
                             f"(input {tuple(x.shape[-2:])}): build with the run's --res")
        return self.head.cls(torch.sigmoid(pix).flatten(1)).squeeze(-1), pix


class OrthoMAD(nn.Module):
    """OrthoMAD: ResNet-18 pooled feature f (512) -> z1 = Linear(512, z)(f), z2 = Linear(512, z)(f) -> Linear(2z, 1)
    on [z1, z2]. forward -> (logit[B], None, {"aux": aux_w x mean_b((z1_b . z2_b)^2)})."""

    def __init__(self, pretrained: bool, drop_path: float | None, norm: str = "imnet", name: str = "resnet18",
                 z: int = 32, aux_w: float = 100.0):
        super().__init__()
        kw = {} if drop_path is None else dict(drop_path_rate=drop_path)
        self.net, self.weights = _create(name, pretrained, num_classes=0, **kw)
        d = self.net.num_features
        self.head = _Head(z1=nn.Linear(d, z), z2=nn.Linear(d, z), cls=nn.Linear(2 * z, 1))
        self.aux_w = float(aux_w)
        _norm_buffers(self, norm)

    def forward(self, x):
        f = self.net((x - self.mean) / self.std)
        z1, z2 = self.head.z1(f), self.head.z2(f)
        logit = self.head.cls(torch.cat([z1, z2], dim=1)).squeeze(-1)
        aux = self.aux_w * ((z1 * z2).sum(dim=1) ** 2).mean()
        return logit, None, {"aux": aux}


class CLIPMADation(nn.Module):
    """MADation: frozen CLIP visual tower (projection kept) -> L2-normalised d-dim feature -> Linear(d, 1).
    forward -> (logit[B], None). Only ``head`` is trainable after the build (LoRA comes from --ft lora)."""

    def __init__(self, name: str, weights_tag: str, dim: int, res: int, pretrained: bool, drop_path: float | None,
                 norm: str = "clip"):
        super().__init__()
        if pretrained and res != CLIP_RES:      # timm would resample the pretrained position embedding (F.interpolate):
            raise ValueError(f"{name}: pretrained CLIP tower at res {res}; only {CLIP_RES} keeps its position "
                             f"embedding unresampled (agents add no resampling; plan 0.8). A random-init smoke "
                             f"(pretrained=False, e.g. archs_a12.py --random-init) may use any res")
        kw = dict(num_classes=dim, img_size=res, dynamic_img_size=False)   # head = the CLIP projection (d x width)
        if drop_path is not None:
            kw["drop_path_rate"] = drop_path
        self.net, self.weights = _create(name, pretrained, weights_tag, **kw)
        for p in self.net.parameters():
            p.requires_grad_(False)
        self.head = _Head(cls=nn.Linear(dim, 1))
        _norm_buffers(self, norm)

    def head_parameters(self):
        return self.head.parameters()

    def forward(self, x):
        f = F.normalize(self.net((x - self.mean) / self.std), dim=-1)
        return self.head.cls(f).squeeze(-1), None


class DINOv3MADation(nn.Module):
    """BB2: the MADation head on DINOv3 ViT-L/16. Frozen timm Eva tower built with num_classes=0 and
    global_pool="token" (the CLS token after the final LayerNorm; no projection exists in DINOv3), the 1024-d feature
    L2-normalised, Linear(1024, 1) the only trainable module (LoRA on attn.qkv q/v from --ft lora, as for CLIP).
    forward -> (logit[B], None). With weights the tower is built at 224 only (DINOv3 has no learned position
    embedding (RoPE), so 224 needs no resampling; 224 is the CLIP arm's input size)."""

    def __init__(self, name: str, weights_tag: str, dim: int, res: int, pretrained: bool, drop_path: float | None,
                 norm: str = "imnet"):
        super().__init__()
        if pretrained and res != CLIP_RES:
            raise ValueError(f"{name}: BB2 builds the pretrained DINOv3 tower at res {CLIP_RES} only, got {res}")
        kw = dict(num_classes=0, global_pool="token", img_size=res)
        if drop_path is not None:
            kw["drop_path_rate"] = drop_path
        self.net, self.weights = _create(name, pretrained, weights_tag, **kw)
        if self.net.num_features != dim:
            raise ValueError(f"{name}: feature width {self.net.num_features}, expected {dim}")
        for p in self.net.parameters():
            p.requires_grad_(False)
        self.head = _Head(cls=nn.Linear(dim, 1))
        _norm_buffers(self, norm)

    def head_parameters(self):
        return self.head.parameters()

    def forward(self, x):
        f = F.normalize(self.net((x - self.mean) / self.std), dim=-1)
        return self.head.cls(f).squeeze(-1), None


class MixFaceNetMAD(nn.Module):
    """M8 MixFaceNet-MAD: mixfacenet_port.mixnet_s (published SMDD configuration, random init by the official
    _init_params) up to its BatchNorm1d(embedding) -> Linear(embedding, 1) = head.cls. forward -> (logit[B], None)."""

    def __init__(self, norm: str = "imnet", embedding_size: int = 128, width_scale: float = 1.0, gdw_size: int = 1024,
                 shuffle: bool = False):
        super().__init__()
        from mixfacenet_port import mixnet_s      # the reviewed port (CC BY-NC-SA 4.0; see its header)
        self.net = mixnet_s(embedding_size=embedding_size, gdw_size=gdw_size, shuffle=shuffle,
                            width_scale=width_scale, num_classes=None)
        self.head = _Head(cls=nn.Linear(embedding_size, 1))
        _norm_buffers(self, norm)

    def forward(self, x):
        return self.head.cls(self.net((x - self.mean) / self.std)).squeeze(-1), None


class MixFaceNetMADOfficial(nn.Module):
    """M8 O arm (plans/A12/M8O.md): mixfacenet_port.mixnet_s as MixFaceNetMAD, then head.cls = Linear(embedding, 2)
    built right after the backbone (the official linear2: after _init_params, torch's default Linear init), on the
    official input: x (RGB in [0, 1]) -> x[:, [2, 1, 0]] (BGR, cv2.imread's order) -> (x - 0.5) / 0.5 (ToTensor +
    Normalize(0.5, 0.5)). Official classes 0 = attack, 1 = bona fide. forward -> (z[:, 0] - z[:, 1], None): the
    morph logit, sigmoid(z0 - z1) = softmax(z)[0]."""

    BGR = [2, 1, 0]                               # x[:, BGR]: RGB -> BGR (advanced indexing, a copy)

    def __init__(self, embedding_size: int = 128, width_scale: float = 1.0, gdw_size: int = 1024,
                 shuffle: bool = False):
        super().__init__()
        from mixfacenet_port import mixnet_s      # the reviewed port (CC BY-NC-SA 4.0; see its header)
        self.net = mixnet_s(embedding_size=embedding_size, gdw_size=gdw_size, shuffle=shuffle,
                            width_scale=width_scale, num_classes=None)
        self.head = _Head(cls=nn.Linear(embedding_size, 2))   # official order: after _init_params, default init

    def forward(self, x):
        z = self.head.cls(self.net((x[:, self.BGR] - 0.5) / 0.5))
        return z[:, 0] - z[:, 1], None


def _mixfacenet_refuse(arch: str = "a12_mixfacenet_s_scratch") -> None:
    """M8 builds only with the AI-2 approval file (plan A.5 M8 / author item AI-2; approved 2026-10-31)."""
    if not AI2_APPROVAL.exists():
        raise RuntimeError(f"refused: {arch} (M8) needs the AI-2 approval (plan A.5 M8 / author "
                           f"item AI-2; default: dropped); {AI2_APPROVAL} does not exist")


def build_a12(arch: str, res: int, drop_path: float | None = None, *,
              pretrained: bool | None = None) -> tuple[nn.Module, dict]:
    """-> (model, extra) as in the module docstring. pretrained: None = the arch's own setting; False forces random
    init (architecture smoke tests only)."""
    if arch not in ARCHS_A12:
        raise KeyError(f"unknown A12 arch {arch!r}")
    fam, spec, norm = ARCHS_A12[arch]
    if res < MIN_RES.get(arch, 1):
        raise ValueError(f"{arch}: res {res} < {MIN_RES[arch]}, the smallest input its stem accepts")
    pre = is_pretrained(arch) if pretrained is None else pretrained
    extra = {"lambda_px": 0.0, "lambda_ortho": 0.0, "drop_path": drop_path, "drop_path_skipped": None,
             "weights": None}
    if fam == "mixfacenet":
        _mixfacenet_refuse(arch)
        if pre:
            raise ValueError(f"{arch}: random init only (no MixFaceNet weights are loaded; plan A.5 M8)")
        if spec.get("official"):                  # M8 O arm: 2-class head, BGR / 0.5 input (norm "bgr05")
            if norm != "bgr05":
                raise ValueError(f"{arch}: the official-code entry takes the bgr05 input, not {norm!r}")
            m = MixFaceNetMADOfficial(spec["embedding_size"], spec["width_scale"], spec["gdw_size"], spec["shuffle"])
        else:
            m = MixFaceNetMAD(norm, spec["embedding_size"], spec["width_scale"], spec["gdw_size"], spec["shuffle"])
        extra.update(drop_path=None, drop_path_skipped=drop_path)     # no stochastic depth in MixFaceNet
        return m, extra
    if fam in ("timm", "timm_scratch"):
        from common import Wrapped
        base = spec.split(".")[0]
        hrnet, nodp = base.startswith("hrnet"), base in NO_DROP_PATH
        kw = dict(num_classes=1)
        if drop_path is not None and not hrnet and not nodp:
            kw["drop_path_rate"] = drop_path
        net, extra["weights"] = _create(spec, pre, **kw)
        if hrnet and drop_path:
            from archs_v2 import _hrnet_drop_path      # the A9 hrnet_w18_scratch scheme (archs_v2 is read-only)
            _hrnet_drop_path(net, drop_path)
        if nodp:
            extra.update(drop_path=None, drop_path_skipped=drop_path)
        return Wrapped(net, norm), extra
    if fam == "pwmad":
        m = PWMAD(res, pre, norm, spec["timm"])
        extra.update(lambda_px=spec["lambda_px"], drop_path=None, drop_path_skipped=drop_path, weights=m.weights)
        return m, extra
    if fam == "orthomad":
        m = OrthoMAD(pre, drop_path, norm, spec["timm"], spec["z"], spec["aux_w"])
        extra.update(weights=m.weights)
        return m, extra
    if fam == "clip_madation":
        m = CLIPMADation(spec["timm"], spec["weights"], spec["dim"], res, pre, drop_path, norm)
        extra.update(weights=m.weights)
        return m, extra
    if fam == "dinov3_madation":                  # BB2 only; no other name reaches this branch
        m = DINOv3MADation(spec["timm"], spec["weights"], spec["dim"], res, pre, drop_path, norm)
        extra.update(weights=m.weights)
        return m, extra
    raise KeyError(f"{arch}: family {fam!r} has no builder")


def param_counts(model: nn.Module) -> dict:
    """Total, trainable and head parameter counts (head = head_parameters() / head.* / the timm classifier)."""
    from common import head_param_names
    head = head_param_names(model)
    ps = dict(model.named_parameters())
    return {"total": sum(p.numel() for p in ps.values()),
            "trainable": sum(p.numel() for p in ps.values() if p.requires_grad),
            "head": sum(ps[n].numel() for n in head)}


def main():
    """Build (and optionally forward/backward) every A12 name: python smadcvpr/archs_a12.py [--res R | --native]
    [--names a,b] [--device cpu|cuda] [--random-init] [--fwd-bwd] [--bs 2]."""
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=None)
    ap.add_argument("--native", action="store_true", help="each name at its NATIVE_RES")
    ap.add_argument("--names", default=",".join(ARCHS_A12))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--random-init", action="store_true", help="pretrained=False (no weights needed)")
    ap.add_argument("--fwd-bwd", action="store_true")
    ap.add_argument("--bs", type=int, default=2)
    ap.add_argument("--drop-path", type=float, default=None)
    a = ap.parse_args()
    for arch in [n for n in a.names.split(",") if n]:
        res = NATIVE_RES[arch] if a.native or a.res is None else max(a.res, MIN_RES.get(arch, 1))
        torch.manual_seed(0)
        model, extra = build_a12(arch, res, a.drop_path, pretrained=False if a.random_init else None)
        model.to(a.device).train()
        row = {"arch": arch, "res": res, **param_counts(model), **{k: v for k, v in extra.items()}}
        if a.fwd_bwd:
            x = torch.rand(a.bs, 3, res, res, device=a.device)
            out = model(x)
            logit, pix = out[0], out[1] if len(out) > 1 else None
            loss = F.binary_cross_entropy_with_logits(logit, torch.ones_like(logit))
            if pix is not None:
                loss = loss + extra["lambda_px"] * F.binary_cross_entropy_with_logits(pix, torch.ones_like(pix))
            if len(out) > 2 and "aux" in out[2]:
                loss = loss + out[2]["aux"]
                row["aux"] = out[2]["aux"].item()
            loss.backward()
            g = [p.grad for p in model.parameters() if p.requires_grad]
            row.update(logit=list(logit.shape), map=list(pix.shape) if pix is not None else None,
                       loss=loss.item(), grads_finite=all(t is not None and bool(torch.isfinite(t).all()) for t in g))
            if a.device.startswith("cuda"):
                row["max_mem_GB"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
                torch.cuda.reset_peak_memory_stats()
        print(json.dumps(row), flush=True)
        del model


if __name__ == "__main__":
    main()

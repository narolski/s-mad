"""Input resolution and resize method (RZ1): the input transforms of every RZ1 arm.

Author's ruling, 13 Nov 2026 evening (NOTEBOOK 19:20): for RZ1 the input may be 512 px and resampling code that varies
the resize method may be written. Nothing else changes: the stored images (aligned 512 x 512 PNG frames, the existing
shrink-and-enlarge storage copies, JPEG branch) are read as they are; this module only maps a stored 512 frame to the
network input.

Kernels (KERNELS, name -> function(PIL RGB image, (w, h)) -> PIL RGB image):
  pil_bilinear   PIL Image.BILINEAR = the current loader (common.ImageItems.load); PIL antialiases when shrinking
  pil_nearest    PIL Image.NEAREST (no antialiasing)
  pil_bicubic    PIL Image.BICUBIC (antialiased when shrinking)
  pil_lanczos    PIL Image.LANCZOS (antialiased when shrinking)
  pil_box        PIL Image.BOX (area average)
  cv_area        cv2.INTER_AREA
  cv_linear      cv2.INTER_LINEAR (no antialiasing)
  cv_cubic       cv2.INTER_CUBIC (no antialiasing; uint8 saturation)
  cv_lanczos4    cv2.INTER_LANCZOS4 (no antialiasing; uint8 saturation)
Transforms (Transform(spec)):
  fixed:<kernel>   every image resized to res with that kernel (fixed:pil_bilinear = the current loader, bit for bit)
  mix              per image a kernel drawn uniformly from the nine
  mixR             per image: with p 0.5 a two-step resize res_in -> s -> res, s = round(exp(U(ln 256, ln 400))),
                   each step with its own uniformly drawn kernel; otherwise one step as in mix. At res 512 the
                   two-step branch is 512 -> s -> 512 (a shrink-and-enlarge); the one-step branch leaves the frame as is
  two:<s>:<k1>:<k2>  deterministic two-step resize 512 -> s (kernel k1) -> res (kernel k2); test side only
  crop:<x0>:<y0>   integer slice frame[y0:y0+res, x0:x0+res] of the stored frame (no resampling at all)
Held-out kernels (HELDOUT; never used in training, never drawn by mix / mixR; test side only, pre-run review M2):
  pil_hamming (PIL Image.HAMMING), cv_nearest (cv2.INTER_NEAREST), cv_linear_exact (cv2.INTER_LINEAR_EXACT); the
  held-out two-step transform two:300:pil_hamming:cv_linear_exact.
OpenCV runs single-threaded (cv2.setNumThreads(1)) inside the loader workers (pre-run review m3).
Random draws come from a numpy Generator per loader worker seeded with (torch.initial_seed() + 7919) mod 2**63, a
stream separate from common.ImageItems' own (flip) stream, so the flip draws of a fixed-kernel arm are unchanged.
"""
import math

import numpy as np
from PIL import Image

S_LO, S_HI, P_TWO = 256, 400, 0.5


def _pil(flag):
    return lambda im, wh: im.resize(wh, flag)


def _cv(flag):
    def f(im, wh):
        import cv2
        return Image.fromarray(cv2.resize(np.asarray(im), wh, interpolation=flag))
    return f


def _kernels():
    import cv2
    cv2.setNumThreads(1)
    return {"pil_bilinear": _pil(Image.BILINEAR), "pil_nearest": _pil(Image.NEAREST), "pil_bicubic": _pil(Image.BICUBIC),
            "pil_lanczos": _pil(Image.LANCZOS), "pil_box": _pil(Image.BOX), "cv_area": _cv(cv2.INTER_AREA),
            "cv_linear": _cv(cv2.INTER_LINEAR), "cv_cubic": _cv(cv2.INTER_CUBIC), "cv_lanczos4": _cv(cv2.INTER_LANCZOS4)}


KERNELS = _kernels()
NAMES = tuple(KERNELS)          # order fixed: index = draw value (the nine training kernels)


def _heldout():
    import cv2
    return {"pil_hamming": _pil(Image.HAMMING), "cv_nearest": _cv(cv2.INTER_NEAREST),
            "cv_linear_exact": _cv(cv2.INTER_LINEAR_EXACT)}


HELDOUT = _heldout()
ALL = {**KERNELS, **HELDOUT}


class Transform:
    def __init__(self, spec: str, res: int):
        self.spec, self.res = spec, int(res)
        self.kind, _, arg = spec.partition(":")
        if self.kind == "fixed":
            if arg not in ALL:
                raise ValueError(f"RZ1 transform {spec}: kernel {arg!r} not in {tuple(ALL)}")
            self.k = arg
        elif self.kind == "two":
            s_, k1, k2 = arg.split(":")
            if k1 not in ALL or k2 not in ALL:
                raise ValueError(f"RZ1 transform {spec}: kernels")
            self.s, self.k1, self.k2 = int(s_), k1, k2
        elif self.kind == "crop":
            x0, y0 = (int(v) for v in arg.split(":"))
            self.x0, self.y0 = x0, y0
        elif self.kind not in ("mix", "mixR"):
            raise ValueError(f"RZ1 transform {spec!r}")
        self._g, self._pid = None, None

    def rng(self):
        import os
        import torch
        if self._pid != os.getpid():
            self._g, self._pid = np.random.default_rng((torch.initial_seed() + 7919) % 2 ** 63), os.getpid()
        return self._g

    def __call__(self, img: Image.Image) -> Image.Image:
        R = (self.res, self.res)
        if self.kind == "crop":
            if img.size[0] < self.x0 + self.res or img.size[1] < self.y0 + self.res:
                raise ValueError(f"RZ1 crop {self.spec}: frame {img.size} too small")
            return img.crop((self.x0, self.y0, self.x0 + self.res, self.y0 + self.res))
        if self.kind == "fixed":
            return img if img.size == R else ALL[self.k](img, R)
        if self.kind == "two":
            return ALL[self.k2](ALL[self.k1](img, (self.s, self.s)), R)
        g = self.rng()
        if self.kind == "mixR" and g.random() < P_TWO:
            s = int(round(math.exp(g.uniform(math.log(S_LO), math.log(S_HI)))))
            k1, k2 = NAMES[g.integers(len(NAMES))], NAMES[g.integers(len(NAMES))]
            return KERNELS[k2](KERNELS[k1](img, (s, s)), R)
        k = NAMES[g.integers(len(NAMES))]
        return img if img.size == R else KERNELS[k](img, R)

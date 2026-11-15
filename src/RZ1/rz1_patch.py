"""RZ1: patch the unchanged pack code (smadcvpr/common.py, archs_a12.py) at import time, without editing any pack file.

  RZ1_TRANSFORM   transform spec of rz1_kernels.Transform (default fixed:pil_bilinear = the current loader)
  RZ1_RES512=1    allow the pretrained CLIP ViT-B/16 tower at --res 512: archs_a12.CLIP_RES is set to 512, so timm
                  builds the tower at img_size 512 and its checkpoint filter resamples the 14 x 14 pretrained position
                  embedding to 32 x 32 (timm resample_abs_pos_embed, bicubic; registered design choice of wave 2)
apply(code_dir) must be called before train.py / the scorer build a dataset or a model.
"""
import os
import pathlib
import sys

STATE = {}


def apply(code_dir):
    sys.path.insert(0, str(pathlib.Path(code_dir) / "smadcvpr"))
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import common as C
    import archs_a12 as AR
    import rz1_kernels as K
    STATE["spec"] = spec = os.environ.get("RZ1_TRANSFORM", "fixed:pil_bilinear")
    if os.environ.get("RZ1_RES512") == "1":
        AR.CLIP_RES = 512
    cache = {}

    def load(self, p):
        from PIL import Image
        img = Image.open(self.root / p).convert("RGB")
        w0 = img.size[0]
        spec = STATE["spec"]
        t = cache.get((spec, self.res))
        if t is None:
            t = cache[(spec, self.res)] = K.Transform(spec, self.res)
        img = t(img)
        if img.size != (self.res, self.res):
            raise RuntimeError(f"RZ1: transform {spec} gave {img.size}, not {self.res}")
        return img, w0

    C.ImageItems.load = load
    return spec


def set_spec(spec):
    """Scorer: switch the transform (the next load() call uses it)."""
    os.environ["RZ1_TRANSFORM"] = STATE["spec"] = spec

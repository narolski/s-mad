import sys
import torch
import logging
import clip
import os

class ClipModel():
    def __init__(self, rank, model_name):
        if os.environ.get("AD5_CLIP_SD"):  # AD5 patch: same tensors as clip.load (checked), no download, weights_only
            sd = torch.load(os.environ["AD5_CLIP_SD"], map_location="cpu", weights_only=True)
            self.backbone = clip.model.build_model(sd).to("cuda")
        else:
            self.backbone, _ = clip.load(model_name, device="cuda", jit=False)
        self.backbone.to(rank)

        for param in self.backbone.parameters():
            if param.dtype == torch.float16:
                param.data = param.data.to(torch.float32)


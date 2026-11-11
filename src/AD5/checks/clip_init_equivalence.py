"""Retrains of released methods (AD5): check that our CLIP initialisation equals the authors'.

The authors' MADation code calls clip.load(name, device="cuda", jit=False) on the OpenAI TorchScript file. Our patched
backbone/model.py instead calls clip.model.build_model(state_dict) on the OpenAI-format state dict of the Hugging Face
file timm/<name>.openai (pytorch_model.bin, loaded with weights_only=True), then the authors' own fp16 -> fp32 cast.
This script rebuilds that path on CPU and compares every tensor with the authors' frozen-encoder (FE) release
checkpoint 40_backbone.pth (the CLIP model after the authors' load path; the FE run never updates the encoder).

  python3 -I clip_init_equivalence.py MODEL_PY HF_BIN FE_BACKBONE OUT_JSON
"""
import hashlib
import importlib.util
import json
import sys

import torch


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


model_py, hf_bin, fe_pth, out = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("clip_model", model_py)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
sd = torch.load(hf_bin, map_location="cpu", weights_only=True)
m = cm.build_model(dict(sd))                      # the authors' clip.load(jit=False) minus the file source
for p in m.parameters():                          # the authors' ClipModel.__init__ cast
    if p.dtype == torch.float16:
        p.data = p.data.to(torch.float32)
ours = m.state_dict()
fe = torch.load(fe_pth, map_location="cpu", weights_only=True)
k_ours, k_fe = set(ours), set(fe)
common = sorted(k_ours & k_fe)
diff = {k: float((ours[k].float() - fe[k].float()).abs().max()) for k in common}
dtype_mismatch = [k for k in common if ours[k].dtype != fe[k].dtype]
rep = dict(model_py=model_py, model_py_sha256=sha(model_py), hf_bin=hf_bin, hf_bin_sha256=sha(hf_bin),
           fe_backbone=fe_pth, fe_backbone_sha256=sha(fe_pth), n_ours=len(k_ours), n_fe=len(k_fe),
           only_ours=sorted(k_ours - k_fe), only_fe=sorted(k_fe - k_ours), n_common=len(common),
           max_abs_diff=max(diff.values()), n_nonzero=sum(v > 0 for v in diff.values()),
           worst=sorted(diff.items(), key=lambda kv: -kv[1])[:5], dtype_mismatch=dtype_mismatch[:10])
json.dump(rep, open(out, "w"), indent=1)
print(json.dumps({k: rep[k] for k in ("n_ours", "n_fe", "only_ours", "only_fe", "max_abs_diff", "n_nonzero",
                                      "dtype_mismatch")}))

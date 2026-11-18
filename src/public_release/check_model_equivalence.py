"""PRIVATE check (CPU, synthetic inputs only): the release training/model.py equals the research model
(common.build_run_model + apply_lora of the PN1 code) - same initial LoRA tensors under the same seed, and the same
logits on random images with a frozen Sb network's trained tensors loaded.
  HF_HOME=<pack>/hf python3 -I check_model_equivalence.py <release-repo>"""
import json, os, sys, random
import numpy as np, torch
REL, CODE = sys.argv[1], "/mnt/t7/smad_next/FRLL_READ_V1/pn1_code/pn1/code"
sys.path.insert(0, CODE + "/smadcvpr"); sys.path.insert(0, REL + "/training")
import common as C
from model import Detector
W = os.environ["HF_HOME"] + "/a12/vit_base_patch16_clip_224.openai.safetensors"
net = REL + "/weights/sb_frozen_s403-407/PN1_Sb_s403"
meta = json.load(open(net + "/meta.json"))
def seeded(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)
seeded(403); old, _ = C.build_model(meta["arch"], meta["res"], meta.get("drop_path")); C.apply_lora(old, meta["lora_r"], **C.lora_settings(meta))
seeded(403); new = Detector("vitb16", 2, 4.0, 0.4, weights_file=W)
so = {n: p for n, p in old.named_parameters() if p.requires_grad}
sn = {n: p for n, p in new.named_parameters() if p.requires_grad}
assert so.keys() == sn.keys(), set(so) ^ set(sn)
init_same = all(torch.equal(so[k], sn[k]) for k in so)
frozen_same = all(torch.equal(a, b) for a, b in zip(old.state_dict().values(), new.state_dict().values()))
tr = torch.load(net + "/last_trainable.pt", map_location="cpu", weights_only=True)
old.load_state_dict(tr, strict=False); new.load_state_dict(tr, strict=False); old.eval(); new.eval()
g = torch.Generator().manual_seed(0); x = torch.rand(8, 3, 224, 224, generator=g)
with torch.no_grad():
    lo, ln = C.forward_logit(old, x)[0], new(x)
d = float((lo - ln).abs().max())
print("initial trainable tensors identical:", init_same, "| all tensors identical:", frozen_same, "| max |logit diff|:", d, lo[:3].tolist())
sys.exit(0 if init_same and frozen_same and d == 0.0 else 1)

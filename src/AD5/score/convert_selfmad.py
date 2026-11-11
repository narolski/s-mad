"""Retrains of released methods (AD5): SelfMAD retrain checkpoint -> the release's storage format.

The authors' train__.py saves {"model": Detector.state_dict() (keys net.*), "optimizer": ..., "epoch": ...}. The
release we score (hrnet_w18_checkpoint.model.safetensors, sha256 0ad8db6f...) is that "model" dict as safetensors.
  python3 -I convert_selfmad.py EPOCH_TAR OUT.safetensors [RELEASE.safetensors]
Loads with torch.load(weights_only=True); checks key set and shapes against the release when given; prints JSON.
"""
import hashlib
import json
import sys

import torch
from safetensors.torch import load_file, save_file

src, dst = sys.argv[1], sys.argv[2]
d = torch.load(src, map_location="cpu", weights_only=True)
sd = {k: v.contiguous() for k, v in d["model"].items()}
rep = dict(src=src, epoch_index=int(d["epoch"]), tensors=len(sd))
if len(sys.argv) > 3:
    r = load_file(sys.argv[3])
    rep.update(release_tensors=len(r), same_keys=set(r) == set(sd),
               same_shapes=all(tuple(r[k].shape) == tuple(sd[k].shape) for k in r if k in sd))
    assert rep["same_keys"] and rep["same_shapes"], rep
save_file(sd, dst, metadata={"source": src})
rep["sha256"] = hashlib.sha256(open(dst, "rb").read()).hexdigest()
print(json.dumps(rep))

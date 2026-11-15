"""BB2 amendment 3: log the effective fp32 matmul / convolution precision under this torch build after setting TF32 the
way pn1_score.py and src/TT1/rescore_tf32.py do (legacy flags torch.backends.cuda.matmul.allow_tf32 = True and
torch.backends.cudnn.allow_tf32 = True). Prints the legacy flags, the newer fp32_precision attributes where the build
has them, and an empirical check: the relative error of a 4096 x 4096 fp32 matmul against fp64 (about 1e-7 for IEEE
fp32, about 1e-4 to 1e-3 for TF32). Also asserts the GPU name. Decides nothing beyond the GPU assertion.
  python -I precision_probe.py --expect-gpu "NVIDIA H100" """
import argparse
import json
import sys

import torch

ap = argparse.ArgumentParser()
ap.add_argument("--expect-gpu", required=True)
a = ap.parse_args()
name = torch.cuda.get_device_name(0)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
rec = dict(gpu=name, torch=torch.__version__, cuda=torch.version.cuda,
           legacy_matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32, legacy_cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
           float32_matmul_precision=torch.get_float32_matmul_precision())
for path in ("backends.fp32_precision", "backends.cuda.matmul.fp32_precision", "backends.cudnn.fp32_precision",
             "backends.cudnn.conv.fp32_precision", "backends.cudnn.rnn.fp32_precision"):
    o = torch
    try:
        for p in path.split("."):
            o = getattr(o, p)
        rec[path] = str(o)
    except Exception:  # noqa: BLE001 - attribute absent in this build
        rec[path] = "absent"
g = torch.Generator(device="cuda").manual_seed(0)
x = torch.randn(4096, 4096, device="cuda", generator=g)
y = torch.randn(4096, 4096, device="cuda", generator=g)
ref = (x.double() @ y.double())
rec["matmul_rel_err_vs_fp64"] = float(((x @ y).double() - ref).norm() / ref.norm())
c = torch.nn.Conv2d(64, 64, 3, padding=1).cuda()
xi = torch.randn(8, 64, 56, 56, device="cuda", generator=g)
cd = torch.nn.Conv2d(64, 64, 3, padding=1).cuda().double()
cd.load_state_dict({k: v.double() for k, v in c.state_dict().items()})
with torch.no_grad():
    r2 = cd(xi.double())
    rec["conv_rel_err_vs_fp64"] = float((c(xi).double() - r2).norm() / r2.norm())
rec["gpu_ok"] = name == a.expect_gpu
print("BB2_PRECISION", json.dumps(rec), flush=True)
sys.exit(0 if rec["gpu_ok"] else 4)

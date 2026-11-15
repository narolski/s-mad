"""TT1 amendment H-new-5 (prereg.md section 9): do GB10 kernel settings reproduce the A100 logits on the five diagnostic
FFHQ genuine rows? A_s401, DGX stack. Settings: default; TF32 off (matmul + cuDNN); TF32 on (matmul + cuDNN);
math-only SDPA attention (flash and memory-efficient off); math-only + TF32 off; math-only + TF32 on. The input tensors
are those of diag_stack (bit-identical across stacks). Compared with the A100 logits in diag_a100.npz.
  python -I diag_kernels.py --data D --code C --net N --a100 diag_a100.npz --out OUT.json"""
import argparse
import json
import pathlib
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    for k in ("data", "code", "net", "a100", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--manifest", default="tt1_score.csv")
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    import common as C
    ref = np.load(a.a100)
    ids = ref["ids"].tolist()
    x = torch.from_numpy(ref["x"])                  # A100 input tensor (bit-identical to the DGX one, diag_stack)
    meta = json.load(open(pathlib.Path(a.net) / "meta.json"))
    model, _ = C.build_run_model(meta)
    tr = torch.load(pathlib.Path(a.net) / "last_trainable.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(tr, strict=False)
    model.to("cuda").eval()
    xs = x.to("cuda")

    def run(tf32, math_only):
        if tf32 is not None:
            torch.backends.cuda.matmul.allow_tf32 = tf32
            torch.backends.cudnn.allow_tf32 = tf32
        ctx = torch.nn.attention.sdpa_kernel([torch.nn.attention.SDPBackend.MATH]) if math_only else None
        with torch.no_grad():
            if ctx:
                with ctx:
                    lg = C.forward_logit(model, xs)[0].float().cpu().numpy()
            else:
                lg = C.forward_logit(model, xs)[0].float().cpu().numpy()
        return lg

    d0 = (torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32)
    res = dict(ids=ids, a100=ref["logit"].tolist(), torch=torch.__version__, defaults_tf32=list(d0), settings={})
    for name, tf32, mo in (("default", None, False), ("tf32_off", False, False), ("tf32_on", True, False),
                           ("math", None, False), ("math_tf32_off", False, True), ("math_tf32_on", True, True)):
        if name == "math":
            torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32 = d0
            mo = True
        lg = run(tf32, mo)
        dd = np.abs(lg - ref["logit"])
        res["settings"][name] = dict(logit=lg.tolist(), max_abs_vs_a100=float(dd.max()))
    best = min(v["max_abs_vs_a100"] for v in res["settings"].values())
    res["best_max_abs"] = best
    res["verdict"] = "falsified (no setting brings |delta| below 1e-3)" if best >= 1e-3 else "not falsified (a setting reaches |delta| < 1e-3)"
    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v["max_abs_vs_a100"] for k, v in res["settings"].items()}, indent=1), res["verdict"])


if __name__ == "__main__":
    main()

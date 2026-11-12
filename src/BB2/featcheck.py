"""BB2 platform check (pre-run review finding 5): the pooled, L2-normalised DINOv3 ViT-L/16 feature of 8 fixed training
images at initialisation (no LoRA, eval mode, fp32, TF32 off), through the unchanged loader (common.ImageItems, 224).
The 8 images: the first 8 unique paths of train_A.csv in sorted order (training images only).
  python -I featcheck.py --root PN1_TREE --out feats.npz [--ref ref.npz]
SMAD_DATA must point at the data root (as run.sh sets it) and HF_HOME at ROOT/hf. With --ref, prints the largest absolute
difference and exits 3 if it exceeds 1e-3 (the registered tolerance)."""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default=None)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.root) / "code" / "smadcvpr"))
    import torch
    import torch.nn.functional as F
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    rows = list(csv.DictReader(open(C.data_root() / "manifests" / "train_A.csv")))
    paths = sorted({r["path"] for r in rows})[:8]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    m, extra = C.build_model("a12_dinov3_vitl16_madation", 224, 0.0)
    m.to(dev).eval()
    x = torch.stack([C.ImageItems([(p, 0)], 224)[0][0] for p in paths]).to(dev)
    with torch.no_grad():
        f = F.normalize(m.net((x - m.mean) / m.std), dim=-1).float().cpu().numpy()
    np.savez(a.out, paths=np.array(paths), feat=f)
    rec = dict(device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", torch=torch.__version__,
               timm=__import__("timm").__version__, weights=extra["weights"], n=len(paths))
    rc = 0
    if a.ref:
        r = np.load(a.ref)
        assert list(r["paths"]) == paths, "different images"
        d = float(np.abs(r["feat"] - f).max())
        rec.update(max_abs_diff=d, tolerance=1e-3, ok=d <= 1e-3)
        rc = 0 if d <= 1e-3 else 3
    print("BB2_FEATCHECK", json.dumps(rec), flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()

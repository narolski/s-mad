"""PD1 landmark: frozen features, nothing written as an image.

Model and preprocessing: the alpha-field probe's (AF0) `build()` from src/AF0/feat.py, imported unchanged (timm,
offline Hugging Face cache, eval mode, the model's own transform at input size 224 (CLIP) or 512 (DINOv3), crop_pct 1,
bf16 autocast exactly as AF0). One forward pass gives
  cls  : the class token after the final norm (CLIP: the pooled pre-projection feature, 1,024-d)
  mean : the mean of the patch tokens after the final norm (prefix tokens dropped), 1,024-d
Images of any size are passed through the same transform (its own resize; SMDD renders are 256 px, their stored-small
copies 80 px); AF0's 512-only assert is not applied. Output OUT/feat/<backbone>/<list>.npz (ids, cls, mean float32),
written in resumable parts of --chunk images.

  python3 -I feat.py --backbone clip224 --list ar1 [--only-rung R2wm] [--limit 8] [--bs 16] [--workers 2]
"""
import argparse
import importlib.util
import json
import os
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402

AF0_FEAT = K.REPO / "src/AF0/feat.py"


def af0_build():
    spec = importlib.util.spec_from_file_location("af0_feat", AF0_FEAT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Items:
    def __init__(self, paths, tf):
        self.paths, self.tf = paths, tf

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        from PIL import Image
        return self.tf(Image.open(self.paths[i]).convert("RGB"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True, choices=("clip224", "dinov3_512"))
    ap.add_argument("--list", required=True)
    ap.add_argument("--only-rung", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunk", type=int, default=512)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import torch
    torch.set_num_threads(2)
    F = af0_build()
    model, tf, cfg = F.build(a.backbone)
    npt = model.num_prefix_tokens
    model.to("cuda")
    for lst in a.list.split(","):
        run_one(a, lst, model, tf, cfg, npt, torch)


def run_one(a, lst, model, tf, cfg, npt, torch):
    rr = K.rows(K.OUT / "lists" / f"{lst}.csv")
    if a.only_rung:
        rr = [r for r in rr if r["rung"] in a.only_rung.split(",")]
    rr = rr[: a.limit or None]
    for r in rr:
        assert not K.forbidden(r["path"]), r["path"]
    tag = lst + (f"_{a.only_rung.replace(',', '-')}" if a.only_rung else "") + (f"_limit{a.limit}" if a.limit else "")
    od = K.OUT / "feat" / a.backbone
    od.mkdir(parents=True, exist_ok=True)
    final = od / f"{tag}.npz"
    if final.exists():
        print("exists", final)
        return
    t0 = time.time()
    for c0 in range(0, len(rr), a.chunk):
        part = od / f"{tag}.part{c0:06d}.npz"
        if part.exists():
            continue
        sel = rr[c0:c0 + a.chunk]
        dl = torch.utils.data.DataLoader(Items([r["path"] for r in sel], tf), batch_size=a.bs, num_workers=a.workers)
        cls, mean = [], []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x in dl:
                t = model.forward_features(x.to("cuda", non_blocking=True)).float()
                cls.append(t[:, 0].cpu().numpy())
                mean.append(t[:, npt:].mean(1).cpu().numpy())
        np.savez(part, ids=np.array([r["id"] for r in sel]), cls=np.concatenate(cls), mean=np.concatenate(mean))
        el = time.time() - t0
        print(f"{tag}: {c0 + len(sel)}/{len(rr)} {(c0 + len(sel)) / el:.1f} img/s, max mem "
              f"{torch.cuda.max_memory_allocated() / 2**30:.1f} GB", flush=True)
    parts = sorted(od.glob(f"{tag}.part*.npz"))
    D = [np.load(p) for p in parts]
    ids = np.concatenate([d["ids"] for d in D])
    assert list(ids) == [r["id"] for r in rr], "part order mismatch"
    np.savez(final, ids=ids, cls=np.concatenate([d["cls"] for d in D]), mean=np.concatenate([d["mean"] for d in D]))
    json.dump(dict(backbone=a.backbone, list=lst, only_rung=a.only_rung, n=len(rr), prefix_tokens=npt,
                   data_config={k: list(v) if isinstance(v, tuple) else v for k, v in cfg.items()}, transform=str(tf),
                   af0_feat_py=str(AF0_FEAT), seconds=round(time.time() - t0, 1),
                   max_mem_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2)),
              open(od / f"{tag}.meta.json", "w"), indent=1)
    for p in parts:
        p.unlink()
    print("DONE", final, len(ids), flush=True)


if __name__ == "__main__":
    main()

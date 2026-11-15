"""Follow-ups (b) and (c) of the morph-free networks experiment (AD4), prereg Amendment 4, run inside one Athena GPU job.

  python fu_rescore.py blank --manifest M --root D --out-prefix blank     constant-colour blanking outside the fixed face
        ellipse (centre (256, 264), semi-axes 125 x 172 px) to (128, 128, 128), every row of M, lossless PNG at
        D/<out-prefix>/<path>; writes D/manifests/<stem>_blank.csv with the new paths (no other change to any pixel)
  python fu_rescore.py score --code C --nets N --manifests a.csv,b.csv --out O [--workers 7] [--limit 8]
        every network in N (one folder per network: meta.json + last_trainable.pt; or zero.json for the untrained one)
        rebuilt with common.build_run_model + the pack weights + its trained tensors, scored on each manifest with the
        ad4_score.py core (common.ImageItems at meta res, TTA = mean of sigmoid(image, h-flip)); O/<net>/scores_<stem>.npz
SMAD_DATA = the data root of the manifests. Prints FU_DONE at the end.
"""
import argparse
import csv
import json
import os
import pathlib
import random
import sys
import time

import numpy as np

CX, CY, AX, AY = 256, 264, 125, 172
GREY = 128
RECIPES = {"m3": dict(arch="a12_clip_vitb16_madation", res=224, drop_path=0.0, ft="lora", lora_r=2, lora_targets="qv",
                      lora_alpha=4.0, lora_dropout=0.4, lora_rs=True, lora_train_norms=False)}   # = ad4_score.RECIPES


def blank(a):
    from PIL import Image
    root = pathlib.Path(a.root)
    rows = list(csv.DictReader(open(a.manifest)))
    yy, xx = np.mgrid[0:512, 0:512]
    out_mask = ((xx - CX) / AX) ** 2 + ((yy - CY) / AY) ** 2 > 1.0
    n_other = 0
    for k, r in enumerate(rows[: a.limit or None]):
        src, dst = root / r["path"], root / a.out_prefix / r["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = np.array(Image.open(src).convert("RGB"))
        if im.shape[:2] != (512, 512):
            n_other += 1                       # not in the canonical frame: blanked with the same mask only if 512
            raise SystemExit(f"FU blank: {src} is {im.shape}, not 512 x 512")
        im[out_mask] = GREY
        Image.fromarray(im).save(dst, format="PNG", compress_level=1)
        r["path"] = f"{a.out_prefix}/{r['path']}"
        if k % 5000 == 0:
            print(f"FU blank {k}/{len(rows)}", flush=True)
    mp = root / "manifests" / (pathlib.Path(a.manifest).stem + "_blank.csv")
    with open(mp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows[: a.limit or None])
    print(f"FU blank done {mp} rows {len(rows[: a.limit or None])}", flush=True)


def score(a):
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    out = pathlib.Path(a.out)
    from PIL import Image
    yy, xx = np.mgrid[0:512, 0:512]
    outside = ((xx - CX) / AX) ** 2 + ((yy - CY) / AY) ** 2 > 1.0

    class BlankItems(C.ImageItems):
        """ImageItems with the grey fill outside the face ellipse applied in memory before the unchanged load step
        (common.ImageItems.load: convert RGB, bilinear resize to res); equal to a lossless PNG of the blanked image."""

        def load(self, p):
            arr = np.array(Image.open(self.root / p).convert("RGB"))
            if arr.shape[:2] != (512, 512):
                raise SystemExit(f"FU blank: {p} is {arr.shape}, not 512 x 512")
            arr[outside] = GREY
            img = Image.fromarray(arr)
            w0 = img.size[0]
            if img.size != (self.res, self.res):
                img = img.resize((self.res, self.res), Image.BILINEAR)
            return img, w0
    for nd in sorted(pathlib.Path(a.nets).iterdir()):
        t0 = time.time()
        if (nd / "zero.json").is_file():
            z = json.load(open(nd / "zero.json"))
            meta = dict(RECIPES[z["recipe"]], seed=z["seed"], steps=0)
            random.seed(z["seed"]); np.random.seed(z["seed"]); torch.manual_seed(z["seed"])
            torch.cuda.manual_seed_all(z["seed"])
            model, _ = C.build_run_model(meta)
            info = {"network": "zero-step", "seed": z["seed"]}
        else:
            meta = json.load(open(nd / "meta.json"))
            model, _ = C.build_run_model(meta)
            sd = torch.load(nd / "last_trainable.pt", map_location="cpu", weights_only=True)
            trn = {n for n, p in model.named_parameters() if p.requires_grad}
            if set(sd) != trn:
                raise SystemExit(f"FU {nd.name}: trained tensors {len(sd)} do not match the trainable set {len(trn)}")
            missing, unexpected = model.load_state_dict(sd, strict=False)
            if unexpected or set(missing) & trn:
                raise SystemExit(f"FU {nd.name}: load_state_dict unexpected {unexpected}")
            info = {"network": "trained", "seed": meta["seed"], "n_trained_tensors": len(sd)}
        model.to(dev).eval()
        (out / nd.name).mkdir(parents=True, exist_ok=True)
        for tok in a.manifests.split(","):
            mf, _, mode = tok.partition(":")          # "name.csv:blank" = in-memory blanking (Amendment 4b)
            rows = C.read_manifest(mf)
            if a.limit:
                rows = rows[::max(1, len(rows) // a.limit)][:a.limit]
            Items = BlankItems if mode == "blank" else C.ImageItems
            dl = DataLoader(Items([(r["path"], int(r["label"])) for r in rows], meta["res"]),
                            batch_size=64, num_workers=a.workers)
            s_tta, s_one = [], []
            with torch.no_grad():
                for x, _ in dl:
                    x = x.to(dev, non_blocking=True)
                    p0 = torch.sigmoid(C.forward_logit(model, x)[0].float())
                    p1 = torch.sigmoid(C.forward_logit(model, torch.flip(x, dims=[3]))[0].float())
                    s_one += p0.cpu().tolist()
                    s_tta += ((p0 + p1) / 2).cpu().tolist()
            stem = pathlib.Path(mf).stem + ("_blank" if mode == "blank" else "")
            np.savez(out / nd.name / f"scores_{stem}.npz", id=np.array([r["id"] for r in rows]),
                     score=np.array(s_tta, np.float32), score_noTTA=np.array(s_one, np.float32), limit=a.limit,
                     device=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", torch=torch.__version__,
                     info=json.dumps(info))
        print(f"FU scored {nd.name} in {time.time() - t0:.0f} s", flush=True)
    print("FU_DONE", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("blank")
    b.add_argument("--manifest", required=True)
    b.add_argument("--root", required=True)
    b.add_argument("--out-prefix", default="blank")
    b.add_argument("--limit", type=int, default=0)
    s = sp.add_parser("score")
    s.add_argument("--code", required=True)
    s.add_argument("--nets", required=True)
    s.add_argument("--manifests", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--workers", type=int, default=7)
    s.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    blank(a) if a.cmd == "blank" else score(a)


if __name__ == "__main__":
    main()

"""ID0 DiffAE semantic code z_sem (encoder only; no sampling, no decoding, nothing written as an image).

Pinned DiffAE repository (commit 00c57d3f..., clean) and FFHQ256 autoencoder checkpoint (sha 9bd2ba9e...), loaded as
in the registered A43 generator (a43_gen.py: LitModel(ffhq256_autoenc()), torch.load(weights_only=True) with the
Lightning callback entry mapped to an inert placeholder, state_dict only). z_sem = LitModel.encode(x) =
ema_model.encoder(x), float32. Input transform = the repository's own ImageDataset transform (Resize 256, CenterCrop
256, ToTensor, Normalize 0.5), taken from an ImageDataset instance unchanged.

  /mnt/t7/thirdparty/diffae_venv/bin/python -I feat_diffae.py [--limit 8] [--tag test] [--bs 32]
Output /mnt/t7/smad_next/ID0/feat/diffae<_tag>.npz (keys, feat, found).
"""
import argparse
import csv
import json
import pathlib
import subprocess
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path("/mnt/t7/smad_next/ID0")
BASE = pathlib.Path("/mnt/t7/thirdparty/diffae_00c57d3f626f28bf9ed8aff58d90baab25de3af4")
REPO = BASE / "repo"
CKPT = BASE / "checkpoints_download/ffhq256_autoenc/last.ckpt"
CKPT_SHA = "9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca"
REPO_COMMIT = "00c57d3f626f28bf9ed8aff58d90baab25de3af4"


class _InertCallbackState:
    def __init__(self, *a, **k):
        self._a, self._k = a, k


def fsha(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--max-tier", type=int, default=3)
    ap.add_argument("--merge-only", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    items = [(r["key"], r["path"]) for r in csv.DictReader(open(OUT / "fit.csv"))]
    items += [(r["key"], r["path"]) for r in csv.DictReader(open(OUT / "items.csv"))]
    if a.limit:
        seen, kept = {}, []
        for k, p in items:
            g = k.split("|")[0] + "|" + k.split("|")[1]
            seen[g] = seen.get(g, 0) + 1
            if seen[g] <= 1 and len(kept) < a.limit:
                kept.append((k, p))
        items = kept
    sys.path.insert(0, str(HERE))
    import id0_common as C
    items = C.ordered(items, "diffae", a.max_tier)
    print(f"items after tier order (max tier {a.max_tier}): {len(items)}", flush=True)
    for _, p in items:
        assert not forbidden(p), p
    sfx = f"_{a.tag}" if a.tag else ""
    fd = OUT / "feat"
    fd.mkdir(parents=True, exist_ok=True)
    if a.merge_only:
        merge(fd, sfx, [k for k, _ in items])
        return
    gr = lambda *c: subprocess.run(["git", "-C", str(REPO), *c], capture_output=True, text=True).stdout  # noqa: E731
    commit, dirty = gr("rev-parse", "HEAD").strip(), gr("status", "--porcelain").strip()
    if commit != REPO_COMMIT or dirty:
        sys.exit(f"DiffAE repo HEAD {commit!r} dirty={bool(dirty)} is not the clean pinned commit")
    t0 = time.time()
    got = fsha(CKPT)
    if got != CKPT_SHA:
        sys.exit(f"checkpoint sha {got} != {CKPT_SHA}")
    sys.path.insert(0, str(REPO))
    import torch
    from PIL import Image
    from templates import ffhq256_autoenc, LitModel  # pinned repository
    from dataset import ImageDataset
    conf = ffhq256_autoenc()
    model = LitModel(conf)
    torch.serialization.add_safe_globals(
        [(_InertCallbackState, "pytorch_lightning.callbacks.model_checkpoint.ModelCheckpoint")])
    state = torch.load(str(CKPT), map_location="cpu", weights_only=True)
    res = model.load_state_dict(state["state_dict"], strict=False)
    del state
    if any(k.startswith("ema_model.") for k in res.missing_keys):
        sys.exit("ema_model keys missing")
    enc = model.ema_model.encoder.eval().to("cuda")
    del model
    tf = ImageDataset(str(HERE), image_size=conf.img_size, exts=["png"], do_augment=False, sort_names=True,
                      has_subdir=False).transform
    keys = [k for k, _ in items]
    ds = DS([p for _, p in items], tf)
    for c0 in range(0, len(items), a.chunk):
        part = fd / f"partdae{sfx}_{c0:06d}.npz"
        if part.exists():
            continue
        sel = list(range(c0, min(c0 + a.chunk, len(items))))
        sub = torch.utils.data.Subset(ds, sel)
        dl = torch.utils.data.DataLoader(sub, batch_size=a.bs, num_workers=a.workers)
        F = []
        with torch.no_grad():
            for x in dl:
                F.append(model_encode(enc, x.to("cuda")).float().cpu().numpy())
        np.savez(part, idx=np.array(sel), feat=np.concatenate(F))
        print(f"{time.strftime('%T')} part {c0} done ({len(sel)}), {time.time() - t0:.0f} s", flush=True)
    Fm = merge(fd, sfx, keys)
    info = dict(model="DiffAE ffhq256_autoenc ema encoder", ckpt_sha256=got, repo_commit=commit, n=len(keys),
                seconds=round(time.time() - t0, 1), torch=torch.__version__, finite=bool(np.isfinite(Fm).all()),
                load_missing=len(res.missing_keys), load_unexpected=len(res.unexpected_keys))
    json.dump(info, open(OUT / "feat" / f"diffae{sfx}.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


class DS:
    def __init__(self, paths, tf):
        self.paths, self.tf = paths, tf

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        from PIL import Image
        return self.tf(Image.open(self.paths[i]).convert("RGB"))


def merge(fd, sfx, keys):
    F = np.zeros((len(keys), 512), np.float32)
    done = np.zeros(len(keys), bool)
    for p in sorted(fd.glob(f"partdae{sfx}_*.npz")):
        z = np.load(p)
        F[z["idx"]] = z["feat"]
        done[z["idx"]] = True
    np.savez(fd / f"diffae{sfx}.npz", keys=np.array(keys)[done], feat=F[done], found=np.ones(int(done.sum()), bool))
    print(f"merged diffae: {int(done.sum())} of {len(keys)} rows", flush=True)
    return F[done]


def model_encode(enc, x):
    """LitModel.encode(x) is self.ema_model.encoder.forward(x) (experiment.py l.141-145); called on the encoder."""
    return enc.forward(x)


if __name__ == "__main__":
    main()

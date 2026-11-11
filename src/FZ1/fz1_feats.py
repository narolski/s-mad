"""FZ1 frozen-feature extraction (P2, P3). Images through the existing loader smadcvpr/common.ImageItems(res=224)
(its PIL bilinear resize is the only resize). No training, no gradients.

  fz1_feats.py --backbone clip_mad|clip_native|dinov3|dinov2 --set a43|sg3|eval|smdd [--flip] [--smoke] [--bs 64]
  fz1_feats.py --check        CLIP tensors vs the released FE ViT-L/14 encoder; FE head on our features vs A43 scores

Writes /mnt/t7/smad_next/FZ1/feats/<backbone>/<set>[_flip].npz (id, feat float32, meta). Third-party weights:
torch.load(weights_only=True) or safetensors only; HF offline.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_feats.py ...
"""
import argparse, csv, json, os, pathlib, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
import fz1_common as K
from common import ImageItems  # noqa: E402  (the existing loader; PIL bilinear resize to res)

HUB = pathlib.Path.home() / ".cache/huggingface/hub"
CLIP_BIN = next((HUB / "models--timm--vit_large_patch14_clip_224.openai/snapshots").glob("*/pytorch_model.bin"))
DINO2 = next((HUB / "models--timm--vit_large_patch14_dinov2.lvd142m/snapshots").glob("*/model.safetensors"))
DINO3 = next((HUB / "models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots").glob("*/model.safetensors"))
FE_REL = pathlib.Path("/mnt/t7/smad_next/FZ1/release/madation_fe_vitl14_model.safetensors")  # copy of A12REL/madation_fe_vitl14/model.safetensors (sha 74dd7fbc...) from madation_official.tar
CLIP_MEAN, CLIP_STD = (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)


def build(backbone):
    import timm
    if backbone.startswith("clip"):
        m = timm.create_model("vit_large_patch14_clip_quickgelu_224", pretrained=False, num_classes=768, img_size=224)
        from timm.models.vision_transformer import checkpoint_filter_fn
        sd = checkpoint_filter_fn(torch.load(CLIP_BIN, map_location="cpu", weights_only=True), m)  # OpenAI layout -> timm
        missing, unexpected = m.load_state_dict(sd, strict=False)
        assert not unexpected and set(missing) <= {"head.bias"}, (str(missing)[:300], str(unexpected)[:300])
        if "head.bias" in missing:
            torch.nn.init.zeros_(m.head.bias)
        if backbone == "clip_mad":
            norm = dict(bgr=True, mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
        else:
            norm = dict(bgr=False, mean=CLIP_MEAN, std=CLIP_STD)
        info = dict(timm="vit_large_patch14_clip_quickgelu_224", weights=str(CLIP_BIN), missing=list(missing))
    elif backbone == "dinov2":
        m = timm.create_model("vit_large_patch14_dinov2.lvd142m", pretrained=True, num_classes=0, img_size=224,
                              pretrained_cfg_overlay=dict(file=str(DINO2)))
        c = m.pretrained_cfg
        norm = dict(bgr=False, mean=tuple(c["mean"]), std=tuple(c["std"]))
        info = dict(timm="vit_large_patch14_dinov2.lvd142m", weights=str(DINO2), global_pool=str(getattr(m, "global_pool", "")))
    elif backbone == "dinov3":
        m = timm.create_model("vit_large_patch16_dinov3.lvd1689m", pretrained=True, num_classes=0, img_size=224,
                              pretrained_cfg_overlay=dict(file=str(DINO3)))
        c = m.pretrained_cfg
        norm = dict(bgr=False, mean=tuple(c["mean"]), std=tuple(c["std"]))
        info = dict(timm="vit_large_patch16_dinov3.lvd1689m", weights=str(DINO3), global_pool=str(getattr(m, "global_pool", "")))
    else:
        raise SystemExit(f"unknown backbone {backbone}")
    info.update(norm=norm, timm_version=timm.__version__)
    return m.eval(), norm, info


def prep(x, norm):
    if norm["bgr"]:
        x = x[:, [2, 1, 0]]
    mean = torch.tensor(norm["mean"], device=x.device).view(1, 3, 1, 1)
    std = torch.tensor(norm["std"], device=x.device).view(1, 3, 1, 1)
    return (x - mean) / std


def items_for(set_name):
    """[(id, absolute path)] of a set."""
    if set_name == "a43":
        return [(r["id"], str(K.a43_path(r))) for r in K.a43_rows()]
    if set_name == "sg3":
        R4, R2, RX = K.sg3_rows()
        return [(r["id"], str(K.H3 / r["path"])) for r in R4 + R2] + [(r["id"], str(K.A37 / r["path"])) for r in RX]
    if set_name == "eval":
        import fz1_eval as E
        ctx = E.Ctx(smoke=True)
        byid = ctx.ev_by_id
        return [(i, str(K.EVAL_ROOT / byid[i]["path"])) for i in ctx.eval_ids()]
    if set_name == "smdd":
        rows = [r for r in csv.DictReader(open(K.TRAIN)) if r["source"] == "smdd"]
        assert len(rows) == 40000, len(rows)
        return [(r["path"], str(K.EVAL_ROOT / r["path"])) for r in rows]
    raise SystemExit(f"unknown set {set_name}")


@torch.no_grad()
def extract(model, norm, items, flip, bs, dev, workers=4):
    ds = ImageItems([(p, 0) for _, p in items], res=224, root="/")
    dl = torch.utils.data.DataLoader(ds, batch_size=bs, shuffle=False, num_workers=workers, pin_memory=True)
    out, outf = [], []
    t0 = time.time()
    for k, (x, _) in enumerate(dl):
        x = x.to(dev, non_blocking=True)
        if flip == "both":                         # one decode, orig and flipped features
            out.append(model(prep(x, norm)).float().cpu())
            outf.append(model(prep(torch.flip(x, dims=[3]), norm)).float().cpu())
        else:
            if flip:
                x = torch.flip(x, dims=[3])
            out.append(model(prep(x, norm)).float().cpu())
        if k % 10 == 0:
            print(f"  batch {k}/{len(dl)} {time.time() - t0:.0f}s", flush=True)
    if flip == "both":
        return torch.cat(out).numpy(), torch.cat(outf).numpy()
    return torch.cat(out).numpy()


def check(dev):
    from safetensors.torch import load_file
    m, norm, info = build("clip_mad")
    if "--rgb" in sys.argv:            # calibration control: a deliberately wrong channel order
        norm = dict(norm, bgr=False)
        info = dict(info, norm=norm, control="wrong channel order (RGB)")
    rel = load_file(str(FE_REL))
    sd = m.state_dict()
    diffs = {}
    for k, v in sd.items():
        rk = "net." + k
        assert rk in rel, rk
        diffs[k] = float((rel[rk].float() - v.float()).abs().max())
    extra = [k for k in rel if k.startswith("net.") and k[4:] not in sd]
    mx = max(diffs.values())
    print(f"CLIP vs FE release encoder: {len(diffs)} tensors, max |d| {mx:.3e}; worst {max(diffs, key=diffs.get)}; extra {extra}")
    W, b = rel["head.weight"].float(), rel["head.bias"].float()
    rows = K.a43_rows()
    g = K.a43_groups(rows)
    z = np.load(K.A43 / "a43_out/a43/madation_fe_vitl14/rel/scores_a43.npz", allow_pickle=False)
    ref = z["score_noTTA"].astype(float)
    sel = [i for k in ("A", "B", "B20", "C", "C20", "D", "D20", "E", "R0") for i in g[k][:8]]
    m = m.to(dev)
    f = extract(m, norm, [(rows[i]["id"], str(K.a43_path(rows[i]))) for i in sel], False, 32, dev, workers=2)
    zz = F.normalize(torch.from_numpy(f), dim=-1) @ W.t() + b
    s = torch.sigmoid(zz[:, 0] - zz[:, 1]).numpy()
    d = np.abs(s - ref[sel])
    lref = z["logit_noTTA"].astype(float)[sel]
    dl = np.abs((zz[:, 0] - zz[:, 1]).numpy() - lref)
    res = dict(logit_max_abs=float(dl.max()), logit_mean_abs=float(dl.mean()), logit_ref_absmean=float(np.abs(lref).mean()),
               score_corr=float(np.corrcoef(s, ref[sel])[0, 1]), encoder_tensors=len(diffs), encoder_max_abs=mx, extra_release_keys=extra, n_images=len(sel),
               score_max_abs=float(d.max()), score_mean_abs=float(d.mean()), tf32=torch.backends.cuda.matmul.allow_tf32,
               passes=bool(d.max() <= 2e-3), info=info)
    print(json.dumps(res, indent=1))
    tag = ("tf32" if torch.backends.cuda.matmul.allow_tf32 else "fp32") + ("_rgbcontrol" if "--rgb" in sys.argv else "")
    json.dump(res, open(K.OUT / f"check_clip_vs_release_{tag}.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone")
    ap.add_argument("--set")
    ap.add_argument("--flip", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--no-tf32", action="store_true")
    ap.add_argument("--rgb", action="store_true")
    ap.add_argument("--part", default=None, help="k/n: contiguous k-th of n chunks (1-based), '+flip' sets only")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    tf32 = "--no-tf32" not in sys.argv
    torch.backends.cuda.matmul.allow_tf32 = tf32      # A43 scoring ran with tf32_matmul / tf32_cudnn True
    torch.backends.cudnn.allow_tf32 = tf32
    dev = "cuda"
    if a.check:
        return check(dev)
    model, norm, info = build(a.backbone)
    model = model.to(dev)
    for spec in a.set.split(","):                      # e.g. a43,sg3,eval,smdd,smdd_flip,smdd+flip (one pass, both files)
        if spec.endswith("+flip"):
            set_name = spec[:-5]
            tag = f"_part{a.part.replace('/', 'of')}" if a.part else ""
            o1 = K.BIG / "feats" / a.backbone / f"{set_name}{tag}{'_smoke' if a.smoke else ''}.npz"
            o2 = K.BIG / "feats" / a.backbone / f"{set_name}_flip{tag}{'_smoke' if a.smoke else ''}.npz"
            if o1.exists() and o2.exists() and not a.smoke:
                print("exists, skipped:", o1, o2)
                continue
            items = items_for(set_name)
            if a.part:
                k, n = (int(x) for x in a.part.split("/"))
                lo, hi = (k - 1) * len(items) // n, k * len(items) // n
                items = items[lo:hi]
                print(f"part {k}/{n}: items {lo}:{hi}", flush=True)
            if a.smoke:
                items = items[:8]
            t0 = time.time()
            f1, f2 = extract(model, norm, items, "both", a.bs, dev, workers=a.workers)
            dt = time.time() - t0
            print(f"{a.backbone} {set_name} orig+flip: {f1.shape} in {dt:.0f}s; max GPU mem {torch.cuda.max_memory_allocated() / 2**30:.2f} GB", flush=True)
            o1.parent.mkdir(parents=True, exist_ok=True)
            for o, f, fl in ((o1, f1, False), (o2, f2, True)):
                np.savez(o, id=np.array([i for i, _ in items]), feat=f.astype(np.float32),
                         meta=json.dumps(dict(info, set=set_name, flip=fl, n=len(items), seconds=dt, tf32=bool(torch.backends.cuda.matmul.allow_tf32))))
                print("wrote", o, flush=True)
            continue
        set_name, flip = (spec[:-5], True) if spec.endswith("_flip") else (spec, a.flip)
        out = K.BIG / "feats" / a.backbone / (f"{set_name}{'_flip' if flip else ''}{'_smoke' if a.smoke else ''}.npz")
        if out.exists() and not a.smoke:
            print("exists, skipped:", out)
            continue
        items = items_for(set_name)
        if a.smoke:
            items = items[:8]
        t0 = time.time()
        f = extract(model, norm, items, flip, a.bs, dev)
        dt = time.time() - t0
        print(f"{a.backbone} {set_name} flip={flip}: {f.shape} in {dt:.0f}s; max GPU mem {torch.cuda.max_memory_allocated() / 2**30:.2f} GB", flush=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(out, id=np.array([i for i, _ in items]), feat=f.astype(np.float32),
                 meta=json.dumps(dict(info, set=set_name, flip=flip, n=len(items), seconds=dt, tf32=bool(torch.backends.cuda.matmul.allow_tf32))))
        print("wrote", out, flush=True)


if __name__ == "__main__":
    main()

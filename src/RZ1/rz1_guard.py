"""RZ1 first-step guard, run inside every fit job before training (and after it on meta.json). Exits non-zero unless:
  pre:  the model built at RES has a position embedding of 1 + (RES/16)^2 tokens (197 at 224, 1025 at 512), the 512
        embedding equals timm's bicubic resample of the pretrained 224 one (resample_abs_pos_embed) within 1e-5, and a
        training item through the RZ1 transform is a 3 x RES x RES tensor;
  post: meta.json holds res RES, bs BS, accum ACCUM, steps STEPS and the run's rz1_transform.json the spec SPEC.
  python rz1_guard.py pre  CODE ARCH RES SPEC MANIFEST
  python rz1_guard.py post RUN RES BS ACCUM STEPS SPEC"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def die(m):
    print("RZ1 GUARD FAIL:", m, flush=True)
    sys.exit(1)


def pre(code, arch, res, spec, manifest):
    import os
    os.environ["RZ1_TRANSFORM"] = spec
    import rz1_patch
    rz1_patch.apply(code)
    import torch
    import common as C
    res = int(res)
    model, _ = C.build_model(arch, res)
    pe = [p for n, p in model.named_parameters() if n.endswith("pos_embed")]
    if len(pe) != 1:
        die(f"{len(pe)} pos_embed tensors")
    ntok = pe[0].shape[1]
    if ntok != 1 + (res // 16) ** 2:
        die(f"pos_embed tokens {ntok} at res {res}")
    if res != 224:
        from timm.layers import resample_abs_pos_embed
        import archs_a12 as AR
        keep, AR.CLIP_RES = AR.CLIP_RES, 224          # the 224 reference tower (the pack's guard accepts 224 only)
        ref, _ = C.build_model(arch, 224)
        AR.CLIP_RES = keep
        p224 = [p for n, p in ref.named_parameters() if n.endswith("pos_embed")][0].detach()
        want = resample_abs_pos_embed(p224, new_size=(res // 16, res // 16), num_prefix_tokens=1)
        d = float((want - pe[0].detach()).abs().max())
        if d > 1e-5:
            die(f"pos_embed differs from the bicubic resample by {d}")
        print(f"RZ1 GUARD pos_embed = resample of the 224 embedding (max diff {d:.2e})")
    rows = C.read_manifest(manifest)[:4]
    ds = C.ImageItems([(r["path"], int(r["label"])) for r in rows], res, aug="flip")
    for i in range(len(rows)):
        x, _ = ds[i]
        if tuple(x.shape) != (3, res, res):
            die(f"item shape {tuple(x.shape)}")
    with torch.no_grad():
        model.eval()
        out = C.forward_logit(model, torch.stack([ds[i][0] for i in range(2)]))[0]
    print(f"RZ1 GUARD pre ok: arch {arch} res {res} tokens {ntok} spec {spec} item {tuple(x.shape)} logits {out.shape}",
          flush=True)


def post(run, res, bs, accum, steps, spec):
    m = json.load(open(pathlib.Path(run) / "meta.json"))
    t = json.load(open(pathlib.Path(run) / "rz1_transform.json"))
    want = dict(res=int(res), bs=int(bs), accum=int(accum), steps=int(steps))
    got = {k: m.get(k) for k in want}
    if got.get("accum") is None:
        got["accum"] = 1
    if got != want:
        die(f"meta {got} != {want}")
    if t["spec"] != spec or int(t["res"]) != int(res):
        die(f"rz1_transform {t} != {spec} {res}")
    print(f"RZ1 GUARD post ok: {want} spec {spec}", flush=True)


if __name__ == "__main__":
    (pre if sys.argv[1] == "pre" else post)(*sys.argv[2:])

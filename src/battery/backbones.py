"""Shared test battery (BATTERY): pluggable network loaders.

A loader turns a trained-network directory into (model in eval mode on the device, meta, the smadcvpr `common` module,
provenance). Both registered backbones are built by the training code's own `common.build_run_model(meta)` (as
src/PN1/rescore.py and pn1_score.py do); what differs is the code tree (the BB2 overlay replaces archs_a12.py and adds the
DINOv3 weights) and the reference network of the platform gate.

Network directory: meta.json plus last_trainable.pt (LoRA and head; strict on every trained tensor, as rescore.py) or
last.pt (the full state dict of train.py; strict, as pn1_score.py).

To add a backbone: add an entry to LOADERS with its architecture names and the sha256 of the code files that define it,
and pin a reference network for each platform in platform.py (a backbone without a reference cannot pass the gate)."""
import hashlib
import json
import pathlib
import sys

LOADERS = {
    "clip_vitb16_lora": dict(
        archs={"a12_clip_vitb16_madation"},
        code_pins={"smadcvpr/common.py": "b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8"},
        base_weights="a12/vit_base_patch16_clip_224.openai.safetensors",
        base_weights_sha256="4b8699299b1e8997753c64b052ba32031449d5d853f55a039148560ee02b820f",
        gate_reference=True),
    "dinov3_vitl16_lora": dict(
        archs={"a12_dinov3_vitl16_madation"},
        code_pins={"smadcvpr/common.py": "b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8"},
        # archs_a12.py comes from the BB2 overlay (bb2_overlay.tar); its sha256 is recorded, and must be pinned here
        # together with a DINOv3 reference network in platform.py before this loader is used for a read.
        base_weights=None, base_weights_sha256=None,
        gate_reference=False),
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load(name, netdir, code, device, hf_home=None):
    import torch
    spec = LOADERS[name]
    code = pathlib.Path(code)
    prov = dict(backbone=name, code=str(code))
    for rel, want in spec["code_pins"].items():
        got = sha(code / rel)
        prov[rel] = got
        if got != want:
            raise RuntimeError(f"BATTERY: {code / rel} off its pin ({got[:16]} != {want[:16]})")
    prov["smadcvpr/archs_a12.py"] = sha(code / "smadcvpr" / "archs_a12.py") if (code / "smadcvpr" / "archs_a12.py").exists() else None
    if hf_home and spec.get("base_weights"):
        bw = pathlib.Path(hf_home) / spec["base_weights"]
        prov["base_weights_sha256"] = sha(bw) if bw.exists() else "missing"
        if bw.exists() and prov["base_weights_sha256"] != spec["base_weights_sha256"]:
            raise RuntimeError(f"BATTERY: base weights {bw} off their pin")
    d = str(code / "smadcvpr")
    if d not in sys.path:
        sys.path.insert(0, d)
    import common as C
    netdir = pathlib.Path(netdir)
    meta = json.load(open(netdir / "meta.json"))
    if meta["arch"] not in spec["archs"]:
        raise RuntimeError(f"BATTERY: arch {meta['arch']} is not a {name} architecture ({sorted(spec['archs'])})")
    model, _ = C.build_run_model(meta)
    if (netdir / "last_trainable.pt").exists():                      # rescore.py semantics
        f = netdir / "last_trainable.pt"
        tr = torch.load(f, map_location="cpu", weights_only=True)
        names = {n for n, p in model.named_parameters() if p.requires_grad}
        assert set(tr) == names, (len(tr), len(names))
        missing, unexpected = model.load_state_dict(tr, strict=False)
        assert not unexpected
        trainable = tr
    else:                                                           # pn1_score.py semantics (full last.pt)
        f = netdir / "last.pt"
        sd = torch.load(f, map_location="cpu", weights_only=True)
        model.load_state_dict(sd)
        trn = {n for n, p in model.named_parameters() if p.requires_grad}
        trainable = {k: v for k, v in sd.items() if k in trn}
    prov.update(weights_file=str(f), weights_sha256=sha(f), meta_sha256=sha(netdir / "meta.json"), arch=meta["arch"],
                res=meta["res"], seed=meta.get("seed"), steps=meta.get("steps"))
    model.to(device).eval()
    return model, meta, C, trainable, prov

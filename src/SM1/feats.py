"""SM1 Part 3 frozen features: OpenAI CLIP ViT-L/14 at 224, the MADation FE release's feature.

Tower: timm vit_large_patch14_clip_quickgelu_224 with the cached timm/vit_large_patch14_clip_224.openai weights
(offline; timm's note: "natively QuickGELU, use quickgelu model variant"); its head is CLIP's projection, so
net(x) = ln_post(class token) @ proj (768-d); feature = F.normalize(net(x)), exactly what the FE release header reads
(a36_madation.MADationOfficial.forward). Input = the FE release's own convention: common.ImageItems at 224 (the
loader's PIL bilinear resize of the whole image; no new resampling code) -> a12_released.adapt_input (BGR,
(x - 0.5) / 0.5). TF32 matmuls, no TTA.

  python3 -I feats.py check            tower == FE ViT-L/14 release tower; FE header on 8 eval.csv frames vs A12REL
  python3 -I feats.py run --list L.csv --name NAME [--limit 8] [--bs 64]
-> OUT/feat/<NAME>.npz (id, path, feat float32 (n, 768))
"""
import argparse
import csv
import json
import os
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FE_L14 = pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                      "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors")
A12REL_FE = K.MC / "smadcvpr_runs/A12_scored/A12REL/madation_fe_vitl14/scores_eval.npz"


def setup():
    os.environ["HF_HUB_OFFLINE"] = "1"
    for p in (K.MC, K.W46 / "smadcvpr"):
        sys.path.insert(0, str(p))
    import torch
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C
    import timm
    net = timm.create_model("vit_large_patch14_clip_quickgelu_224.openai", pretrained=True).eval()
    return torch, C, R, net


def loader(C, torch, paths, root="/", bs=64, workers=5):
    return torch.utils.data.DataLoader(C.ImageItems([(p, 0) for p in paths], 224, root=root), batch_size=bs,
                                       num_workers=workers)


def extract(torch, R, net, dl, spec):
    import torch.nn.functional as F
    out, n, t0 = [], 0, time.time()
    with torch.no_grad():
        for x, _ in dl:
            x = R.adapt_input(x.to("cuda", non_blocking=True), spec)
            out.append(F.normalize(net(x).float(), dim=-1).cpu().numpy())
            n += len(x)
            if len(out) % 20 == 0:
                print(f"PROGRESS {n} {time.time() - t0:.0f}s", flush=True)
    return np.concatenate(out).astype(np.float32)


def check():
    torch, C, R, net = setup()
    torch.backends.cuda.matmul.allow_tf32 = True
    spec = R.RELEASES["madation_fe_vitl14"]
    assert K.sha(FE_L14) == "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9"
    fe = R.build_release(spec)
    fe.load_state_dict(R.extract_state(R.load_release(FE_L14), spec), strict=True)
    a, b = net.state_dict(), fe.net.state_dict()
    assert set(a) == set(b), (set(a) ^ set(b))
    wdiff = max(float((a[k].float() - b[k].float()).abs().max()) for k in a)
    rows = [r for r in csv.DictReader(open(K.MC / "smadcvpr_data/manifests/eval.csv"))
            if r["set"] == "frllm" and r["variant"] == "orig"]
    pick = rows[::max(1, len(rows) // 8)][:8]
    net.to("cuda")
    feat = extract(torch, R, net, loader(C, torch, [r["path"] for r in pick], root=K.MC / "smadcvpr_data", bs=8,
                                         workers=2), spec)
    head = fe.head.cpu().float()
    with torch.no_grad():
        z = R.head_logit(head(torch.from_numpy(feat)), 2, 0)
    ours = torch.sigmoid(z).numpy()
    ref = np.load(A12REL_FE, allow_pickle=False)
    pos = {str(i): j for j, i in enumerate(ref["id"])}
    refv = np.array([ref["score_noTTA"][pos[r["id"]]] for r in pick])
    res = dict(tower_vs_fe_release_max_abs_weight_diff=wdiff, n=len(pick), ids=[r["id"] for r in pick],
               fe_header_on_our_features=[round(float(v), 6) for v in ours],
               a12rel_fe_vitl14_score_noTTA=[round(float(v), 6) for v in refv],
               max_abs_score_diff=float(np.abs(ours - refv).max()))
    json.dump(res, open(K.RES / "feat_check.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


def run(a):
    torch, C, R, net = setup()
    torch.backends.cuda.matmul.allow_tf32 = True
    spec = R.RELEASES["madation_fe_vitl14"]
    rows = list(csv.DictReader(open(a.list)))[: a.limit or None]
    for r in rows:
        assert not K.forbidden(r["path"])
    tag = a.name + (f"_limit{a.limit}" if a.limit else "")
    fo = K.OUT / "feat" / f"{tag}.npz"
    fo.parent.mkdir(parents=True, exist_ok=True)
    if fo.exists():
        print("exists", fo)
        return
    net.to("cuda")
    t0 = time.time()
    F_ = extract(torch, R, net, loader(C, torch, [r["path"] for r in rows], bs=a.bs, workers=a.workers), spec)
    dt = time.time() - t0
    np.savez(fo, id=np.array([r["id"] for r in rows]), path=np.array([r["path"] for r in rows]), feat=F_)
    mem = torch.cuda.max_memory_allocated() / 2 ** 30
    log = dict(name=tag, n=len(rows), seconds=round(dt, 1), img_per_s=round(len(rows) / dt, 1), max_gpu_gb=round(mem, 2))
    print(json.dumps(log), flush=True)
    with open(K.OUT / "feat/feat_log.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("check", "run"))
    ap.add_argument("--list")
    ap.add_argument("--name")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    check() if a.cmd == "check" else run(a)

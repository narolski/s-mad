"""Diffusion-autoencoder generation on Athena (DG1): the A43 MorDIFF-controls generator, unchanged in every part that
touches an image, driven by a job list.

Generator (as mambamorph-code-a44/smadcvpr/a43_gen.py sha fc862ec6... and src/AD1b/ad1b_gen.py): the pinned DiffAE
repository (commit 00c57d3f...), the FFHQ256 autoencoder checkpoint (sha 9bd2ba9e..., torch.load(weights_only=True),
the Lightning callback state mapped to an inert placeholder, only state_dict used, ema_model in eval mode),
LitModel.encode (z_sem), LitModel.encode_stochastic(T=250) (x_T), LitModel.render(T=steps), the A43 interp() verbatim
with alpha as a parameter (z lerp, x_T slerp; 0.5 unless a dose job sets it), the official fp16 autocast, batches of
16, torchvision.utils.save_image to 256-px PNG, inputs read with DiffAE's ImageDataset (do_augment=False).
New operations, both from AD1b: a lossless left-right flip of a loaded input tensor (a source named '<stem>__flip'),
and the identical-input case as its limit: a job with an empty src_b renders render(x_T(src_a), z(src_a)) (the A43
reconstruction path; the A43 slerp is 0/0 for identical inputs). A job with steps 0 (rung G) writes the loaded input
tensor back through the same save_image call (genuine photo, same storage); it is checked pixel-identical to its input.
Seeds: LitModel seeds with conf.seed = 0; DDIM eta = 0 in both directions, so no random number affects a pixel.

Job list CSV columns: set,pool,rung,name,src_a,src_b,alpha,steps,host,partner. Output: <out-root>/<pool>/<name>,
<out-root>/gen_rows.csv, <out-root>/gen_log.json. The output folder must not exist (nothing is replaced).

usage: python -I dg1_gen.py --repo R --ckpt C --inputs DIR --jobs CSV --out-root DIR [--bs 16] [--repo-manifest F]
"""
import argparse
import csv
import hashlib
import json
import pathlib
import platform
import shutil
import subprocess
import sys
import time

T_ENC = 250
CKPT_SHA = "9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca"
REPO_COMMIT = "00c57d3f626f28bf9ed8aff58d90baab25de3af4"
STEPS_OK = {0, 20, 100}
FLIP = "__flip"
COLS = ["set", "pool", "rung", "name", "src_a", "src_b", "alpha", "steps", "host", "partner"]


class _InertCallbackState:
    """Placeholder for pytorch_lightning.callbacks.model_checkpoint.ModelCheckpoint in the checkpoint's 'callbacks'
    entry (never used)."""

    def __init__(self, *a, **k):
        self._a, self._k = a, k


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def check_repo(repo, manifest):
    """The pinned clean DiffAE commit: git when available; always the per-file sha256 manifest if one is given."""
    info = {}
    if shutil.which("git"):
        gr = lambda *c: subprocess.run(["git", "-C", repo, *c], capture_output=True, text=True).stdout  # noqa: E731
        head, dirty = gr("rev-parse", "HEAD").strip(), gr("status", "--porcelain").strip()
        info["git_head"], info["git_dirty"] = head, bool(dirty)
        if head != REPO_COMMIT or dirty:
            sys.exit(f"DiffAE repo is not the clean pinned commit (HEAD {head!r}, dirty {bool(dirty)})")
    if manifest:
        bad = 0
        n = 0
        for ln in open(manifest):
            h, rel = ln.rstrip("\n").split("  ", 1)
            n += 1
            if fsha(pathlib.Path(repo) / rel) != h:
                bad += 1
        info["manifest_files"], info["manifest_bad"] = n, bad
        if bad:
            sys.exit(f"DiffAE repo: {bad} of {n} files differ from the manifest")
    if not info:
        sys.exit("no way to verify the DiffAE repo (no git, no manifest)")
    return info


def main():
    ap = argparse.ArgumentParser()
    for k in ("repo", "ckpt", "inputs", "jobs", "out-root"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--repo-manifest", default="")
    ap.add_argument("--bs", type=int, default=16)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run as python -I (third-party code and checkpoint)")
    out = pathlib.Path(a.out_root)
    if out.exists():
        sys.exit(f"{out} exists (a new output folder; nothing is replaced)")
    t_all = time.time()
    jobs = list(csv.DictReader(open(a.jobs)))
    if not jobs or list(jobs[0].keys()) != COLS:
        sys.exit(f"job list columns {list(jobs[0].keys()) if jobs else None} != {COLS}")
    keys = [(j["pool"], j["name"]) for j in jobs]
    if len(set(keys)) != len(keys):
        sys.exit("two jobs share an output name")
    for j in jobs:
        if int(j["steps"]) not in STEPS_OK:
            sys.exit(f"job {j['pool']}/{j['name']}: steps {j['steps']}")
        if int(j["steps"]) == 0 and (j["src_b"] or j["src_a"].endswith(FLIP)):
            sys.exit(f"job {j['pool']}/{j['name']}: a genuine-photo job has one unflipped source")
    got = fsha(a.ckpt)
    if got != CKPT_SHA:
        sys.exit(f"checkpoint sha256 {got} != {CKPT_SHA}")
    repo_info = check_repo(a.repo, a.repo_manifest)
    sys.path.insert(0, a.repo)
    import numpy as np
    import torch
    import torch.nn.functional as F
    import torchvision
    import PIL
    from PIL import Image
    from torchvision.utils import save_image
    from templates import ffhq256_autoenc, LitModel  # noqa: E402  (pinned DiffAE repository)
    from dataset import ImageDataset  # noqa: E402

    device = "cuda:0"
    conf = ffhq256_autoenc()
    model = LitModel(conf)
    torch.serialization.add_safe_globals(
        [(_InertCallbackState, "pytorch_lightning.callbacks.model_checkpoint.ModelCheckpoint")])
    state = torch.load(a.ckpt, map_location="cpu", weights_only=True)
    res = model.load_state_dict(state["state_dict"], strict=False)
    n_sd = len(state["state_dict"])
    del state
    if [k for k in res.missing_keys if k.startswith("ema_model.")]:
        sys.exit("ema_model keys missing")
    model.ema_model.eval()
    model.ema_model.to(device)

    data = ImageDataset(a.inputs, image_size=conf.img_size, exts=["png"], do_augment=False, sort_names=True,
                        has_subdir=False)
    idx = {pathlib.Path(str(p)).stem: i for i, p in enumerate(data.paths)}

    def base(s):
        return s[:-len(FLIP)] if s.endswith(FLIP) else s

    srcs = sorted({s for j in jobs for s in (j["src_a"], j["src_b"]) if s})
    missing = sorted({base(s) for s in srcs if base(s) not in idx})
    if missing:
        sys.exit(f"inputs missing: {missing[:10]} ({len(missing)})")

    def load(s):
        t = data[idx[base(s)]]["img"]
        return torch.flip(t, dims=[-1]) if s.endswith(FLIP) else t

    def sync():
        torch.cuda.synchronize()

    log = {"generator": "A43 path (a43_gen.py fc862ec6...) via dg1_gen.py", "T_enc": T_ENC, "bs": a.bs,
           "fp16_autocast": conf.fp16, "seed": conf.seed, "ckpt_sha256": got, "state_dict_keys": n_sd,
           "load_missing": len(res.missing_keys), "load_unexpected": len(res.unexpected_keys), "repo": repo_info,
           "torch": torch.__version__, "cuda": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
           "torchvision": torchvision.__version__, "numpy": np.__version__, "pillow": PIL.__version__,
           "python": platform.python_version(), "machine": platform.machine(), "node": platform.node(),
           "device": torch.cuda.get_device_name(0), "jobs_file": a.jobs, "jobs_sha256": fsha(a.jobs),
           "script_sha256": fsha(__file__), "n_jobs": len(jobs)}
    try:
        import pytorch_lightning
        log["pytorch_lightning"] = pytorch_lightning.__version__
    except Exception as e:  # noqa: BLE001
        log["pytorch_lightning"] = repr(e)

    # ---- codes: one encoding per source in this run (z_sem and x_T, the A43 calls), shared by every job
    need = sorted({s for j in jobs if int(j["steps"]) > 0 for s in (j["src_a"], j["src_b"]) if s})
    cond, xT = {}, {}
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(need), a.bs):
            names = need[i:i + a.bs]
            batch = torch.stack([load(s) for s in names]).to(device)
            c = model.encode(batch)
            x = model.encode_stochastic(batch, c, T=T_ENC)
            for k, s in enumerate(names):
                cond[s], xT[s] = c[k].float().cpu(), x[k].float().cpu()
            print(f"encode {i + len(names)}/{len(need)} {time.time() - t0:.0f}s", flush=True)
        sync()
    log["n_encode"] = len(need)
    log["encode_s"] = time.time() - t0
    log["encode_s_per_image"] = log["encode_s"] / max(1, len(need))
    log["codes_finite"] = bool(all(torch.isfinite(v).all() for v in xT.values()) and
                               all(torch.isfinite(v).all() for v in cond.values()))
    if not log["codes_finite"]:
        sys.exit("non-finite codes")

    def cosv(u, v):
        u = F.normalize(u.view(-1), dim=0)
        v = F.normalize(v.view(-1), dim=0)
        return (u * v).sum()

    def interp(sa, sb, ALPHA):   # the A43 interp(), verbatim but for ALPHA as an argument
        c0, c1, x0, x1 = cond[sa], cond[sb], xT[sa], xT[sb]
        alpha = torch.tensor([ALPHA], dtype=torch.float32)
        intp = c0[None] * (1 - alpha[:, None]) + c1[None] * alpha[:, None]
        theta = torch.arccos(cosv(x0, x1))
        x_shape = x0.shape
        intp_x = (torch.sin((1 - alpha[:, None]) * theta) * x0.flatten(0, 2)[None] +
                  torch.sin(alpha[:, None] * theta) * x1.flatten(0, 2)[None]) / torch.sin(theta)
        return intp[0], intp_x.view(-1, *x_shape)[0], float(theta)

    rows, per = [], {}
    pools = list(dict.fromkeys(j["pool"] for j in jobs))
    with torch.no_grad():
        for pool in pools:
            pj = [j for j in jobs if j["pool"] == pool]
            steps = {int(j["steps"]) for j in pj}
            if len(steps) != 1:
                sys.exit(f"pool {pool} mixes step counts {steps}")
            steps = steps.pop()
            (out / pool).mkdir(parents=True, exist_ok=False)
            per[pool] = [0, 0.0, steps]
            for i in range(0, len(pj), a.bs):
                chunk = pj[i:i + a.bs]
                t1 = time.time()
                if steps == 0:
                    pred = [(load(j["src_a"]) + 1) / 2 for j in chunk]
                    th = [""] * len(chunk)
                else:
                    cs, xs, th = [], [], []
                    for j in chunk:
                        if not j["src_b"]:
                            cs.append(cond[j["src_a"]]); xs.append(xT[j["src_a"]]); th.append("")
                        else:
                            c_, x_, t_ = interp(j["src_a"], j["src_b"], float(j["alpha"]))
                            cs.append(c_); xs.append(x_); th.append(round(t_, 6))
                    pred = model.render(torch.stack(xs).to(device), torch.stack(cs).to(device), T=steps)
                    sync()
                per[pool][0] += len(chunk)
                per[pool][1] += time.time() - t1
                for k, j in enumerate(chunk):
                    p = pred[k]
                    fin = bool(torch.isfinite(p).all())
                    std = float(p.float().std())
                    f = out / pool / j["name"]
                    if f.exists():
                        sys.exit(f"refusing to overwrite {f}")
                    save_image(p, str(f))
                    lossless = ""
                    if steps == 0:
                        src = pathlib.Path(a.inputs) / data.paths[idx[j["src_a"]]]
                        lossless = int(np.array_equal(np.asarray(Image.open(f).convert("RGB")),
                                                      np.asarray(Image.open(src).convert("RGB"))))
                    rows.append({**{c: j[c] for c in COLS}, "theta_xT": th[k], "finite": int(fin),
                                 "std01": round(std, 5), "lossless_vs_input": lossless, "seed": conf.seed,
                                 "sha256": fsha(f)})
            print(f"pool {pool}: {per[pool][0]} images, {per[pool][1]:.0f}s", flush=True)
    log["decode"] = {p: {"images": v[0], "seconds": v[1], "steps": v[2], "s_per_image": v[1] / max(1, v[0])}
                     for p, v in per.items()}
    log["all_finite"] = all(r["finite"] for r in rows)
    log["min_std01"] = min(r["std01"] for r in rows)
    log["genuine_lossless"] = [sum(r["lossless_vs_input"] == 1 for r in rows if r["steps"] == "0"),
                               sum(r["steps"] == "0" for r in rows)]
    log["elapsed_s"] = time.time() - t_all
    with open(out / "gen_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json.dump(log, open(out / "gen_log.json", "w"), indent=1)
    print(json.dumps(log, indent=1))
    if not log["all_finite"] or log["genuine_lossless"][0] != log["genuine_lossless"][1]:
        sys.exit("non-finite image or a genuine-photo write that is not lossless")


if __name__ == "__main__":
    main()
